"""Custom evaluation metrics for generated emails."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.parser import ParsedEmail, parse_email


METRIC_DEFINITIONS = {
    "fact_recall": {
        "name": "Fact Recall",
        "definition": (
            "Measures whether the generated email includes all required key facts "
            "from the input scenario."
        ),
        "logic": (
            "For each key fact, check if its meaningful content appears in the email "
            "(case-insensitive keyword overlap). Score = included_facts / total_facts. "
            "Missing facts are listed in the result."
        ),
    },
    "tone_and_format_accuracy": {
        "name": "Tone and Format Accuracy",
        "definition": (
            "Measures whether the email matches the requested tone and contains "
            "all four expected sections: subject, greeting, body, and closing."
        ),
        "logic": (
            "Format score (0.5 max): 0.125 per present section (subject, greeting, body, closing). "
            "Tone score (0.5 max): keyword/pattern match against tone-specific indicators. "
            "Final score = format_score + tone_score (0.0–1.0)."
        ),
    },
    "conciseness_and_fluency": {
        "name": "Conciseness and Fluency",
        "definition": (
            "Measures readability, polish, and conciseness of the generated email."
        ),
        "logic": (
            "Starts at 1.0 and applies penalties: excessive length (>180 words), "
            "very short body (<20 words), repeated sentences, grammar issues "
            "(double spaces, missing punctuation), or excessive wordiness patterns."
        ),
    },
}

TONE_INDICATORS: dict[str, list[str]] = {
    "formal": [
        "thank you", "please", "regarding", "appreciate", "sincerely", "respectfully",
        "kindly", "would like", "following up",
    ],
    "casual": [
        "hi", "hey", "hope", "quick", "thanks", "let me know", "catch up", "cheers",
    ],
    "urgent": [
        "promptly", "asap", "urgent", "immediately", "earliest", "deadline",
        "time-sensitive", "priority", "soon as possible",
    ],
    "empathetic": [
        "understand", "sorry", "apologize", "inconvenience", "appreciate your patience",
        "concern", "support", "here to help",
    ],
    "professional": [
        "thank you", "please", "follow up", "discuss", "confirm", "update",
        "best regards", "looking forward",
    ],
}


@dataclass
class MetricResult:
    score: float
    details: dict[str, Any] = field(default_factory=dict)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _fact_in_email(fact: str, email_text: str) -> bool:
    """Check if a key fact's content appears in the email."""
    fact_norm = _normalize(fact)
    email_norm = _normalize(email_text)

    if fact_norm in email_norm:
        return True

    words = [w for w in re.findall(r"[a-z0-9]+", fact_norm) if len(w) > 3]
    if not words:
        words = re.findall(r"[a-z0-9]+", fact_norm)

    if not words:
        return False

    matched = sum(1 for w in words if w in email_norm)
    threshold = max(1, int(len(words) * 0.5))
    return matched >= threshold


def score_fact_recall(key_facts: list[str], email_text: str) -> MetricResult:
    included = []
    missing = []

    for fact in key_facts:
        if _fact_in_email(fact, email_text):
            included.append(fact)
        else:
            missing.append(fact)

    total = len(key_facts)
    score = len(included) / total if total else 0.0

    return MetricResult(
        score=round(score, 4),
        details={
            "included_count": len(included),
            "total_count": total,
            "included": included,
            "missing": missing,
            "summary": f"{len(included)} of {total} key facts included",
        },
    )


def score_tone_and_format(tone: str, email_text: str) -> MetricResult:
    parsed = parse_email(email_text)
    sections = {
        "subject": bool(parsed.subject.strip()),
        "greeting": bool(parsed.greeting.strip()),
        "body": bool(parsed.body.strip()),
        "closing": bool(parsed.closing.strip()),
    }

    format_score = sum(0.125 for present in sections.values() if present)

    tone_key = tone.lower().strip()
    indicators = TONE_INDICATORS.get(tone_key, TONE_INDICATORS["professional"])
    email_lower = email_text.lower()
    tone_hits = sum(1 for ind in indicators if ind in email_lower)
    tone_score = min(0.5, (tone_hits / max(len(indicators) * 0.3, 1)) * 0.5)

    score = round(min(1.0, format_score + tone_score), 4)
    missing_sections = [k for k, v in sections.items() if not v]

    return MetricResult(
        score=score,
        details={
            "sections_present": sections,
            "missing_sections": missing_sections,
            "tone_requested": tone,
            "tone_indicator_hits": tone_hits,
            "format_score": round(format_score, 4),
            "tone_score": round(tone_score, 4),
        },
    )


def score_conciseness_and_fluency(email_text: str) -> MetricResult:
    parsed = parse_email(email_text)
    body = parsed.body or email_text
    words = re.findall(r"\b\w+\b", body)
    word_count = len(words)

    score = 1.0
    penalties: list[str] = []

    if word_count > 180:
        score -= 0.25
        penalties.append("excessive length")
    elif word_count < 20:
        score -= 0.25
        penalties.append("body too short")

    sentences = [s.strip() for s in re.split(r"[.!?]+", body) if s.strip()]
    if len(sentences) != len(set(s.lower() for s in sentences)) and len(sentences) > 1:
        score -= 0.25
        penalties.append("repeated sentences")

    if "  " in email_text:
        score -= 0.15
        penalties.append("double spaces")

    wordy_patterns = [
        r"\b(in order to|due to the fact that|at this point in time|"
        r"for the purpose of|it is important to note that)\b",
    ]
    for pattern in wordy_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            score -= 0.15
            penalties.append("wordy phrasing")
            break

    if body and body[-1] not in ".!?":
        score -= 0.1
        penalties.append("missing end punctuation")

    score = round(max(0.0, min(1.0, score)), 4)

    return MetricResult(
        score=score,
        details={
            "word_count": word_count,
            "sentence_count": len(sentences),
            "penalties": penalties,
        },
    )


def evaluate_email(
    email_text: str,
    key_facts: list[str],
    tone: str,
) -> dict[str, Any]:
    """Run all three custom metrics on a generated email."""
    fact = score_fact_recall(key_facts, email_text)
    tone_fmt = score_tone_and_format(tone, email_text)
    fluency = score_conciseness_and_fluency(email_text)

    scores = {
        "fact_recall": fact.score,
        "tone_and_format_accuracy": tone_fmt.score,
        "conciseness_and_fluency": fluency.score,
    }
    overall = round(sum(scores.values()) / 3, 4)

    return {
        "scores": scores,
        "overall_average": overall,
        "details": {
            "fact_recall": fact.details,
            "tone_and_format_accuracy": tone_fmt.details,
            "conciseness_and_fluency": fluency.details,
        },
    }
