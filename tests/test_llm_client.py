"""Tests for LLM client mock mode (TC-16, TC-28)."""

from __future__ import annotations

from src.llm_client import LLMClient, mock_generate


def test_client_mock_mode_when_forced():
    client = LLMClient(mock=True)
    assert client.mock is True


def test_mock_generate_urgent_closing():
    scenario = {"intent": "Reminder", "tone": "Urgent", "key_facts": ["Deadline is tomorrow"]}
    email = mock_generate("## Task", scenario)
    assert "earliest convenience" in email.lower() or "Best regards" in email


def test_mock_generate_casual_closing():
    scenario = {"intent": "Thanks", "tone": "Casual", "key_facts": ["Helped last week"]}
    email = mock_generate("", scenario)
    assert email.startswith("Subject:")
    assert "Thanks," in email


def test_mock_generate_includes_all_facts_structured():
    scenario = {
        "intent": "Follow up",
        "tone": "Formal",
        "key_facts": ["Alpha fact", "Beta fact", "Gamma fact"],
    }
    prompt = "## Task\n## Output Requirements"
    email = mock_generate(prompt, scenario)
    assert "Alpha fact" in email
    assert "Beta fact" in email
    assert "Gamma fact" in email
