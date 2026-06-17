"""PDF report generation for final analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.evaluator import METRIC_DEFINITIONS
from src.prompt_builder import PROMPT_TEMPLATE_DOCUMENTATION, build_structured_prompt


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    safe = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return Paragraph(safe, style)


def generate_report(
    evaluation_results: dict[str, Any],
    comparison: dict[str, Any],
    output_path: str | Path,
    sample_scenario: dict[str, Any] | None = None,
) -> Path:
    """Generate the final PDF report."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    heading = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=8,
    )
    body = styles["BodyText"]
    mono = ParagraphStyle("Mono", parent=body, fontName="Courier", fontSize=8, leading=10)

    story: list[Any] = []

    story.append(_p("Email Generation Assistant — Final Report", title_style))
    story.append(_p(
        "This report documents the prompting approach, custom evaluation metrics, "
        "raw evaluation results, strategy comparison, and production recommendation.",
        body,
    ))
    story.append(Spacer(1, 0.2 * inch))

    story.append(_p("1. Project Summary", heading))
    story.append(_p(
        "A working Email Generation Assistant was built to produce professional emails "
        "from structured inputs: Intent, Key Facts, and Tone. Two prompting strategies "
        "were compared across 10 evaluation scenarios using three custom metrics.",
        body,
    ))

    story.append(_p("2. Prompting Approach and Template", heading))
    story.append(_p(PROMPT_TEMPLATE_DOCUMENTATION, body))
    if sample_scenario:
        template = build_structured_prompt(sample_scenario)
        story.append(Spacer(1, 0.1 * inch))
        story.append(_p("Structured Prompt Template (Strategy B):", body))
        story.append(_p(template[:2000], mono))

    story.append(_p("3. Evaluation Dataset Summary", heading))
    story.append(_p(
        "10 unique scenarios with Intent, Key Facts, Tone, and Human Reference Email. "
        "Each scenario was run through Strategy A (basic prompt) and Strategy B (structured prompt).",
        body,
    ))

    story.append(_p("4. Custom Metric Definitions and Logic", heading))
    for key, meta in METRIC_DEFINITIONS.items():
        story.append(_p(f"<b>{meta['name']}</b>", body))
        story.append(_p(f"Definition: {meta['definition']}", body))
        story.append(_p(f"Logic: {meta['logic']}", body))
        story.append(Spacer(1, 0.08 * inch))

    story.append(_p("5. Raw Evaluation Results", heading))
    strategy_avgs = evaluation_results.get("strategy_averages", {})
    table_data = [["Strategy", "Fact Recall", "Tone & Format", "Conciseness", "Overall"]]
    for strategy, stats in strategy_avgs.items():
        ma = stats.get("metric_averages", {})
        table_data.append([
            strategy,
            f"{ma.get('fact_recall', 0):.2f}",
            f"{ma.get('tone_and_format_accuracy', 0):.2f}",
            f"{ma.get('conciseness_and_fluency', 0):.2f}",
            f"{stats.get('overall_average', 0):.2f}",
        ])

    t = Table(table_data, colWidths=[1.5 * inch, 1.1 * inch, 1.2 * inch, 1.2 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FA")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.15 * inch))

    scenario_scores = evaluation_results.get("scenario_scores", [])[:5]
    if scenario_scores:
        story.append(_p("Sample per-scenario scores (first 5 entries):", body))
        sample_json = json.dumps(scenario_scores, indent=2)[:1500]
        story.append(_p(sample_json, mono))

    story.append(_p("6. Strategy Comparison", heading))
    winner = comparison.get("recommended_strategy", "N/A")
    loser = comparison.get("loser", "N/A")
    avgs = comparison.get("overall_averages", {})
    story.append(_p(
        f"Recommended strategy: <b>{winner}</b><br/>"
        f"Reason: {comparison.get('reason', '')}<br/>"
        f"Overall averages — {winner}: {avgs.get(winner, 0):.2f}, "
        f"{loser}: {avgs.get(loser, 0):.2f}",
        body,
    ))

    story.append(_p("7. Failure Mode Analysis", heading))
    story.append(_p(
        f"Biggest failure mode of {loser}: {comparison.get('biggest_failure_mode', 'N/A')}",
        body,
    ))

    story.append(_p("8. Final Recommendation", heading))
    story.append(_p(comparison.get("production_recommendation", ""), body))

    doc.build(story)
    return output_path
