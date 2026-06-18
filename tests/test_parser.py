"""Tests for email section parsing (TC-19, TC-20)."""

from __future__ import annotations

from src.parser import email_to_text, parse_email


def test_parse_email_extracts_all_sections(sample_email):
    parsed = parse_email(sample_email)
    assert parsed.subject == "Follow-Up on Product Demo"
    assert parsed.greeting.startswith("Hi")
    assert "product demo on Monday" in parsed.body
    assert "Best regards" in parsed.closing


def test_parse_subject_line_variant():
    text = "Subject Line: Quarterly Review\n\nDear Team,\n\nBody here.\n\nRegards,\nSender"
    parsed = parse_email(text)
    assert parsed.subject == "Quarterly Review"
    assert parsed.greeting.startswith("Dear")


def test_parse_email_without_closing():
    text = "Subject: Update\n\nHello,\n\nOnly a body with no sign-off."
    parsed = parse_email(text)
    assert parsed.subject == "Update"
    assert parsed.body
    assert not parsed.closing


def test_thank_you_in_body_is_not_treated_as_closing():
    """Structured emails use tone phrases like 'Thank you' in the body."""
    text = (
        "Subject: Follow-Up on Demo\n\n"
        "Hi [Recipient Name],\n\n"
        "I am following up regarding the product demo we held on Monday. "
        "Thank you for your interest in our automation dashboard.\n\n"
        "As requested, I will share the proposal by Friday.\n\n"
        "Best regards,\n[Sender Name]"
    )
    parsed = parse_email(text)
    assert "automation dashboard" in parsed.body
    assert "proposal by Friday" in parsed.body
    assert parsed.closing.startswith("Best regards")
    assert len(parsed.body.split()) >= 20


def test_email_to_text_round_trip(sample_email):
    parsed = parse_email(sample_email)
    rebuilt = email_to_text(parsed)
    assert "Subject: Follow-Up on Product Demo" in rebuilt
    assert "Best regards" in rebuilt
