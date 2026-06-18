"""Strategy comparison and production recommendation."""

from __future__ import annotations

from typing import Any

from src.prompt_builder import STRATEGY_STRUCTURED

# Prefer structured when scores tie — it enforces tone, facts, and format by design.
_STRATEGY_RANK = {STRATEGY_STRUCTURED: 1, "basic": 0}


def compare_strategies(evaluation_results: dict[str, Any]) -> dict[str, Any]:
    """
    Compare Strategy A vs Strategy B using evaluation metric averages.

    Returns recommendation, failure mode analysis, and winner details.
    """
    strategy_averages = evaluation_results.get("strategy_averages", {})
    if len(strategy_averages) < 2:
        raise ValueError("Need at least two strategies to compare.")

    ranked = sorted(
        strategy_averages.items(),
        key=lambda x: (
            x[1].get("overall_average", 0),
            _STRATEGY_RANK.get(x[0], 0),
        ),
        reverse=True,
    )
    winner_name, winner_stats = ranked[0]
    loser_name, loser_stats = ranked[1]

    metric_names = {
        "fact_recall": "Fact Recall",
        "tone_and_format_accuracy": "Tone and Format Accuracy",
        "conciseness_and_fluency": "Conciseness and Fluency",
    }

    winner_metrics = winner_stats.get("metric_averages", {})
    loser_metrics = loser_stats.get("metric_averages", {})

    metric_comparison = {}
    metrics_won = 0
    for key, label in metric_names.items():
        w_score = winner_metrics.get(key, 0)
        l_score = loser_metrics.get(key, 0)
        metric_comparison[label] = {
            winner_name: w_score,
            loser_name: l_score,
        }
        if w_score >= l_score:
            metrics_won += 1

    failure_mode = _identify_failure_mode(
        loser_name, evaluation_results.get("scenario_scores", [])
    )

    winner_avg = winner_stats.get("overall_average", 0)
    loser_avg = loser_stats.get("overall_average", 0)

    reason = (
        f"Highest overall average ({winner_avg:.2f} vs {loser_avg:.2f}) "
        f"and leads on {metrics_won} of 3 custom metrics."
    )

    production = (
        f"Use {winner_name} — more complete, tone-accurate, and polished emails "
        f"across the same 10 scenarios."
    )

    return {
        "recommended_strategy": winner_name,
        "reason": reason,
        "biggest_failure_mode": failure_mode,
        "production_recommendation": production,
        "overall_averages": {
            winner_name: winner_avg,
            loser_name: loser_avg,
        },
        "metric_comparison": metric_comparison,
        "winner": winner_name,
        "loser": loser_name,
    }


def _identify_failure_mode(strategy: str, scenario_scores: list[dict]) -> str:
    """Identify the biggest failure mode for a strategy from per-scenario scores."""
    strategy_rows = [r for r in scenario_scores if r.get("strategy") == strategy]
    if not strategy_rows:
        return "Insufficient data to determine failure mode."

    metric_totals = {
        "fact_recall": 0.0,
        "tone_and_format_accuracy": 0.0,
        "conciseness_and_fluency": 0.0,
    }
    for row in strategy_rows:
        scores = row.get("scores", {})
        for key in metric_totals:
            metric_totals[key] += scores.get(key, 0)

    n = len(strategy_rows)
    metric_avgs = {k: v / n for k, v in metric_totals.items()}
    worst_metric = min(metric_avgs, key=metric_avgs.get)

    failure_messages = {
        "fact_recall": "missed key facts and omitted required information from inputs",
        "tone_and_format_accuracy": "inconsistent formatting and tone misalignment",
        "conciseness_and_fluency": "wordy or poorly structured sentences",
    }

    label = {
        "fact_recall": "Fact Recall",
        "tone_and_format_accuracy": "Tone and Format Accuracy",
        "conciseness_and_fluency": "Conciseness and Fluency",
    }[worst_metric]

    return (
        f"Lowest average on {label} ({metric_avgs[worst_metric]:.2f}): "
        f"{failure_messages[worst_metric]}."
    )
