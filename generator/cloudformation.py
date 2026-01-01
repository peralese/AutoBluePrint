from jinja2 import Environment, FileSystemLoader
import os

# Basic instance catalog for quick heuristic matching
INSTANCE_CATALOG = [
    {"name": "t3.micro", "vcpus": 2, "memory_gib": 1},
    {"name": "t3.small", "vcpus": 2, "memory_gib": 2},
    {"name": "t3.medium", "vcpus": 2, "memory_gib": 4},
    {"name": "t3.large", "vcpus": 2, "memory_gib": 8},
    {"name": "t3.xlarge", "vcpus": 4, "memory_gib": 16},
    {"name": "m5.large", "vcpus": 2, "memory_gib": 8},
    {"name": "m5.xlarge", "vcpus": 4, "memory_gib": 16},
    {"name": "m5.2xlarge", "vcpus": 8, "memory_gib": 32},
    {"name": "m5.4xlarge", "vcpus": 16, "memory_gib": 64},
]

DEFAULT_AMI_SSM = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"


def _normalize_specs(specs):
    if not specs:
        return {}
    normalized = {}
    for key, value in specs.items():
        if isinstance(value, dict) and "value" in value:
            normalized[key] = value.get("value")
        else:
            normalized[key] = value
    return normalized


def _memory_bytes_to_gib(memory_bytes):
    if not memory_bytes:
        return None
    return max(1, round(int(memory_bytes) / (1024 ** 3)))


def recommend_instance_type(specs):
    """
    Choose an instance type that meets or exceeds detected cores/memory,
    picking the smallest match from a simple catalog.
    """
    specs = _normalize_specs(specs)
    if not specs:
        return None
    target_vcpus = specs.get("cpu_logical_cores") or specs.get("cpu_physical_cores")
    mem_gib = _memory_bytes_to_gib(specs.get("memory_bytes"))
    if not target_vcpus and not mem_gib:
        return None

    candidates = []
    for inst in INSTANCE_CATALOG:
        if target_vcpus and inst["vcpus"] < target_vcpus:
            continue
        if mem_gib and inst["memory_gib"] < mem_gib:
            continue
        candidates.append(inst)
    if not candidates:
        return None
    # Pick the one with the smallest resources that still meets requirements
    candidates.sort(key=lambda i: (i["vcpus"], i["memory_gib"]))
    return candidates[0]["name"]


def recommend_ami_parameter(specs):
    """
    Pick an SSM parameter path for AMI based on detected OS.
    """
    specs = _normalize_specs(specs)
    if not specs:
        return DEFAULT_AMI_SSM

    os_name = (specs.get("os_name") or "").lower()
    platform = (specs.get("platform") or "").lower()

    if "windows" in os_name or platform == "windows":
        return "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
    if "ubuntu 22" in os_name or "ubuntu 22" in platform:
        return "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
    if "ubuntu 20" in os_name or "ubuntu 20" in platform:
        return "/aws/service/canonical/ubuntu/server/20.04/stable/current/amd64/hvm/ebs-gp2/ami-id"

    return DEFAULT_AMI_SSM


def recommend_volume_size(specs):
    """
    Heuristic: default larger root volume for Windows hosts.
    """
    specs = _normalize_specs(specs)
    if not specs:
        return 20
    os_name = (specs.get("os_name") or "").lower()
    platform = (specs.get("platform") or "").lower()
    if "windows" in os_name or platform == "windows":
        return 60
    return 20


def _prepare_components(components):
    normalized = []
    for component in components or []:
        item = dict(component)
        name = item.get("name") or item.get("component_id") or "Component"
        item["name"] = name
        # Normalize resource names for template usage
        item["resource_name"] = name.replace(" ", "").replace("-", "").replace("_", "")
        normalized.append(item)
    return normalized


def generate_cloudformation_template(components, specs=None):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("cloudformation_template.j2")

    components = _prepare_components(components)
    recommended_instance = recommend_instance_type(specs) if specs else None
    recommended_ami_param = recommend_ami_parameter(specs)
    recommended_volume_size = recommend_volume_size(specs)

    return template.render(
        components=components,
        specs=specs or {},
        instance_type_default=recommended_instance,
        ami_param_default=recommended_ami_param,
        volume_size_default=recommended_volume_size,
    )


def generate_cloudformation_from_workload(workload):
    specs = (workload or {}).get("host_spec") or {}
    components = (workload or {}).get("software_components") or []
    sizing = (workload or {}).get("sizing") or {}
    iac_intent = (workload or {}).get("iac_intent") or {}
    min_confidence = iac_intent.get("min_component_confidence", 0.0)
    components = [
        c
        for c in components
        if (c.get("eligible_for_iac", True) and (c.get("confidence") or 0) >= min_confidence)
    ]

    instance_type_default = sizing.get("recommended_instance_type") or recommend_instance_type(specs)
    ami_param_default = recommend_ami_parameter(specs)
    volume_size_default = recommend_volume_size(specs)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("cloudformation_template.j2")

    return template.render(
        components=_prepare_components(components),
        specs=specs,
        instance_type_default=instance_type_default,
        ami_param_default=ami_param_default,
        volume_size_default=volume_size_default,
    )
