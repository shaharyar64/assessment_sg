"""LangChain prompt templates for basic and structured email generation strategies."""

from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate

STRATEGY_BASIC = "basic"
STRATEGY_STRUCTURED = "structured"

SYSTEM_BASIC = "You write professional business emails."
SYSTEM_STRUCTURED = (
    "You are a professional business email writer. "
    "Follow instructions exactly and use only provided information."
)

BASIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BASIC),
    (
        "human",
        """Write a professional email.

Intent: {intent}
Key Facts:
{key_facts}
Tone: {tone}

Include a subject line, greeting, body, and closing.""",
    ),
])

STRUCTURED_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_STRUCTURED),
    (
        "human",
        """## Task
Generate one complete email based on the structured input below.

## Input
Intent: {intent}

Key Facts (every fact must appear naturally in the email):
{key_facts}

Tone: {tone}

## Output Requirements
Return the email with exactly these sections:
1. Subject: (one clear subject line)
2. Greeting: (e.g., Hi [Recipient Name],)
3. Body: (clear paragraphs covering the intent and all key facts)
4. Closing: (professional sign-off with [Sender Name])

## Rules
- Use ONLY information from the Key Facts. Do not invent names, prices, dates, attachments, or commitments not provided.
- Match the requested tone throughout.
- Keep the email professional and concise.
- Use placeholders [Recipient Name] and [Sender Name] instead of inventing names.

## Output Format
Subject: <subject line>

<greeting>

<body paragraphs>

<closing>""",
    ),
])

_PROMPT_TEMPLATES: dict[str, ChatPromptTemplate] = {
    STRATEGY_BASIC: BASIC_PROMPT,
    STRATEGY_STRUCTURED: STRUCTURED_PROMPT,
}


def format_key_facts(scenario: dict[str, Any]) -> str:
    return "\n".join(f"- {fact}" for fact in scenario["key_facts"])


def build_prompt_inputs(scenario: dict[str, Any]) -> dict[str, str]:
    """Variables passed to LangChain prompt templates."""
    return {
        "intent": scenario["intent"],
        "key_facts": format_key_facts(scenario),
        "tone": scenario["tone"],
    }


def get_prompt_template(strategy: str) -> ChatPromptTemplate:
    """Return the LangChain ChatPromptTemplate for a strategy."""
    if strategy not in _PROMPT_TEMPLATES:
        raise ValueError(f"Unknown strategy: {strategy}")
    return _PROMPT_TEMPLATES[strategy]


def build_prompt(scenario: dict[str, Any], strategy: str) -> str:
    """Render the full prompt string for logging, traces, and the final report."""
    template = get_prompt_template(strategy)
    messages = template.format_messages(**build_prompt_inputs(scenario))
    parts: list[str] = []
    for message in messages:
        role = message.type.upper()
        parts.append(f"[{role}]\n{message.content}")
    return "\n\n".join(parts)


def build_basic_prompt(scenario: dict[str, Any]) -> str:
    return build_prompt(scenario, STRATEGY_BASIC)


def build_structured_prompt(scenario: dict[str, Any]) -> str:
    return build_prompt(scenario, STRATEGY_STRUCTURED)


PROMPT_TEMPLATE_DOCUMENTATION = """
## Prompting Approach: Structured Prompting with LangChain (Strategy B)

This project uses **LangChain ChatPromptTemplate** chains backed by **Groq** (`ChatGroq`).

Strategy B uses **structured prompting** with a role instruction. The LangChain template separates:
- **System role**: Professional business email writer
- **Task**: Generate one complete email
- **Input fields**: Intent, Key Facts, Tone (template variables)
- **Output requirements**: Subject, Greeting, Body, Closing
- **No-hallucination rule**: Use only provided facts; placeholders for names

The generation chain is: `ChatPromptTemplate | ChatGroq | StrOutputParser`

This improves reliability by giving the model explicit section boundaries and
constraints, reducing missed facts and invented details compared to the basic prompt.

Strategy A (basic) uses a minimal LangChain template without section rules or hallucination guardrails.
""".strip()
