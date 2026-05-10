# pyright: reportMissingModuleSource=false

from __future__ import annotations

from pathlib import Path
import re
from typing import Any
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
ORDERED_LIST_PATTERN = re.compile(r"(?P<num>\d+)\.\s+(?P<text>.+)")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")


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
    lines = markdown_report.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped:
            if story:
                story.append(Spacer(1, 0.08 * inch))
            index += 1
            continue

        image_match = IMAGE_PATTERN.fullmatch(stripped)
        if image_match:
            story.extend(_image_flowables(image_match.group("path"), image_match.group("alt"), report_dir))
            index += 1
            continue

        if _looks_like_table_row(stripped):
            table_lines = [raw_line]
            index += 1
            while index < len(lines) and _looks_like_table_row(lines[index].strip()):
                table_lines.append(lines[index])
                index += 1
            table_flowables = _table_flowable(table_lines, styles)
            if table_flowables is not None:
                story.extend(table_flowables)
                continue
            for table_line in table_lines:
                story.append(Paragraph(escape(_sanitize_markdown_text(table_line.strip())), styles["body"]))
            continue

        if stripped.startswith("# "):
            text = _sanitize_markdown_text(stripped[2:])
            story.append(Paragraph(escape(text), styles["title"]))
            story.append(Spacer(1, 0.14 * inch))
            title_seen = True
            index += 1
            continue

        if stripped.startswith("## "):
            text = _sanitize_markdown_text(stripped[3:])
            if title_seen:
                story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(escape(text), styles["h2"]))
            index += 1
            continue

        if stripped.startswith("### "):
            text = _sanitize_markdown_text(stripped[4:])
            story.append(Paragraph(escape(text), styles["h3"]))
            index += 1
            continue

        ordered_match = ORDERED_LIST_PATTERN.fullmatch(stripped)
        if ordered_match:
            text = _sanitize_markdown_text(ordered_match.group("text"))
            story.append(Paragraph(escape(text), styles["bullet"], bulletText=f'{ordered_match.group("num")}.'))
            index += 1
            continue

        if stripped.startswith("- "):
            text = _sanitize_markdown_text(stripped[2:])
            story.append(Paragraph(escape(text), styles["bullet"], bulletText="-"))
            index += 1
            continue

        story.append(Paragraph(escape(_sanitize_markdown_text(stripped)), styles["body"]))
        index += 1

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
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=HexColor("#111111"),
        ),
        "table_cell": ParagraphStyle(
            "ReportTableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=HexColor("#222222"),
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


def _looks_like_table_row(text: str) -> bool:
    return text.startswith("|") and text.endswith("|") and text.count("|") >= 3


def _table_flowable(table_lines: list[str], styles: dict[str, ParagraphStyle]) -> list[Any] | None:
    if len(table_lines) < 2:
        return None

    rows = [_split_table_row(line) for line in table_lines]
    if not rows or not _is_separator_row(rows[1]):
        return None

    body_rows = [rows[0], *rows[2:]]
    column_count = max(len(row) for row in body_rows)
    normalized_rows = [row + [""] * (column_count - len(row)) for row in body_rows]
    widths = _table_column_widths(normalized_rows)
    table_data: list[list[Paragraph]] = []

    for row_index, row in enumerate(normalized_rows):
        style = styles["table_header"] if row_index == 0 else styles["table_cell"]
        table_data.append([Paragraph(escape(_sanitize_markdown_text(cell)), style) for cell in row])

    table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EEF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#111111")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#F7F9FC")]),
            ]
        )
    )
    return [table, Spacer(1, 0.08 * inch)]


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(row: list[str]) -> bool:
    return bool(row) and all(TABLE_SEPARATOR_PATTERN.fullmatch(cell.strip()) for cell in row)


def _table_column_widths(rows: list[list[str]]) -> list[float]:
    max_width = 7.2 * inch
    column_count = len(rows[0])
    weights: list[float] = []

    for column_index in range(column_count):
        column_lengths = [len(re.sub(r"\s+", " ", row[column_index]).strip()) for row in rows]
        weight = max(column_lengths) or 1
        weights.append(float(min(max(weight, 10), 60)))

    total_weight = sum(weights) or float(column_count)
    return [max_width * (weight / total_weight) for weight in weights]


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
