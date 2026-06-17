"""Tests for LangChain prompt templates (TC-05, TC-27)."""

from __future__ import annotations

import pytest

from src.prompt_builder import (
    STRATEGY_BASIC,
    STRATEGY_STRUCTURED,
    build_prompt,
    build_prompt_inputs,
    format_key_facts,
)


def test_format_key_facts_bulleted(valid_scenario):
    assert format_key_facts(valid_scenario).startswith("- The demo was held on Monday")


def test_structured_prompt_has_no_hallucination_rules(valid_scenario):
    prompt = build_prompt(valid_scenario, STRATEGY_STRUCTURED)
    assert "Do not invent" in prompt
    assert "## Rules" in prompt


def test_basic_prompt_has_no_structured_sections(valid_scenario):
    prompt = build_prompt(valid_scenario, STRATEGY_BASIC)
    assert "## Task" not in prompt
    assert "Write a professional email" in prompt


def test_build_prompt_inputs_keys(valid_scenario):
    assert set(build_prompt_inputs(valid_scenario).keys()) == {"intent", "key_facts", "tone"}


def test_unknown_strategy_raises(valid_scenario):
    with pytest.raises(ValueError, match="Unknown strategy"):
        build_prompt(valid_scenario, "invalid")
