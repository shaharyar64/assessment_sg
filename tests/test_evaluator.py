"""Tests for custom evaluation metrics (TC-08–TC-10, TC-21–TC-24)."""

from __future__ import annotations

from src.evaluator import (
    evaluate_email,
    score_conciseness_and_fluency,
    score_fact_recall,
    score_tone_and_format,
)


def test_fact_recall_perfect_when_all_facts_present(sample_email):
    facts = ["The demo was held on Monday", "The client asked for pricing details"]
    result = score_fact_recall(facts, sample_email)
    assert result.score == 1.0
    assert result.details["included_count"] == 2


def test_fact_recall_partial_when_some_facts_missing(sample_email):
    facts = [
        "The demo was held on Monday",
        "The client asked for pricing details",
        "The client is interested in the automation dashboard",
    ]
    result = score_fact_recall(facts, sample_email)
    assert 0.0 < result.score < 1.0
    assert any("automation" in m.lower() for m in result.details["missing"])


def test_fact_recall_zero_when_facts_missing():
    result = score_fact_recall(
        ["The contract expires next year"],
        "Subject: Hello\n\nHi there,\n\nGeneric message.\n\nThanks",
    )
    assert result.score == 0.0


def test_tone_and_format_detects_sections(sample_email):
    result = score_tone_and_format("Formal", sample_email)
    assert result.score >= 0.5
    assert result.details["sections_present"]["subject"] is True


def test_urgent_tone_scores_with_urgency_keywords():
    email = (
        "Subject: Deadline Tomorrow\n\nHi,\n\nThis is urgent. "
        "The deadline is tomorrow. Please respond ASAP.\n\nBest regards,\nSender"
    )
    result = score_tone_and_format("Urgent", email)
    assert result.details["tone_indicator_hits"] >= 1


def test_empathetic_tone_scores_with_empathy_keywords():
    email = (
        "Subject: Apology\n\nHi,\n\nI apologize for the inconvenience. "
        "I understand your concern and appreciate your patience.\n\nBest regards,\nSender"
    )
    result = score_tone_and_format("Empathetic", email)
    assert result.details["tone_indicator_hits"] >= 1


def test_conciseness_penalizes_excessive_length():
    long_body = "word " * 200
    email = f"Subject: Test\n\nHi there,\n\n{long_body}\n\nBest regards,\nSender"
    result = score_conciseness_and_fluency(email)
    assert result.score < 1.0
    assert "excessive length" in result.details["penalties"]


def test_conciseness_penalizes_short_body():
    email = "Subject: Test\n\nHi,\n\nToo short.\n\nBest regards,\nSender"
    result = score_conciseness_and_fluency(email)
    assert "body too short" in result.details["penalties"]


def test_conciseness_penalizes_double_spaces():
    email = "Subject: Test\n\nHi,\n\nBody  with  double  spaces.\n\nBest regards,\nSender"
    result = score_conciseness_and_fluency(email)
    assert "double spaces" in result.details["penalties"]


def test_evaluate_email_overall_average_is_mean_of_three(sample_email):
    result = evaluate_email(
        email_text=sample_email,
        key_facts=["The demo was held on Monday", "The client asked for pricing details"],
        tone="Formal",
    )
    scores = result["scores"]
    expected = round(
        (scores["fact_recall"] + scores["tone_and_format_accuracy"] + scores["conciseness_and_fluency"]) / 3,
        4,
    )
    assert result["overall_average"] == expected
