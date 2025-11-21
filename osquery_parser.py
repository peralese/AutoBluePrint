import json
from json import JSONDecodeError
from typing import Any, Dict, List, Optional

# Expected order for concatenated queries in discovery.sql
QUERY_ORDER = [
    "os_version",
    "cpu_info",
    "memory_info",
    "interface_details",
    "processes",
    "programs",
]


def _parse_concatenated_arrays(text: str) -> List[Any]:
    """
    Parse a string containing multiple top-level JSON arrays placed back-to-back.
    Returns a list of decoded JSON values in the order encountered.
    """
    decoder = json.JSONDecoder()
    idx = 0
    values = []
    length = len(text)

    while idx < length:
        # Skip whitespace between arrays
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break
        try:
            val, end = decoder.raw_decode(text, idx)
        except JSONDecodeError as exc:
            raise ValueError(f"Failed to decode OSQuery dump near position {idx}: {exc}") from exc
        values.append(val)
        idx = end
    return values


def parse_osquery_dump(path: str) -> Dict[str, Any]:
    """
    Parse an OSQuery export produced by discovery.sql into a structured dict.

    The export is expected to be multiple JSON arrays concatenated in the order of QUERY_ORDER.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = _parse_concatenated_arrays(text)
    parsed: Dict[str, Any] = {}
    for i, name in enumerate(QUERY_ORDER):
        parsed[name] = blocks[i] if i < len(blocks) else []
    parsed["raw_blocks"] = blocks
    return parsed


def extract_specs(parsed: Dict[str, Any]) -> Dict[str, Optional[Any]]:
    """
    Extract basic server specs (OS, CPU, memory) from parsed OSQuery tables.
    """
    os_rows = parsed.get("os_version") or []
    cpu_rows = parsed.get("cpu_info") or []
    memory_rows = parsed.get("memory_info") or []

    os_row = os_rows[0] if os_rows else {}
    cpu_row = cpu_rows[0] if cpu_rows else {}
    mem_row = memory_rows[0] if memory_rows else {}

    def _get_int(row: Dict[str, Any], key: str) -> Optional[int]:
        val = row.get(key)
        try:
            return int(val) if val not in (None, "") else None
        except (TypeError, ValueError):
            return None

    specs = {
        "os_name": os_row.get("name"),
        "os_version": os_row.get("version") or os_row.get("build"),
        "platform": os_row.get("platform"),
        "cpu_model": cpu_row.get("cpu_brand") or cpu_row.get("model"),
        "cpu_physical_cores": _get_int(cpu_row, "cpu_physical_cores") or _get_int(cpu_row, "number_of_cores"),
        "cpu_logical_cores": _get_int(cpu_row, "cpu_logical_cores") or _get_int(cpu_row, "logical_processors"),
        "memory_bytes": _get_int(cpu_row, "physical_memory") or _get_int(mem_row, "total_bytes"),
    }
    return specs
