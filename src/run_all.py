"""End-to-end pipeline: generate, evaluate, compare, report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import compare_strategies
from src.evaluation_export import export_evaluation_csv
from src.evaluator import METRIC_DEFINITIONS, evaluate_email
from src.generator import generate_batch, load_scenarios, save_generated_emails
from src.llm_client import LLMClient
from src.prompt_builder import STRATEGY_BASIC, STRATEGY_STRUCTURED
from src.report import generate_report_docx
from src.trace_logger import log_trace
from src.validation import ValidationError, validate_scenario


def run_evaluation(generated: list[dict]) -> dict:
    """Score all generated emails and compute strategy averages."""
    scenario_scores = []

    for item in generated:
        result = evaluate_email(
            email_text=item["email"],
            key_facts=item["key_facts"],
            tone=item["tone"],
        )
        scenario_scores.append({
            "scenario_id": item["scenario_id"],
            "strategy": item["strategy"],
            "scores": result["scores"],
            "overall_average": result["overall_average"],
            "details": result["details"],
        })

    strategy_averages = {}
    strategies = sorted(set(s["strategy"] for s in scenario_scores))
    for strategy in strategies:
        rows = [r for r in scenario_scores if r["strategy"] == strategy]
        metric_keys = ["fact_recall", "tone_and_format_accuracy", "conciseness_and_fluency"]
        metric_avgs = {}
        for key in metric_keys:
            metric_avgs[key] = round(
                sum(r["scores"][key] for r in rows) / len(rows), 4
            )
        overall = round(
            sum(r["overall_average"] for r in rows) / len(rows), 4
        )
        strategy_averages[strategy] = {
            "metric_averages": metric_avgs,
            "overall_average": overall,
            "scenario_count": len(rows),
        }

    return {
        "metric_definitions": METRIC_DEFINITIONS,
        "scenario_scores": scenario_scores,
        "strategy_averages": strategy_averages,
    }


def run_validation_traces() -> bool:
    """Run TRACE 02 and TRACE 03 validation checks."""
    all_passed = True

    missing_tone = {
        "intent": "Apologize for a delayed response",
        "key_facts": [
            "The response was delayed due to internal review",
            "The requested document is now attached",
        ],
    }
    err = validate_scenario(missing_tone)
    passed = err is not None and "tone" in err.missing_fields
    log_trace(
        "trace_missing_tone_001",
        "TRACE 02 — Missing Required Field",
        "validation",
        missing_tone,
        {"status": "error", "message": err.message if err else None, "missing": err.missing_fields if err else []},
        passed,
    )
    all_passed &= passed

    empty_facts = {
        "intent": "Confirm next steps after a call",
        "key_facts": [],
        "tone": "Professional",
    }
    err2 = validate_scenario(empty_facts)
    passed2 = err2 is not None and "key fact" in err2.message.lower()
    log_trace(
        "trace_empty_facts_001",
        "TRACE 03 — Empty Key Facts Rejected",
        "validation",
        empty_facts,
        {"status": "error", "message": err2.message if err2 else None},
        passed2,
    )
    all_passed &= passed2

    return all_passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Email Generation Assistant — full pipeline")
    parser.add_argument("--scenarios", default="data/scenarios.json", help="Path to scenarios JSON")
    parser.add_argument("--mock", action="store_true", help="Use mock LLM (no API key needed)")
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model name (default: gpt-4o-mini; use gpt-4o for highest quality)",
    )
    parser.add_argument("--skip-report", action="store_true", help="Skip PDF report generation")
    args = parser.parse_args()

    scenarios_path = ROOT / args.scenarios
    outputs_dir = ROOT / "outputs"
    reports_dir = ROOT / "reports"
    traces_dir = ROOT / "traces"

    outputs_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Email Generation Assistant — Full Pipeline")
    print("=" * 60)

    print("\n[1/6] Running validation traces (TRACE 02, 03)...")
    run_validation_traces()

    print(f"\n[2/6] Loading scenarios from {scenarios_path}...")
    scenarios = load_scenarios(scenarios_path)
    print(f"  Loaded {len(scenarios)} validated scenarios.")

    log_trace(
        "trace_scenarios_load_001",
        "TRACE 06 — Ten Evaluation Scenarios",
        "batch",
        {"path": str(scenarios_path)},
        {"count": len(scenarios), "ids": [s["id"] for s in scenarios]},
        len(scenarios) == 10,
    )

    client = LLMClient(model=args.model, mock=args.mock)
    mode = "mock" if client.mock else f"LangChain + OpenAI ({args.model})"
    print(f"\n[3/6] Generating emails (Strategy A + B) using {mode}...")

    generated = generate_batch(
        scenarios,
        strategies=[STRATEGY_BASIC, STRATEGY_STRUCTURED],
        client=client,
    )
    emails_path = outputs_dir / "generated_emails.json"
    save_generated_emails(generated, emails_path)
    print(f"  Saved {len(generated)} emails to {emails_path}")

    log_trace(
        "trace_batch_generation_001",
        "TRACE 07 — Strategy A and Strategy B Generation",
        "batch",
        {"scenarios": 10, "strategies": [STRATEGY_BASIC, STRATEGY_STRUCTURED]},
        {"total_emails": len(generated), "output": str(emails_path)},
        len(generated) == 20,
    )

    print("\n[4/6] Evaluating with three custom metrics...")
    evaluation = run_evaluation(generated)
    eval_path = outputs_dir / "evaluation_results.json"
    with eval_path.open("w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)

    for strategy, stats in evaluation["strategy_averages"].items():
        print(f"  {strategy}: overall average = {stats['overall_average']:.2f}")

    print(f"  Saved evaluation to {eval_path}")

    log_trace(
        "trace_full_evaluation_001",
        "TRACE 11 — Evaluation Results File",
        "evaluation",
        {"emails_evaluated": len(generated)},
        {"strategy_averages": evaluation["strategy_averages"]},
        True,
    )

    print("\n[5/6] Comparing strategies...")
    comparison = compare_strategies(evaluation)
    comparison_path = outputs_dir / "comparison_summary.json"
    with comparison_path.open("w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print(f"  Recommended: {comparison['recommended_strategy']}")
    print(f"  Reason: {comparison['reason']}")
    print(f"  Failure mode ({comparison['loser']}): {comparison['biggest_failure_mode']}")

    log_trace(
        "trace_strategy_comparison_001",
        "TRACE 12 — Strategy Comparison and Recommendation",
        "comparison",
        evaluation["strategy_averages"],
        comparison,
        True,
    )

    csv_path = outputs_dir / "evaluation_results.csv"
    export_evaluation_csv(evaluation, csv_path)
    print(f"  Saved evaluation CSV to {csv_path}")

    if not args.skip_report:
        print("\n[6/6] Generating reports...")
        report_docx = reports_dir / "final_report.docx"
        saved_report = generate_report_docx(
            evaluation,
            comparison,
            report_docx,
            sample_scenario=scenarios[0],
            scenarios_path=args.scenarios,
        )
        print(f"  Final report (Word): {saved_report}")
        if saved_report != report_docx:
            print(
                "  Note: Close final_report.docx in Word, then re-run to overwrite it. "
                f"Report saved as {saved_report.name} instead."
            )

        log_trace(
            "trace_final_analysis_generation_001",
            "TRACE 13 — Final Report",
            "report",
            {"evaluation": str(eval_path)},
            {
                "report_docx": str(saved_report),
                "evaluation_csv": str(csv_path),
            },
            saved_report.exists(),
        )
    else:
        print("\n[6/6] Skipped reports (--skip-report).")

    log_trace(
        "trace_end_to_end_project_run_001",
        "End-to-End Pipeline",
        "e2e",
        {"scenarios": 10, "strategies": 2},
        {
            "generated_emails": str(emails_path),
            "evaluation_results": str(eval_path),
            "comparison_summary": str(comparison_path),
            "recommended_strategy": comparison["recommended_strategy"],
        },
        True,
    )

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print(f"  Generated emails:  {emails_path}")
    print(f"  Evaluation:        {eval_path}")
    print(f"  Comparison:        {comparison_path}")
    print(f"  Evaluation CSV:    {outputs_dir / 'evaluation_results.csv'}")
    if not args.skip_report:
        print(f"  Final report (Word): {reports_dir / 'final_report.docx'}")
    print("=" * 60)

    return 0


def demo_single_email() -> None:
    """Demo TRACE 01 — generate one email from valid input."""
    scenario = {
        "id": "DEMO-001",
        "intent": "Follow up after a product demo",
        "key_facts": [
            "The demo was held on Monday",
            "The client asked for pricing details",
            "The proposal should be shared by Friday",
            "The client is interested in the automation dashboard",
        ],
        "tone": "Formal",
    }
    error = validate_scenario(scenario)
    if error:
        print(f"Validation error: {error.message}")
        return

    from src.generator import generate_email

    client = LLMClient(mock=True)
    result = generate_email(scenario, strategy=STRATEGY_STRUCTURED, client=client)
    print(result["email"])


if __name__ == "__main__":
    raise SystemExit(main())
