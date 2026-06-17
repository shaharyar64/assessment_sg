"""Tests for input validation (TC-02, TC-03, TC-17, TC-18)."""

from __future__ import annotations

from src.validation import validate_scenario, validate_scenarios_file


def test_valid_scenario_passes(valid_scenario):
    assert validate_scenario(valid_scenario) is None


def test_missing_tone_rejected():
    scenario = {
        "intent": "Apologize for a delayed response",
        "key_facts": ["The document is now ready"],
    }
    error = validate_scenario(scenario)
    assert error is not None
    assert "tone" in error.missing_fields


def test_empty_key_facts_rejected():
    scenario = {
        "intent": "Confirm next steps",
        "key_facts": [],
        "tone": "Professional",
    }
    error = validate_scenario(scenario)
    assert error is not None
    assert "key fact" in error.message.lower()


def test_missing_intent_rejected():
    scenario = {"key_facts": ["Some fact"], "tone": "Formal"}
    error = validate_scenario(scenario)
    assert error is not None
    assert "intent" in error.missing_fields


def test_whitespace_only_tone_rejected(valid_scenario):
    scenario = {**valid_scenario, "tone": "   "}
    error = validate_scenario(scenario)
    assert error is not None
    assert "tone" in error.missing_fields


def test_whitespace_only_intent_rejected(valid_scenario):
    scenario = {**valid_scenario, "intent": "  "}
    error = validate_scenario(scenario)
    assert error is not None
    assert "intent" in error.missing_fields


def test_scenarios_file_requires_exactly_ten():
    scenarios = [
        {"id": f"SCN-{i:03d}", "intent": "x", "key_facts": ["f"], "tone": "Formal", "reference_email": "Subject: x"}
        for i in range(5)
    ]
    errors = validate_scenarios_file(scenarios)
    assert any("10 scenarios" in e for e in errors)


def test_scenarios_file_requires_unique_ids():
    base = {"intent": "x", "key_facts": ["f"], "tone": "Formal", "reference_email": "Subject: x"}
    scenarios = [{**base, "id": "DUPE"} for _ in range(10)]
    errors = validate_scenarios_file(scenarios)
    assert any("unique" in e.lower() for e in errors)


def test_scenarios_file_requires_reference_email():
    scenarios = [
        {"id": f"SCN-{i:03d}", "intent": "x", "key_facts": ["f"], "tone": "Formal", "reference_email": "Subject: x"}
        for i in range(9)
    ]
    scenarios.append({"id": "SCN-009", "intent": "x", "key_facts": ["f"], "tone": "Formal"})
    errors = validate_scenarios_file(scenarios)
    assert any("reference_email" in e for e in errors)
