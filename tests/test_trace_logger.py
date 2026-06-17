"""Tests for trace logging (TC-30)."""

from __future__ import annotations

import json

from src.trace_logger import log_trace


def test_log_trace_writes_json(tmp_path):
    path = log_trace(
        trace_id="trace_test_001",
        trace_name="Test Trace",
        category="test",
        input_data={"intent": "Test"},
        output_data={"status": "ok"},
        passed=True,
        traces_dir=tmp_path,
    )
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["trace_id"] == "trace_test_001"
    assert payload["passed"] is True
    assert payload["category"] == "test"
    assert "timestamp" in payload
