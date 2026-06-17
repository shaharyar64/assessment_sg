"""Tests for email generation (TC-01, TC-07, TC-22, TC-26)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.generator import generate_batch, generate_email, load_scenarios, save_generated_emails
from src.llm_client import LLMClient
from src.prompt_builder import STRATEGY_BASIC, STRATEGY_STRUCTURED
from src.validation import ValidationError


def test_generate_email_mock_returns_complete_email(valid_scenario):
    client = LLMClient(mock=True)
    result = generate_email(valid_scenario, strategy=STRATEGY_STRUCTURED, client=client)
    assert "Subject:" in result["email"]
    assert "Monday" in result["email"]


def test_generate_email_invalid_input_raises(valid_scenario):
    with pytest.raises(ValidationError):
        generate_email({**valid_scenario, "tone": ""}, client=LLMClient(mock=True))


def test_structured_includes_more_facts_than_basic(valid_scenario):
    valid_scenario["key_facts"] = ["Fact one", "Fact two", "Fact three"]
    client = LLMClient(mock=True)
    basic = generate_email(valid_scenario, strategy=STRATEGY_BASIC, client=client)["email"]
    structured = generate_email(valid_scenario, strategy=STRATEGY_STRUCTURED, client=client)["email"]
    assert basic.count("Fact") <= structured.count("Fact")


def test_generate_batch_produces_scenarios_times_strategies(valid_scenario):
    client = LLMClient(mock=True)
    results = generate_batch([valid_scenario], strategies=[STRATEGY_BASIC, STRATEGY_STRUCTURED], client=client)
    assert len(results) == 2


def test_load_scenarios_from_project_data():
    path = Path(__file__).resolve().parent.parent / "data" / "scenarios.json"
    scenarios = load_scenarios(path)
    assert len(scenarios) == 10


def test_load_invalid_scenario_count_raises(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps({"scenarios": [{"id": "X", "intent": "i", "key_facts": ["f"], "tone": "Formal", "reference_email": "S"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="validation failed"):
        load_scenarios(bad_file)


def test_save_generated_emails_writes_json(tmp_path, valid_scenario):
    client = LLMClient(mock=True)
    results = generate_batch([valid_scenario], client=client)
    out = tmp_path / "out.json"
    save_generated_emails(results, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "generated_emails" in data
    assert len(data["generated_emails"]) == 2


@pytest.mark.parametrize("tone", ["Formal", "Casual", "Urgent", "Empathetic", "Professional"])
def test_all_supported_tones_generate_mock(valid_scenario, tone):
    valid_scenario["tone"] = tone
    result = generate_email(valid_scenario, client=LLMClient(mock=True))
    assert "Subject:" in result["email"]
