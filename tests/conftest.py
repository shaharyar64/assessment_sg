"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def valid_scenario() -> dict:
    return {
        "id": "TEST-001",
        "intent": "Follow up after a product demo",
        "key_facts": [
            "The demo was held on Monday",
            "The client asked for pricing details",
        ],
        "tone": "Formal",
    }


@pytest.fixture
def sample_email() -> str:
    return (
        "Subject: Follow-Up on Product Demo\n\n"
        "Hi [Recipient Name],\n\n"
        "I wanted to follow up on the product demo on Monday. "
        "The client asked for pricing details and we will share the proposal by Friday.\n\n"
        "Best regards,\n[Sender Name]"
    )
