from __future__ import annotations

from pathlib import Path


def _svg_header(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'


def write_epoch_map_svg(
    *,
    path: Path,
    width: int,
    height: int,
    initial_resources: list[list[int]],
    obstacles: list[list[int]],
    paths: dict[str, list[list[int]]],
) -> None:
    cell = 42
    margin = 28
    svg_width = width * cell + margin * 2
    svg_height = height * cell + margin * 2
    colors = {"agent_a": "#1f77b4", "agent_b": "#d62728"}

    parts = [_svg_header(svg_width, svg_height), '<rect width="100%" height="100%" fill="#ffffff"/>']
    for y in range(height):
        for x in range(width):
            rx = margin + x * cell
            ry = margin + y * cell
            parts.append(f'<rect x="{rx}" y="{ry}" width="{cell}" height="{cell}" fill="#fafafa" stroke="#d6d6d6"/>')

    for x, y in obstacles:
        rx = margin + x * cell
        ry = margin + y * cell
        parts.append(f'<rect x="{rx + 4}" y="{ry + 4}" width="{cell - 8}" height="{cell - 8}" fill="#6c757d"/>')

    for x, y in initial_resources:
        cx = margin + x * cell + cell / 2
        cy = margin + y * cell + cell / 2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{cell / 6}" fill="#2ca02c" opacity="0.65"/>')

    for name, points in paths.items():
        if not points:
            continue
        coords = []
        for x, y in points:
            coords.append(f"{margin + x * cell + cell / 2},{margin + y * cell + cell / 2}")
        parts.append(
            f'<polyline points="{" ".join(coords)}" fill="none" stroke="{colors.get(name, "#000000")}" '
            'stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
        )
        sx, sy = points[0]
        ex, ey = points[-1]
        parts.append(
            f'<circle cx="{margin + sx * cell + cell / 2}" cy="{margin + sy * cell + cell / 2}" r="{cell / 5}" fill="{colors.get(name, "#000000")}"/>'
        )
        parts.append(
            f'<circle cx="{margin + ex * cell + cell / 2}" cy="{margin + ey * cell + cell / 2}" r="{cell / 4.5}" fill="{colors.get(name, "#000000")}" opacity="0.45"/>'
        )

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_score_plot_svg(*, path: Path, title: str, series: dict[str, list[float]]) -> None:
    width = 780
    height = 360
    margin = 48
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    values = [point for line in series.values() for point in line]
    max_value = max(values) if values else 1.0
    x_count = max((len(line) for line in series.values()), default=1)

    def project_x(index: int) -> float:
        return margin + (index / max(1, x_count - 1)) * (width - margin * 2)

    def project_y(value: float) -> float:
        return height - margin - (value / max_value) * (height - margin * 2)

    parts = [
        _svg_header(width, height),
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin}" y="28" font-family="Arial" font-size="20" fill="#111111">{title}</text>',
        f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#444444"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#444444"/>',
    ]

    for idx, (name, line) in enumerate(series.items()):
        if not line:
            continue
        coords = [f"{project_x(i)},{project_y(value)}" for i, value in enumerate(line)]
        color = colors[idx % len(colors)]
        parts.append(
            f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
        )
        parts.append(
            f'<text x="{width - margin - 180}" y="{margin + 22 * idx}" font-family="Arial" font-size="14" fill="{color}">{name}</text>'
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")

