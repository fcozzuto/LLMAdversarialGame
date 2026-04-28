# pyright: reportMissingModuleSource=false

from __future__ import annotations

from pathlib import Path
import re
from typing import Any
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")


def write_pdf_report(
    *,
    path: Path,
    run_name: str,
    markdown_report: str,
    suite_summary: dict[str, Any],
    condition_payloads: list[dict[str, Any]],
) -> None:
    del suite_summary, condition_payloads
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42,
        title=f"LLM Adversarial Grid Report {run_name}",
        author="llm_grid_battle",
    )
    doc.build(_build_story(markdown_report, path.parent, run_name))


def _build_story(markdown_report: str, report_dir: Path, run_name: str) -> list[Any]:
    styles = _build_styles()
    story: list[Any] = []
    title_seen = False

    for raw_line in markdown_report.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            if story:
                story.append(Spacer(1, 0.08 * inch))
            continue

        image_match = IMAGE_PATTERN.fullmatch(stripped)
        if image_match:
            story.extend(_image_flowables(image_match.group("path"), image_match.group("alt"), report_dir))
            continue

        if stripped.startswith("# "):
            text = _sanitize_markdown_text(stripped[2:])
            story.append(Paragraph(escape(text), styles["title"]))
            story.append(Spacer(1, 0.14 * inch))
            title_seen = True
            continue

        if stripped.startswith("## "):
            text = _sanitize_markdown_text(stripped[3:])
            if title_seen:
                story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(escape(text), styles["h2"]))
            continue

        if stripped.startswith("### "):
            text = _sanitize_markdown_text(stripped[4:])
            story.append(Paragraph(escape(text), styles["h3"]))
            continue

        if stripped.startswith("- "):
            text = _sanitize_markdown_text(stripped[2:])
            story.append(Paragraph(escape(text), styles["bullet"], bulletText="•"))
            continue

        story.append(Paragraph(escape(_sanitize_markdown_text(stripped)), styles["body"]))

    if not story:
        story.append(Paragraph(f"LLM Adversarial Grid Report {escape(run_name)}", styles["title"]))
    return story


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=HexColor("#111111"),
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "ReportH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=HexColor("#111111"),
            spaceBefore=6,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "ReportH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=HexColor("#111111"),
            spaceBefore=4,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=HexColor("#222222"),
            spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "ReportBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=HexColor("#222222"),
            leftIndent=12,
            firstLineIndent=0,
            spaceAfter=2,
        ),
        "caption": ParagraphStyle(
            "ReportCaption",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=11,
            textColor=HexColor("#555555"),
            spaceAfter=6,
        ),
    }


def _sanitize_markdown_text(text: str) -> str:
    return text.replace("`", "")


def _image_flowables(path_text: str, alt_text: str, report_dir: Path) -> list[Any]:
    styles = _build_styles()
    image_path = _resolve_image_path(path_text, report_dir)
    if not image_path.exists():
        return [
            Paragraph(
                escape(f"{alt_text or 'Chart image'} not found: {image_path}"),
                styles["caption"],
            )
        ]

    width, height = _image_dimensions(image_path)
    max_width = 6.9 * inch
    max_height = 3.0 * inch
    scale = min(max_width / width, max_height / height, 1.0)
    flowables: list[Any] = [
        Image(str(image_path), width=width * scale, height=height * scale),
        Spacer(1, 0.04 * inch),
    ]
    if alt_text:
        flowables.append(Paragraph(escape(_sanitize_markdown_text(alt_text)), styles["caption"]))
    return flowables


def _resolve_image_path(path_text: str, report_dir: Path) -> Path:
    cleaned = path_text.strip().strip("<>").replace("\\", "/")
    path = Path(cleaned)
    if path.is_absolute():
        return path
    return report_dir / path


def _image_dimensions(image_path: Path) -> tuple[int, int]:
    with PILImage.open(image_path) as image:
        return image.size
