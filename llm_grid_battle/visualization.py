from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _svg_header(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'


def _label_for(agent_name: str, agent_labels: dict[str, str] | None) -> str:
    if agent_labels and agent_name in agent_labels:
        return agent_labels[agent_name]
    return agent_name


def _text_size(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.ImageFont,
    text: str,
) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _wrap_label(text: str, *, max_line_length: int = 16) -> list[str]:
    words = text.split()
    if not words:
        return [text]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_line_length:
            current = candidate
            continue
        lines.append(current)
        current = word
    lines.append(current)
    return lines


def write_epoch_map_svg(
    *,
    path: Path,
    title: str,
    width: int,
    height: int,
    initial_resources: list[list[int]],
    obstacles: list[list[int]],
    paths: dict[str, list[list[int]]],
    agent_labels: dict[str, str] | None = None,
) -> None:
    cell = 42
    left_margin = 72
    top_margin = 72
    right_margin = 290
    bottom_margin = 82
    svg_width = width * cell + left_margin + right_margin
    svg_height = height * cell + top_margin + bottom_margin
    colors = {"agent_a": "#1f77b4", "agent_b": "#d62728"}

    parts = [
        _svg_header(svg_width, svg_height),
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left_margin}" y="34" font-family="Arial" font-size="22" font-weight="bold" fill="#111111">{escape(title)}</text>',
        f'<text x="{left_margin + (width * cell) / 2}" y="{svg_height - 18}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333333">x position</text>',
        f'<text x="22" y="{top_margin + (height * cell) / 2}" font-family="Arial" font-size="14" fill="#333333" transform="rotate(-90 22 {top_margin + (height * cell) / 2})">y position</text>',
    ]
    for y in range(height):
        for x in range(width):
            rx = left_margin + x * cell
            ry = top_margin + y * cell
            parts.append(f'<rect x="{rx}" y="{ry}" width="{cell}" height="{cell}" fill="#fafafa" stroke="#d6d6d6"/>')
        label_y = top_margin + y * cell + cell / 2 + 5
        parts.append(
            f'<text x="{left_margin - 14}" y="{label_y}" text-anchor="end" font-family="Arial" font-size="12" fill="#555555">{y}</text>'
        )

    for x in range(width):
        label_x = left_margin + x * cell + cell / 2
        parts.append(
            f'<text x="{label_x}" y="{top_margin + height * cell + 22}" text-anchor="middle" font-family="Arial" font-size="12" fill="#555555">{x}</text>'
        )

    for x, y in obstacles:
        rx = left_margin + x * cell
        ry = top_margin + y * cell
        parts.append(f'<rect x="{rx + 4}" y="{ry + 4}" width="{cell - 8}" height="{cell - 8}" fill="#6c757d"/>')

    for x, y in initial_resources:
        cx = left_margin + x * cell + cell / 2
        cy = top_margin + y * cell + cell / 2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{cell / 6}" fill="#2ca02c" opacity="0.65"/>')

    for name, points in paths.items():
        if not points:
            continue
        coords = []
        for x, y in points:
            coords.append(f"{left_margin + x * cell + cell / 2},{top_margin + y * cell + cell / 2}")
        parts.append(
            f'<polyline points="{" ".join(coords)}" fill="none" stroke="{colors.get(name, "#000000")}" '
            'stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
        )
        sx, sy = points[0]
        ex, ey = points[-1]
        parts.append(
            f'<circle cx="{left_margin + sx * cell + cell / 2}" cy="{top_margin + sy * cell + cell / 2}" r="{cell / 5}" fill="{colors.get(name, "#000000")}"/>'
        )
        parts.append(
            f'<circle cx="{left_margin + ex * cell + cell / 2}" cy="{top_margin + ey * cell + cell / 2}" r="{cell / 4.5}" fill="{colors.get(name, "#000000")}" opacity="0.45"/>'
        )

    legend_x = left_margin + width * cell + 28
    legend_y = top_margin
    parts.extend(
        [
            f'<text x="{legend_x}" y="{legend_y}" font-family="Arial" font-size="16" font-weight="bold" fill="#111111">Legend</text>',
            f'<circle cx="{legend_x + 10}" cy="{legend_y + 28}" r="7" fill="#2ca02c" opacity="0.65"/>',
            f'<text x="{legend_x + 28}" y="{legend_y + 33}" font-family="Arial" font-size="13" fill="#333333">Resource</text>',
            f'<rect x="{legend_x + 3}" y="{legend_y + 44}" width="14" height="14" fill="#6c757d"/>',
            f'<text x="{legend_x + 28}" y="{legend_y + 57}" font-family="Arial" font-size="13" fill="#333333">Obstacle</text>',
            f'<circle cx="{legend_x + 10}" cy="{legend_y + 80}" r="8" fill="#111111"/>',
            f'<text x="{legend_x + 28}" y="{legend_y + 85}" font-family="Arial" font-size="13" fill="#333333">Solid marker = start</text>',
            f'<circle cx="{legend_x + 10}" cy="{legend_y + 104}" r="8" fill="#111111" opacity="0.45"/>',
            f'<text x="{legend_x + 28}" y="{legend_y + 109}" font-family="Arial" font-size="13" fill="#333333">Translucent marker = end</text>',
            f'<text x="{legend_x}" y="{legend_y + 140}" font-family="Arial" font-size="16" font-weight="bold" fill="#111111">Agents</text>',
        ]
    )
    for index, name in enumerate(paths):
        row_y = legend_y + 166 + index * 28
        color = colors.get(name, "#000000")
        parts.extend(
            [
                f'<line x1="{legend_x}" y1="{row_y}" x2="{legend_x + 18}" y2="{row_y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>',
                f'<text x="{legend_x + 28}" y="{row_y + 5}" font-family="Arial" font-size="13" fill="#333333">{escape(_label_for(name, agent_labels))}</text>',
            ]
        )

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_score_plot_svg(
    *,
    path: Path,
    title: str,
    series: dict[str, list[float]],
    series_labels: dict[str, str] | None = None,
) -> None:
    width = 980
    height = 420
    left_margin = 72
    right_margin = 260
    top_margin = 68
    bottom_margin = 72
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    values = [point for line in series.values() for point in line]
    max_value = max(values) if values else 1.0
    x_count = max((len(line) for line in series.values()), default=1)

    def project_x(index: int) -> float:
        return left_margin + (index / max(1, x_count - 1)) * (width - left_margin - right_margin)

    def project_y(value: float) -> float:
        return height - bottom_margin - (value / max_value) * (height - top_margin - bottom_margin)

    parts = [
        _svg_header(width, height),
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left_margin}" y="34" font-family="Arial" font-size="22" font-weight="bold" fill="#111111">{escape(title)}</text>',
        f'<line x1="{left_margin}" y1="{height - bottom_margin}" x2="{width - right_margin}" y2="{height - bottom_margin}" stroke="#444444"/>',
        f'<line x1="{left_margin}" y1="{top_margin}" x2="{left_margin}" y2="{height - bottom_margin}" stroke="#444444"/>',
        f'<text x="{left_margin + (width - left_margin - right_margin) / 2}" y="{height - 20}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333333">Epoch</text>',
        f'<text x="24" y="{top_margin + (height - top_margin - bottom_margin) / 2}" font-family="Arial" font-size="14" fill="#333333" transform="rotate(-90 24 {top_margin + (height - top_margin - bottom_margin) / 2})">Score</text>',
    ]

    tick_count = min(6, max(2, x_count))
    x_tick_indexes = sorted({round(index * max(0, x_count - 1) / max(1, tick_count - 1)) for index in range(tick_count)})
    for tick_index in x_tick_indexes:
        x_pos = project_x(tick_index)
        parts.extend(
            [
                f'<line x1="{x_pos}" y1="{height - bottom_margin}" x2="{x_pos}" y2="{height - bottom_margin + 6}" stroke="#666666"/>',
                f'<text x="{x_pos}" y="{height - bottom_margin + 22}" text-anchor="middle" font-family="Arial" font-size="12" fill="#555555">{tick_index + 1}</text>',
            ]
        )

    y_tick_count = 5
    for tick_index in range(y_tick_count + 1):
        value = (max_value * tick_index) / y_tick_count
        y_pos = project_y(value)
        label = f"{value:.1f}" if max_value <= 12 else f"{value:.0f}"
        parts.extend(
            [
                f'<line x1="{left_margin - 6}" y1="{y_pos}" x2="{left_margin}" y2="{y_pos}" stroke="#666666"/>',
                f'<line x1="{left_margin}" y1="{y_pos}" x2="{width - right_margin}" y2="{y_pos}" stroke="#e6e6e6"/>',
                f'<text x="{left_margin - 10}" y="{y_pos + 4}" text-anchor="end" font-family="Arial" font-size="12" fill="#555555">{label}</text>',
            ]
        )

    for idx, (name, line) in enumerate(series.items()):
        if not line:
            continue
        coords = [f"{project_x(i)},{project_y(value)}" for i, value in enumerate(line)]
        color = colors[idx % len(colors)]
        parts.append(
            f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
        )
        legend_y = top_margin + 24 * idx
        label = _label_for(name, series_labels)
        parts.extend(
            [
                f'<line x1="{width - right_margin + 8}" y1="{legend_y}" x2="{width - right_margin + 30}" y2="{legend_y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>',
                f'<text x="{width - right_margin + 40}" y="{legend_y + 5}" font-family="Arial" font-size="14" fill="{color}">{escape(label)}</text>',
            ]
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_score_plot_png(
    *,
    path: Path,
    title: str,
    series: dict[str, list[float]],
    series_labels: dict[str, str] | None = None,
) -> None:
    width = 980
    height = 420
    left_margin = 72
    right_margin = 300
    top_margin = 68
    bottom_margin = 72
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    values = [point for line in series.values() for point in line]
    max_value = max(values) if values else 1.0
    x_count = max((len(line) for line in series.values()), default=1)

    def project_x(index: int) -> float:
        return left_margin + (index / max(1, x_count - 1)) * (width - left_margin - right_margin)

    def project_y(value: float) -> float:
        return height - bottom_margin - (value / max_value) * (height - top_margin - bottom_margin)

    def hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    draw.text((left_margin, 20), title, fill=(17, 17, 17), font=title_font)
    draw.line(
        [(left_margin, height - bottom_margin), (width - right_margin, height - bottom_margin)],
        fill=(68, 68, 68),
        width=2,
    )
    draw.line(
        [(left_margin, top_margin), (left_margin, height - bottom_margin)],
        fill=(68, 68, 68),
        width=2,
    )

    x_label = "Epoch"
    x_label_width, _ = _text_size(draw, body_font, x_label)
    draw.text(
        ((left_margin + (width - left_margin - right_margin) / 2) - (x_label_width / 2), height - 34),
        x_label,
        fill=(51, 51, 51),
        font=body_font,
    )
    y_label = "Score"
    draw.text((18, top_margin + 8), y_label, fill=(51, 51, 51), font=body_font)

    tick_count = min(6, max(2, x_count))
    x_tick_indexes = sorted(
        {
            round(index * max(0, x_count - 1) / max(1, tick_count - 1))
            for index in range(tick_count)
        }
    )
    for tick_index in x_tick_indexes:
        x_pos = project_x(tick_index)
        draw.line(
            [(x_pos, height - bottom_margin), (x_pos, height - bottom_margin + 6)],
            fill=(102, 102, 102),
            width=1,
        )
        tick_label = str(tick_index + 1)
        tick_width, _ = _text_size(draw, body_font, tick_label)
        draw.text(
            (x_pos - (tick_width / 2), height - bottom_margin + 10),
            tick_label,
            fill=(85, 85, 85),
            font=body_font,
        )

    y_tick_count = 5
    for tick_index in range(y_tick_count + 1):
        value = (max_value * tick_index) / y_tick_count
        y_pos = project_y(value)
        draw.line(
            [(left_margin - 6, y_pos), (left_margin, y_pos)],
            fill=(102, 102, 102),
            width=1,
        )
        draw.line(
            [(left_margin, y_pos), (width - right_margin, y_pos)],
            fill=(230, 230, 230),
            width=1,
        )
        label = f"{value:.1f}" if max_value <= 12 else f"{value:.0f}"
        label_width, label_height = _text_size(draw, body_font, label)
        draw.text(
            (left_margin - 10 - label_width, y_pos - (label_height / 2)),
            label,
            fill=(85, 85, 85),
            font=body_font,
        )

    for idx, (name, line) in enumerate(series.items()):
        if not line:
            continue
        color = hex_to_rgb(colors[idx % len(colors)])
        points = [(project_x(i), project_y(value)) for i, value in enumerate(line)]
        draw.line(points, fill=color, width=3)
        for x_pos, y_pos in points:
            draw.ellipse((x_pos - 2, y_pos - 2, x_pos + 2, y_pos + 2), fill=color)
        legend_y = top_margin + 24 * idx
        label = _label_for(name, series_labels)
        draw.line(
            [(width - right_margin + 8, legend_y), (width - right_margin + 30, legend_y)],
            fill=color,
            width=4,
        )
        draw.text(
            (width - right_margin + 40, legend_y - 6),
            label,
            fill=color,
            font=body_font,
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def write_grouped_bar_chart_png(
    *,
    path: Path,
    title: str,
    categories: list[str],
    series: dict[str, list[float]],
    x_label: str,
    y_label: str,
    series_labels: dict[str, str] | None = None,
    error_ranges: dict[str, list[tuple[float, float]]] | None = None,
    percent_scale: bool = False,
) -> None:
    width = 1080
    height = 520
    left_margin = 84
    right_margin = 280
    top_margin = 72
    bottom_margin = 116
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]

    def hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))

    def scale_value(value: float) -> float:
        return value * 100.0 if percent_scale else value

    def format_value(value: float) -> str:
        scaled = scale_value(value)
        if percent_scale:
            return f"{scaled:.1f}%"
        if scaled <= 12:
            return f"{scaled:.2f}"
        return f"{scaled:.1f}"

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    plotted_values = [scale_value(point) for points in series.values() for point in points]
    plotted_highs = plotted_values[:]
    if error_ranges:
        for name, ranges in error_ranges.items():
            for _, high in ranges:
                plotted_highs.append(scale_value(high))
            if name not in series:
                continue
    max_value = max(plotted_highs) if plotted_highs else 1.0
    max_value = max(1.0, max_value * 1.12)
    if percent_scale:
        max_value = min(100.0, max_value)

    plot_width = width - left_margin - right_margin
    plot_height = height - top_margin - bottom_margin
    group_count = max(1, len(categories))
    series_count = max(1, len(series))
    group_span = plot_width / group_count
    bar_width = min(60.0, (group_span * 0.72) / series_count)
    bar_cluster_width = bar_width * series_count

    def project_y(value: float) -> float:
        return height - bottom_margin - ((value / max_value) * plot_height)

    draw.text((left_margin, 20), title, fill=(17, 17, 17), font=title_font)
    draw.line(
        [(left_margin, height - bottom_margin), (width - right_margin, height - bottom_margin)],
        fill=(68, 68, 68),
        width=2,
    )
    draw.line(
        [(left_margin, top_margin), (left_margin, height - bottom_margin)],
        fill=(68, 68, 68),
        width=2,
    )

    x_label_width, _ = _text_size(draw, body_font, x_label)
    draw.text(
        ((left_margin + (plot_width / 2)) - (x_label_width / 2), height - 34),
        x_label,
        fill=(51, 51, 51),
        font=body_font,
    )
    draw.text((18, top_margin + 8), y_label, fill=(51, 51, 51), font=body_font)

    tick_count = 5
    for tick_index in range(tick_count + 1):
        value = (max_value * tick_index) / tick_count
        y_pos = project_y(value)
        draw.line([(left_margin - 6, y_pos), (left_margin, y_pos)], fill=(102, 102, 102), width=1)
        draw.line(
            [(left_margin, y_pos), (width - right_margin, y_pos)],
            fill=(230, 230, 230),
            width=1,
        )
        tick_label = f"{value:.0f}%" if percent_scale else (f"{value:.1f}" if max_value <= 12 else f"{value:.0f}")
        label_width, label_height = _text_size(draw, body_font, tick_label)
        draw.text(
            (left_margin - 10 - label_width, y_pos - (label_height / 2)),
            tick_label,
            fill=(85, 85, 85),
            font=body_font,
        )

    for category_index, category in enumerate(categories):
        group_center_x = left_margin + (group_span * category_index) + (group_span / 2)
        group_start_x = group_center_x - (bar_cluster_width / 2)
        tick_x = group_center_x
        draw.line(
            [(tick_x, height - bottom_margin), (tick_x, height - bottom_margin + 6)],
            fill=(102, 102, 102),
            width=1,
        )
        label_lines = _wrap_label(category)
        for line_index, line in enumerate(label_lines):
            line_width, _ = _text_size(draw, body_font, line)
            draw.text(
                (group_center_x - (line_width / 2), height - bottom_margin + 12 + (line_index * 12)),
                line,
                fill=(85, 85, 85),
                font=body_font,
            )

        for series_index, (series_name, values) in enumerate(series.items()):
            if category_index >= len(values):
                continue
            color = hex_to_rgb(colors[series_index % len(colors)])
            bar_value = scale_value(values[category_index])
            x0 = group_start_x + (series_index * bar_width)
            x1 = x0 + bar_width - 6
            y0 = project_y(bar_value)
            y1 = height - bottom_margin
            draw.rectangle((x0, y0, x1, y1), fill=color)

            if error_ranges and series_name in error_ranges and category_index < len(error_ranges[series_name]):
                low, high = error_ranges[series_name][category_index]
                low_y = project_y(scale_value(low))
                high_y = project_y(scale_value(high))
                center_x = (x0 + x1) / 2
                draw.line((center_x, high_y, center_x, low_y), fill=(45, 45, 45), width=1)
                draw.line((center_x - 6, high_y, center_x + 6, high_y), fill=(45, 45, 45), width=1)
                draw.line((center_x - 6, low_y, center_x + 6, low_y), fill=(45, 45, 45), width=1)

            value_label = format_value(values[category_index])
            label_width, label_height = _text_size(draw, body_font, value_label)
            draw.text(
                (((x0 + x1) / 2) - (label_width / 2), y0 - label_height - 4),
                value_label,
                fill=(68, 68, 68),
                font=body_font,
            )

    for legend_index, series_name in enumerate(series):
        color = hex_to_rgb(colors[legend_index % len(colors)])
        label = _label_for(series_name, series_labels)
        legend_y = top_margin + 24 * legend_index
        draw.rectangle(
            (width - right_margin + 8, legend_y - 8, width - right_margin + 26, legend_y + 8),
            fill=color,
        )
        draw.text((width - right_margin + 36, legend_y - 6), label, fill=color, font=body_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
