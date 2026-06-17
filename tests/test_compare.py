"""Tests for strategy comparison (TC-12, TC-25)."""

from __future__ import annotations

import pytest

from src.compare import compare_strategies


def _evaluation(basic_avg: float, structured_avg: float) -> dict:
    return {
        "strategy_averages": {
            "basic": {
                "overall_average": basic_avg,
                "metric_averages": {
                    "fact_recall": basic_avg,
                    "tone_and_format_accuracy": basic_avg,
                    "conciseness_and_fluency": basic_avg,
                },
            },
            "structured": {
                "overall_average": structured_avg,
                "metric_averages": {
                    "fact_recall": structured_avg,
                    "tone_and_format_accuracy": structured_avg - 0.1,
                    "conciseness_and_fluency": structured_avg,
                },
            },
        },
        "scenario_scores": [
            {"strategy": "basic", "scores": {"fact_recall": 1.0, "tone_and_format_accuracy": 0.9, "conciseness_and_fluency": 0.9}},
            {"strategy": "structured", "scores": {"fact_recall": 0.5, "tone_and_format_accuracy": 0.5, "conciseness_and_fluency": 0.9}},
        ],
    }


def test_compare_picks_basic_when_higher():
    result = compare_strategies(_evaluation(basic_avg=0.98, structured_avg=0.85))
    assert result["winner"] == "basic"


def test_compare_picks_structured_when_higher():
    result = compare_strategies(_evaluation(basic_avg=0.72, structured_avg=0.94))
    assert result["winner"] == "structured"
    assert result["recommended_strategy"] == "structured"


def test_compare_identifies_failure_mode():
    result = compare_strategies(_evaluation(basic_avg=0.98, structured_avg=0.85))
    assert "Fact Recall" in result["biggest_failure_mode"]


def test_compare_requires_two_strategies():
    with pytest.raises(ValueError, match="two strategies"):
        compare_strategies({"strategy_averages": {"basic": {"overall_average": 0.9}}})
