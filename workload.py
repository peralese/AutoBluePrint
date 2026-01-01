import hashlib
import os
from datetime import datetime, timezone

DEFAULT_MIN_COMPONENT_CONFIDENCE = 0.6


def _file_sha256(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _normalize_name(component):
    for key in ("name", "program", "display_name", "product"):
        value = component.get(key)
        if value:
            return value
    return "unknown"


def _index_raw_programs(raw_programs):
    index = {}
    for program in raw_programs or []:
        name = _normalize_name(program).strip().lower()
        if not name:
            continue
        index.setdefault(name, []).append(program)
    return index


def _build_component(component, raw_index, llm_model):
    name = _normalize_name(component)
    version = component.get("version") or component.get("product_version")
    comp_type = component.get("type") or component.get("category")
    raw_matches = raw_index.get(name.strip().lower(), [])

    evidence = []
    for idx, record in enumerate(raw_matches[:3]):
        evidence.append(
            {
                "type": "osquery_record",
                "source": "programs",
                "index": idx,
                "record": record,
            }
        )
    evidence.append(
        {
            "type": "llm_classification",
            "source": llm_model or "unknown",
        }
    )

    confidence = 0.4
    if raw_matches:
        confidence += 0.4
    if version:
        confidence += 0.1
    if comp_type:
        confidence += 0.05
    confidence = min(confidence, 0.95)

    component_id = hashlib.sha1(
        f"{name}:{version}:{comp_type}".encode("utf-8")
    ).hexdigest()[:12]

    return {
        "component_id": f"cmp_{component_id}",
        "type": comp_type,
        "name": name,
        "version": version,
        "confidence": confidence,
        "eligible_for_iac": confidence >= DEFAULT_MIN_COMPONENT_CONFIDENCE,
        "evidence": evidence,
    }

def _osquery_evidence(parsed, table, index=0):
    if not parsed:
        return []
    rows = parsed.get(table) or []
    if not rows or index >= len(rows):
        return []
    return [
        {
            "type": "osquery_record",
            "source": table,
            "index": index,
            "record": rows[index],
        }
    ]


def _field_with_evidence(value, evidence):
    if value is None:
        confidence = 0.0
    elif evidence:
        confidence = 0.9
    else:
        confidence = 0.5
    return {
        "value": value,
        "confidence": confidence,
        "evidence": evidence,
    }


def _build_host_spec(specs, parsed):
    specs = specs or {}
    os_evidence = _osquery_evidence(parsed, "os_version")
    cpu_evidence = _osquery_evidence(parsed, "cpu_info")
    memory_evidence = _osquery_evidence(parsed, "memory_info")

    return {
        "hostname": _field_with_evidence(specs.get("hostname"), []),
        "os_name": _field_with_evidence(specs.get("os_name"), os_evidence),
        "os_version": _field_with_evidence(specs.get("os_version"), os_evidence),
        "platform": _field_with_evidence(specs.get("platform"), os_evidence),
        "cpu_model": _field_with_evidence(specs.get("cpu_model"), cpu_evidence),
        "cpu_physical_cores": _field_with_evidence(specs.get("cpu_physical_cores"), cpu_evidence),
        "cpu_logical_cores": _field_with_evidence(specs.get("cpu_logical_cores"), cpu_evidence),
        "memory_bytes": _field_with_evidence(specs.get("memory_bytes"), memory_evidence),
    }


def build_workload(
    raw_programs,
    classified_components,
    specs,
    input_path,
    llm_provider="openai",
    llm_model=None,
    schema_version="0",
    parsed=None,
):
    workload_id = os.path.splitext(os.path.basename(input_path))[0] or "workload"
    generated_at = datetime.now(timezone.utc).isoformat()

    raw_index = _index_raw_programs(raw_programs)
    components = [
        _build_component(component, raw_index, llm_model)
        for component in (classified_components or [])
    ]

    return {
        "schema_version": schema_version,
        "metadata": {
            "workload_id": workload_id,
            "generated_at": generated_at,
            "input_files": [
                {
                    "path": input_path,
                    "sha256": _file_sha256(input_path),
                }
            ],
            "llm": {
                "provider": llm_provider,
                "model": llm_model,
                "prompt_hash": None,
            },
        },
        "host_spec": _build_host_spec(specs, parsed),
        "software_components": components,
        "sizing": {
            "recommended_instance_type": None,
            "basis": "host_specs" if specs else "unknown",
            "confidence": 0.0,
        },
        "iac_intent": {
            "target_platform": "aws",
            "generator": "cloudformation",
            "migration_strategy": "rehost",
            "allowed_resource_types": [],
            "blocked_resource_types": [],
            "min_component_confidence": DEFAULT_MIN_COMPONENT_CONFIDENCE,
        },
        "open_questions": [],
    }
