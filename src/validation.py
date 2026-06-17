"""Input validation for email generation scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationError(Exception):
    message: str
    missing_fields: list[str] = field(default_factory=list)


def validate_scenario(scenario: dict[str, Any]) -> ValidationError | None:
    """Validate a single scenario. Returns None if valid, else ValidationError."""
    missing: list[str] = []

    intent = scenario.get("intent")
    if not intent or not str(intent).strip():
        missing.append("intent")

    tone = scenario.get("tone")
    if tone is None or not str(tone).strip():
        missing.append("tone")

    key_facts = scenario.get("key_facts")
    if not key_facts or not isinstance(key_facts, list) or len(key_facts) == 0:
        return ValidationError(
            message="At least one key fact is required to generate an accurate email.",
            missing_fields=["key_facts"] if not missing else missing + ["key_facts"],
        )

    if missing:
        field_names = ", ".join(missing)
        return ValidationError(
            message=f"The email scenario is missing a required field: {field_names}.",
            missing_fields=missing,
        )

    return None


def validate_scenarios_file(scenarios: list[dict[str, Any]]) -> list[str]:
    """Validate the full scenarios dataset. Returns list of error messages."""
    errors: list[str] = []

    if len(scenarios) != 10:
        errors.append(f"Expected exactly 10 scenarios, found {len(scenarios)}.")

    ids = [s.get("id") for s in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("Scenario IDs must be unique.")

    required_fields = ("intent", "key_facts", "tone", "reference_email")
    for scenario in scenarios:
        sid = scenario.get("id", "unknown")
        for field_name in required_fields:
            value = scenario.get(field_name)
            if field_name == "key_facts":
                if not value or not isinstance(value, list) or len(value) == 0:
                    errors.append(f"{sid}: key_facts must be a non-empty list.")
            elif not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"{sid}: missing required field '{field_name}'.")

    return errors
