"""Trace logging for project observability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def log_trace(
    trace_id: str,
    trace_name: str,
    category: str,
    input_data: Any,
    output_data: Any,
    passed: bool,
    notes: str = "",
    traces_dir: str | Path = "traces",
) -> Path:
    """Write a trace JSON file and return its path."""
    traces_dir = Path(traces_dir) / category
    traces_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "trace_id": trace_id,
        "trace_name": trace_name,
        "category": category,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": input_data,
        "output": output_data,
        "passed": passed,
        "notes": notes,
    }

    path = traces_dir / f"{trace_id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

    return path
