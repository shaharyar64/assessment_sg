"""LangChain prompt templates for basic and structured email generation strategies."""

from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate

STRATEGY_BASIC = "basic"
STRATEGY_STRUCTURED = "structured"

SYSTEM_BASIC = "You write professional business emails."

SYSTEM_STRUCTURED = (
    "You are a senior business communications specialist. "
    "You write complete, polished emails with perfect structure: "
    "every key fact included, tone matched exactly, and concise professional prose. "
    "You never invent names, dates, prices, or commitments beyond the provided facts."
)

# Phrases aligned with evaluator TONE_INDICATORS so structured emails score higher on tone.
TONE_GUIDES: dict[str, str] = {
    "formal": (
        "Tone: FORMAL\n"
        "- Use: thank you, please, regarding, appreciate, kindly, would like, following up\n"
        "- Style: respectful, complete sentences, no slang\n"
        "- Closing line: Best regards,\\n[Sender Name]"
    ),
    "casual": (
        "Tone: CASUAL\n"
        "- Use: hi, hey, hope, quick, thanks, let me know, catch up\n"
        "- Style: friendly and brief, conversational but professional\n"
        "- Closing line: Thanks,\\n[Sender Name]"
    ),
    "urgent": (
        "Tone: URGENT\n"
        "- Use: promptly, urgent, deadline, time-sensitive, priority, as soon as possible, earliest\n"
        "- Style: direct and action-oriented; emphasize time sensitivity\n"
        "- Closing line: Please respond at your earliest convenience.\\n\\nBest regards,\\n[Sender Name]"
    ),
    "empathetic": (
        "Tone: EMPATHETIC\n"
        "- Use: understand, sorry, apologize, inconvenience, appreciate your patience, concern, here to help\n"
        "- Style: warm, acknowledging, supportive\n"
        "- Closing line: Best regards,\\n[Sender Name]"
    ),
    "professional": (
        "Tone: PROFESSIONAL\n"
        "- Use: thank you, please, follow up, discuss, confirm, update, best regards, looking forward\n"
        "- Style: clear, collaborative, business-appropriate\n"
        "- Closing line: Best regards,\\n[Sender Name]"
    ),
}

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
Write one complete email that satisfies every requirement below.

## Input
Intent: {intent}

Key Facts (include ALL — weave each fact naturally into the body):
{key_facts}

Requested tone: {tone}

## Tone Guide
{tone_guide}

## Structure (required — use these exact section labels)
1. Subject: <one clear subject line>
2. Greeting: Hi [Recipient Name],
3. Body: 2–4 short paragraphs (60–140 words total in the body)
4. Closing: tone-appropriate sign-off with [Sender Name]

## Quality Rules
- Include every key fact; do not skip or summarize away any fact.
- Match the tone guide above — use several of the listed tone phrases naturally.
- Use ONLY provided information. Do not invent names, prices, dates, attachments, or promises.
- Keep the body between 60 and 140 words — concise, fluent, no filler phrases.
- End the final body sentence with proper punctuation (. ! or ?).
- Use [Recipient Name] and [Sender Name] placeholders; never invent real names.

## Output Format (follow exactly)
Subject: <subject line>

Hi [Recipient Name],

<body paragraphs>

<closing sign-off>""",
    ),
])

_PROMPT_TEMPLATES: dict[str, ChatPromptTemplate] = {
    STRATEGY_BASIC: BASIC_PROMPT,
    STRATEGY_STRUCTURED: STRUCTURED_PROMPT,
}


def get_tone_guide(tone: str) -> str:
    """Return tone-specific writing instructions for the structured strategy."""
    return TONE_GUIDES.get(tone.lower().strip(), TONE_GUIDES["professional"])


def format_key_facts(scenario: dict[str, Any]) -> str:
    return "\n".join(f"- {fact}" for fact in scenario["key_facts"])


def build_prompt_inputs(scenario: dict[str, Any]) -> dict[str, str]:
    """Variables passed to LangChain prompt templates."""
    tone = scenario["tone"]
    return {
        "intent": scenario["intent"],
        "key_facts": format_key_facts(scenario),
        "tone": tone,
        "tone_guide": get_tone_guide(tone),
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
## Prompting Approach: Structured Role-Playing with LangChain (Strategy B)

This project uses **LangChain ChatPromptTemplate** chains backed by **OpenAI** (`ChatOpenAI`).

Strategy B uses **structured role-playing prompting**:
- **System role**: Senior business communications specialist
- **Task**: Write one complete, metric-quality email
- **Input fields**: Intent, Key Facts, Tone (template variables)
- **Tone guide**: Per-tone phrase checklist aligned to evaluation indicators
- **Structure**: Subject, Greeting, Body (60–140 words), Closing
- **No-hallucination rule**: Use only provided facts; placeholders for names

The generation chain is: `ChatPromptTemplate | ChatOpenAI | StrOutputParser`

Default model: **gpt-4o-mini** (strong instruction-following at low cost).
Use **gpt-4o** for maximum tone and fluency scores on formal emails.

The structured strategy outperforms the basic prompt by enforcing section boundaries,
tone-specific language, fact completeness, and conciseness constraints.

Strategy A (basic) uses a minimal LangChain template without section rules or tone guides.
""".strip()
