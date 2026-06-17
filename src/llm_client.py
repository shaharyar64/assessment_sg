"""LangChain + Groq LLM client with deterministic mock mode."""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from src.prompt_builder import build_prompt_inputs, get_prompt_template

load_dotenv()

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def _tone_opening(tone: str) -> str:
    tone_lower = tone.lower()
    if "empathetic" in tone_lower:
        return "I understand your situation and want to address this thoughtfully."
    if "urgent" in tone_lower:
        return "I am writing to follow up promptly on the items below."
    if "casual" in tone_lower:
        return "Hope you're doing well — quick note on the items we discussed."
    if "formal" in tone_lower:
        return "Thank you for your time and attention regarding the following."
    return "Thank you for your message. I wanted to follow up on the points below."


def _tone_closing(tone: str) -> str:
    tone_lower = tone.lower()
    if "casual" in tone_lower:
        return "Thanks,\n[Sender Name]"
    if "urgent" in tone_lower:
        return "Please respond at your earliest convenience.\n\nBest regards,\n[Sender Name]"
    return "Best regards,\n[Sender Name]"


def mock_generate(prompt: str, scenario: dict[str, Any] | None = None) -> str:
    """
    Deterministic mock generation for demo/offline runs.
    Uses scenario data when available; otherwise parses prompt text.
    """
    if scenario is None:
        scenario = _parse_prompt_fallback(prompt)

    intent = scenario.get("intent", "Follow up")
    tone = scenario.get("tone", "Professional")
    facts = scenario.get("key_facts", [])

    subject = intent.split(".")[0].strip()
    if not subject.lower().startswith(("re:", "follow", "request", "confirm", "apolog")):
        subject = subject[0].upper() + subject[1:] if subject else "Follow Up"

    greeting = "Hi [Recipient Name],"
    opening = _tone_opening(tone)

    body_parts = [opening]
    for fact in facts:
        body_parts.append(fact.rstrip(".") + ".")

    body_parts.append(
        "Please let me know if you need any additional information."
    )
    body = "\n\n".join(body_parts)
    closing = _tone_closing(tone)

    is_structured = "## Task" in prompt or "## Output Requirements" in prompt
    if not is_structured and len(facts) > 2:
        body = "\n\n".join(body_parts[:2])

    return (
        f"Subject: {subject}\n\n"
        f"{greeting}\n\n"
        f"{body}\n\n"
        f"{closing}"
    )


def _parse_prompt_fallback(prompt: str) -> dict[str, Any]:
    intent_match = re.search(r"Intent:\s*(.+)", prompt)
    tone_match = re.search(r"Tone:\s*(.+)", prompt)
    facts = re.findall(r"^- (.+)$", prompt, re.MULTILINE)
    return {
        "intent": intent_match.group(1).strip() if intent_match else "Follow up",
        "tone": tone_match.group(1).strip() if tone_match else "Professional",
        "key_facts": facts or ["Follow up as discussed."],
    }


class LLMClient:
    """LangChain chain wrapper around Groq ChatGroq with mock fallback."""

    def __init__(self, model: str = DEFAULT_GROQ_MODEL, mock: bool = False):
        self.model = model
        self.mock = mock or not os.getenv("GROQ_API_KEY")
        self._llm = None
        self._chains: dict[str, Runnable] = {}

    def _get_llm(self, temperature: float = 0.3):
        if self._llm is None:
            from langchain_groq import ChatGroq

            self._llm = ChatGroq(
                model=self.model,
                temperature=temperature,
                groq_api_key=os.getenv("GROQ_API_KEY"),
            )
        return self._llm

    def _get_chain(self, strategy: str, temperature: float = 0.3) -> Runnable:
        cache_key = f"{strategy}:{temperature}"
        if cache_key not in self._chains:
            prompt = get_prompt_template(strategy)
            self._chains[cache_key] = prompt | self._get_llm(temperature) | StrOutputParser()
        return self._chains[cache_key]

    def generate(
        self,
        scenario: dict[str, Any],
        strategy: str,
        prompt: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """
        Generate an email using a LangChain prompt | ChatGroq | parser chain.

        `prompt` is optional and used only for mock mode detection when provided.
        """
        if self.mock:
            rendered = prompt or ""
            return mock_generate(rendered, scenario)

        chain = self._get_chain(strategy, temperature)
        return chain.invoke(build_prompt_inputs(scenario))
