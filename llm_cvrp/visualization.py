from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def write_metric_plot_svg(
    *,
    path: Path,
    title: str,
    series: dict[str, list[float]],
    y_label: str,
    series_labels: dict[str, str] | None = None,
) -> None:
    width = 980
    height = 420
    left_margin = 72
    right_margin = 260
    top_margin = 68
    bottom_margin = 72
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#8c564b"]
    values = [point for line in series.values() for point in line]
    max_value = max(values) if values else 1.0
    scale_max = max(max_value, 1.0)
    x_count = max((len(line) for line in series.values()), default=1)

    def project_x(index: int) -> float:
        return left_margin + (index / max(1, x_count - 1)) * (width - left_margin - right_margin)

    def project_y(value: float) -> float:
        return height - bottom_margin - (value / scale_max) * (height - top_margin - bottom_margin)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left_margin}" y="34" font-family="Arial" font-size="22" font-weight="bold" fill="#111111">{escape(title)}</text>',
        f'<line x1="{left_margin}" y1="{height - bottom_margin}" x2="{width - right_margin}" y2="{height - bottom_margin}" stroke="#444444"/>',
        f'<line x1="{left_margin}" y1="{top_margin}" x2="{left_margin}" y2="{height - bottom_margin}" stroke="#444444"/>',
        f'<text x="{left_margin + (width - left_margin - right_margin) / 2}" y="{height - 20}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333333">Epoch</text>',
        f'<text x="24" y="{top_margin + (height - top_margin - bottom_margin) / 2}" font-family="Arial" font-size="14" fill="#333333" transform="rotate(-90 24 {top_margin + (height - top_margin - bottom_margin) / 2})">{escape(y_label)}</text>',
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
        value = (scale_max * tick_index) / y_tick_count
        y_pos = project_y(value)
        label = f"{value:.3f}" if scale_max <= 1.0 else f"{value:.2f}"
        parts.extend(
            [
                f'<line x1="{left_margin - 6}" y1="{y_pos}" x2="{left_margin}" y2="{y_pos}" stroke="#666666"/>',
                f'<line x1="{left_margin}" y1="{y_pos}" x2="{width - right_margin}" y2="{y_pos}" stroke="#e6e6e6"/>',
                f'<text x="{left_margin - 10}" y="{y_pos + 4}" text-anchor="end" font-family="Arial" font-size="12" fill="#555555">{label}</text>',
            ]
        )

    for index, (name, line) in enumerate(series.items()):
        if not line:
            continue
        color = colors[index % len(colors)]
        coords = [f"{project_x(i)},{project_y(value)}" for i, value in enumerate(line)]
        parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        legend_y = top_margin + 24 * index
        label = series_labels.get(name, name) if series_labels else name
        parts.extend(
            [
                f'<line x1="{width - right_margin + 8}" y1="{legend_y}" x2="{width - right_margin + 30}" y2="{legend_y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>',
                f'<text x="{width - right_margin + 40}" y="{legend_y + 5}" font-family="Arial" font-size="14" fill="{color}">{escape(label)}</text>',
            ]
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_metric_plot_png(
    *,
    path: Path,
    title: str,
    series: dict[str, list[float]],
    y_label: str,
    series_labels: dict[str, str] | None = None,
) -> None:
    width = 980
    height = 420
    left_margin = 72
    right_margin = 300
    top_margin = 68
    bottom_margin = 72
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#8c564b"]
    values = [point for line in series.values() for point in line]
    max_value = max(values) if values else 1.0
    scale_max = max(max_value, 1.0)
    x_count = max((len(line) for line in series.values()), default=1)

    def project_x(index: int) -> float:
        return left_margin + (index / max(1, x_count - 1)) * (width - left_margin - right_margin)

    def project_y(value: float) -> float:
        return height - bottom_margin - (value / scale_max) * (height - top_margin - bottom_margin)

    def hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return tuple(int(color[idx : idx + 2], 16) for idx in (0, 2, 4))

    def text_size(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
        box = draw.textbbox((0, 0), text, font=font)
        return box[2] - box[0], box[3] - box[1]

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    draw.text((left_margin, 20), title, fill=(17, 17, 17), font=title_font)
    draw.line([(left_margin, height - bottom_margin), (width - right_margin, height - bottom_margin)], fill=(68, 68, 68), width=2)
    draw.line([(left_margin, top_margin), (left_margin, height - bottom_margin)], fill=(68, 68, 68), width=2)
    x_label = "Epoch"
    x_width, _ = text_size(draw, body_font, x_label)
    draw.text(((left_margin + (width - left_margin - right_margin) / 2) - (x_width / 2), height - 34), x_label, fill=(51, 51, 51), font=body_font)
    draw.text((18, top_margin + 8), y_label, fill=(51, 51, 51), font=body_font)

    tick_count = min(6, max(2, x_count))
    x_tick_indexes = sorted({round(index * max(0, x_count - 1) / max(1, tick_count - 1)) for index in range(tick_count)})
    for tick_index in x_tick_indexes:
        x_pos = project_x(tick_index)
        draw.line([(x_pos, height - bottom_margin), (x_pos, height - bottom_margin + 6)], fill=(102, 102, 102), width=1)
        tick = str(tick_index + 1)
        tick_width, _ = text_size(draw, body_font, tick)
        draw.text((x_pos - (tick_width / 2), height - bottom_margin + 10), tick, fill=(85, 85, 85), font=body_font)

    y_tick_count = 5
    for tick_index in range(y_tick_count + 1):
        value = (scale_max * tick_index) / y_tick_count
        y_pos = project_y(value)
        draw.line([(left_margin - 6, y_pos), (left_margin, y_pos)], fill=(102, 102, 102), width=1)
        draw.line([(left_margin, y_pos), (width - right_margin, y_pos)], fill=(230, 230, 230), width=1)
        label = f"{value:.3f}" if scale_max <= 1.0 else f"{value:.2f}"
        label_width, label_height = text_size(draw, body_font, label)
        draw.text((left_margin - 10 - label_width, y_pos - (label_height / 2)), label, fill=(85, 85, 85), font=body_font)

    for index, (name, line) in enumerate(series.items()):
        if not line:
            continue
        color = hex_to_rgb(colors[index % len(colors)])
        points = [(project_x(i), project_y(value)) for i, value in enumerate(line)]
        draw.line(points, fill=color, width=3)
        for x_pos, y_pos in points:
            draw.ellipse((x_pos - 2, y_pos - 2, x_pos + 2, y_pos + 2), fill=color)
        legend_y = top_margin + 24 * index
        label = series_labels.get(name, name) if series_labels else name
        draw.line([(width - right_margin + 8, legend_y), (width - right_margin + 30, legend_y)], fill=color, width=4)
        draw.text((width - right_margin + 40, legend_y - 6), label, fill=color, font=body_font)
    image.save(path)
