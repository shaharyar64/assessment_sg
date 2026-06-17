"""Tests for run_one CLI helpers (TC-14, TC-29)."""

from __future__ import annotations

from src.run_one import parse_facts


def test_parse_facts_from_multiple_flags():
    assert parse_facts(["Fact one", "Fact two"]) == ["Fact one", "Fact two"]


def test_parse_facts_from_comma_separated():
    assert parse_facts(["Fact one, Fact two, Fact three"]) == ["Fact one", "Fact two", "Fact three"]


def test_parse_facts_strips_whitespace():
    assert parse_facts(["  Fact one  ,  Fact two  "]) == ["Fact one", "Fact two"]


def test_parse_facts_skips_empty_segments():
    assert parse_facts(["Fact one,, Fact two, "]) == ["Fact one", "Fact two"]
