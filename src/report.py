"""Word report generation for final analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Inches

from src.docx_helpers import add_body
from src.docx_content import (
    write_comparative_analysis_section,
    write_metrics_section,
    write_prompts_section,
    write_raw_data_section,
)
from src.generator import load_scenarios


def _save_docx(doc: Document, output_path: Path) -> Path:
    """Save a Word doc; use a fallback filename if the target file is open in Word."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(f"{output_path.stem}.tmp{output_path.suffix}")

    doc.save(str(temp_path))
    try:
        temp_path.replace(output_path)
        return output_path
    except PermissionError:
        fallback = output_path.with_name(f"{output_path.stem}_new{output_path.suffix}")
        temp_path.replace(fallback)
        return fallback
    finally:
        temp_path.unlink(missing_ok=True)


def generate_report_docx(
    evaluation_results: dict[str, Any],
    comparison: dict[str, Any],
    output_path: str | Path,
    sample_scenario: dict[str, Any] | None = None,
    scenarios_path: str | Path | None = None,
) -> Path:
    """Generate the final report as a Word document (.docx)."""
    if sample_scenario is None and scenarios_path:
        scenarios = load_scenarios(scenarios_path)
        sample_scenario = scenarios[0] if scenarios else None

    output_path = Path(output_path)
    winner = comparison.get("recommended_strategy", comparison.get("winner", "N/A"))

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    doc.add_heading("Email Generation Assistant — Final Report", level=0)
    add_body(
        doc,
        "LangChain + OpenAI email generator. 10 scenarios × 2 strategies. "
        f"Recommended strategy: {winner}.",
    )

    write_prompts_section(doc, sample_scenario, winner)
    write_metrics_section(doc)
    write_comparative_analysis_section(doc, comparison)
    write_raw_data_section(doc, evaluation_results)

    return _save_docx(doc, output_path)
