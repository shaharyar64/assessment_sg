"""Email generation for single scenarios and batch runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.llm_client import LLMClient
from src.prompt_builder import STRATEGY_BASIC, STRATEGY_STRUCTURED, build_prompt
from src.validation import ValidationError, validate_scenario, validate_scenarios_file


def generate_email(
    scenario: dict[str, Any],
    strategy: str = STRATEGY_STRUCTURED,
    client: LLMClient | None = None,
) -> dict[str, Any]:
    """
    Generate one email from a scenario dict.

    Raises ValidationError if input is invalid (no LLM call made).
    """
    error = validate_scenario(scenario)
    if error:
        raise error

    llm = client or LLMClient()
    prompt = build_prompt(scenario, strategy)
    email_text = llm.generate(scenario=scenario, strategy=strategy, prompt=prompt)

    return {
        "scenario_id": scenario.get("id"),
        "strategy": strategy,
        "intent": scenario["intent"],
        "tone": scenario["tone"],
        "key_facts": scenario["key_facts"],
        "prompt": prompt,
        "email": email_text.strip(),
    }


def load_scenarios(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate scenarios from JSON file."""
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    scenarios = data.get("scenarios", data) if isinstance(data, dict) else data
    errors = validate_scenarios_file(scenarios)
    if errors:
        raise ValueError("Scenario validation failed:\n" + "\n".join(errors))

    return scenarios


def generate_batch(
    scenarios: list[dict[str, Any]],
    strategies: list[str] | None = None,
    client: LLMClient | None = None,
) -> list[dict[str, Any]]:
    """Generate emails for all scenarios across all strategies."""
    strategies = strategies or [STRATEGY_BASIC, STRATEGY_STRUCTURED]
    llm = client or LLMClient()
    results: list[dict[str, Any]] = []

    for scenario in scenarios:
        for strategy in strategies:
            result = generate_email(scenario, strategy=strategy, client=llm)
            results.append(result)

    return results


def save_generated_emails(results: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"generated_emails": results}, f, indent=2, ensure_ascii=False)
