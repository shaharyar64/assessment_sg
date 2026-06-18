"""Generate a single email from intent, key facts, and tone."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.generator import generate_email
from src.llm_client import LLMClient
from src.prompt_builder import STRATEGY_BASIC, STRATEGY_STRUCTURED
from src.validation import ValidationError, validate_scenario


def parse_facts(raw_facts: list[str]) -> list[str]:
    """Accept repeated --fact flags or comma-separated values."""
    facts: list[str] = []
    for item in raw_facts:
        for part in item.split(","):
            cleaned = part.strip()
            if cleaned:
                facts.append(cleaned)
    return facts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate one email from intent, key facts, and tone.",
    )
    parser.add_argument("--intent", required=True, help="Purpose of the email")
    parser.add_argument(
        "--fact",
        action="append",
        dest="facts",
        default=[],
        metavar="TEXT",
        help="One key fact (repeat flag or use comma-separated values)",
    )
    parser.add_argument(
        "--tone",
        required=True,
        help="Writing style: Formal, Casual, Urgent, Empathetic, Professional",
    )
    parser.add_argument(
        "--strategy",
        choices=[STRATEGY_BASIC, STRATEGY_STRUCTURED],
        default=STRATEGY_STRUCTURED,
        help="Prompting strategy (default: structured)",
    )
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no API call)")
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model name (default: gpt-4o-mini; use gpt-4o for highest quality)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to save the result JSON (e.g. outputs/my_email.json)",
    )
    args = parser.parse_args()

    key_facts = parse_facts(args.facts)
    scenario = {
        "id": "CUSTOM",
        "intent": args.intent,
        "key_facts": key_facts,
        "tone": args.tone,
    }

    error = validate_scenario(scenario)
    if error:
        print(f"Validation error: {error.message}", file=sys.stderr)
        return 1

    client = LLMClient(model=args.model, mock=args.mock)
    mode = "mock" if client.mock else f"OpenAI ({args.model})"
    print(f"Generating email using {mode} / strategy: {args.strategy}\n", file=sys.stderr)

    try:
        result = generate_email(scenario, strategy=args.strategy, client=client)
    except ValidationError as exc:
        print(f"Validation error: {exc.message}", file=sys.stderr)
        return 1

    print(result["email"])

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
