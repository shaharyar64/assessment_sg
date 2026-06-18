"""CSV export of evaluation results."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def export_evaluation_csv(evaluation_results: dict[str, Any], output_path: str | Path) -> Path:
    """Write per-scenario evaluation scores to CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "scenario_id",
        "strategy",
        "fact_recall",
        "tone_and_format_accuracy",
        "conciseness_and_fluency",
        "overall_average",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in evaluation_results.get("scenario_scores", []):
            scores = row.get("scores", {})
            writer.writerow(
                {
                    "scenario_id": row.get("scenario_id", ""),
                    "strategy": row.get("strategy", ""),
                    "fact_recall": scores.get("fact_recall", ""),
                    "tone_and_format_accuracy": scores.get("tone_and_format_accuracy", ""),
                    "conciseness_and_fluency": scores.get("conciseness_and_fluency", ""),
                    "overall_average": row.get("overall_average", ""),
                }
            )

        writer.writerow({})
        writer.writerow({"scenario_id": "STRATEGY_AVERAGES", "strategy": ""})
        for strategy, stats in evaluation_results.get("strategy_averages", {}).items():
            ma = stats.get("metric_averages", {})
            writer.writerow(
                {
                    "scenario_id": "",
                    "strategy": strategy,
                    "fact_recall": ma.get("fact_recall", ""),
                    "tone_and_format_accuracy": ma.get("tone_and_format_accuracy", ""),
                    "conciseness_and_fluency": ma.get("conciseness_and_fluency", ""),
                    "overall_average": stats.get("overall_average", ""),
                }
            )

    return output_path
