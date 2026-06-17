"""Parse generated email text into structured sections."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedEmail:
    subject: str
    greeting: str
    body: str
    closing: str
    raw: str


SUBJECT_PATTERNS = [
    re.compile(r"^Subject:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^Subject Line:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
]

GREETING_PATTERN = re.compile(
    r"^(Hi|Hello|Dear|Good morning|Good afternoon|Greetings)\b[^\n]*",
    re.IGNORECASE | re.MULTILINE,
)

CLOSING_PATTERN = re.compile(
    r"(Best regards|Sincerely|Kind regards|Warm regards|Thanks|Thank you|Regards|"
    r"Yours sincerely|Yours truly|Respectfully)[^\n]*(?:\n\[?[^\]]+\]?)?$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_email(text: str) -> ParsedEmail:
    """Extract subject, greeting, body, and closing from email text."""
    raw = text.strip()
    subject = ""
    remaining = raw

    for pattern in SUBJECT_PATTERNS:
        match = pattern.search(remaining)
        if match:
            subject = match.group(1).strip()
            remaining = remaining[match.end() :].strip()
            break

    greeting = ""
    greeting_match = GREETING_PATTERN.search(remaining)
    if greeting_match:
        greeting = greeting_match.group(0).strip()
        remaining = remaining[greeting_match.end() :].strip()

    closing = ""
    closing_match = CLOSING_PATTERN.search(remaining)
    if closing_match:
        closing = closing_match.group(0).strip()
        body = remaining[: closing_match.start()].strip()
    else:
        body = remaining.strip()

    return ParsedEmail(
        subject=subject,
        greeting=greeting,
        body=body,
        closing=closing,
        raw=raw,
    )


def email_to_text(parsed: ParsedEmail) -> str:
    """Reconstruct email text from parsed sections."""
    parts = []
    if parsed.subject:
        parts.append(f"Subject: {parsed.subject}")
    if parsed.greeting:
        parts.append("")
        parts.append(parsed.greeting)
    if parsed.body:
        parts.append("")
        parts.append(parsed.body)
    if parsed.closing:
        parts.append("")
        parts.append(parsed.closing)
    return "\n".join(parts).strip()
