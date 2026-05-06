from __future__ import annotations

import argparse
from difflib import unified_diff
import json
import os
from pathlib import Path
from typing import Any

from llm_grid_battle.behavioral_descriptors import behavioral_cell, behavioral_distance, behavioral_profile_label
from llm_grid_battle.code_fingerprints import code_similarity


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _discover_run_dirs(runs_root: Path, explicit: list[str] | None, pattern: str) -> list[Path]:
    if explicit:
        return [Path(item).resolve() for item in explicit]
    return sorted(path.resolve() for path in runs_root.glob(pattern) if path.is_dir())


def _score_margin(epoch: dict[str, Any], agent_name: str, opponent_name: str) -> float:
    return float(epoch["scores"][agent_name]) - float(epoch["scores"][opponent_name])


def _classify_case(*, novelty: float, descriptor_shift: float, score_delta: float, holdout_delta: float | None) -> str:
    if novelty >= 0.2 and descriptor_shift < 0.08 and score_delta <= 0 and (holdout_delta or 0.0) <= 0:
        return "likely_code_churn"
    if novelty >= 0.2 and descriptor_shift >= 0.16 and (score_delta > 0 or (holdout_delta or 0.0) > 0):
        return "candidate_behavioral_innovation"
    if novelty >= 0.15 and descriptor_shift >= 0.1:
        return "mixed_change"
    return "minor_adjustment"


def _diff_preview(previous_code: str, current_code: str, *, max_lines: int = 80) -> str:
    diff_lines = list(
        unified_diff(
            previous_code.splitlines(),
            current_code.splitlines(),
            fromfile="previous.py",
            tofile="current.py",
            lineterm="",
        )
    )
    if len(diff_lines) > max_lines:
        diff_lines = diff_lines[:max_lines] + ["... diff truncated ..."]
    return "\n".join(diff_lines)


def _top_descriptor_changes(previous: dict[str, float], current: dict[str, float], *, top_n: int = 5) -> list[str]:
    deltas = []
    keys = sorted(set(previous) | set(current))
    for key in keys:
        left = float(previous.get(key, 0.0))
        right = float(current.get(key, 0.0))
        delta = right - left
        deltas.append((abs(delta), key, left, right, delta))
    deltas.sort(reverse=True)
    return [
        f"{key}: {left:.4f} -> {right:.4f} ({delta:+.4f})"
        for _, key, left, right, delta in deltas[:top_n]
    ]


def _candidate_rows(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        for condition_summary_path in run_dir.rglob("condition_summary.json"):
            condition_dir = condition_summary_path.parent
            condition_summary = _load_json(condition_summary_path)
            curriculum = condition_summary.get("curriculum", {})
            learner = str(curriculum.get("focal_agent") or condition_summary["agents"][0]["name"])
            opponent = str(curriculum.get("opponent_agent") or condition_summary["agents"][1]["name"])
            epochs = condition_summary.get("epochs", [])
            for index in range(1, len(epochs)):
                previous = epochs[index - 1]
                current = epochs[index]
                previous_code = str(previous.get("submitted_codes", {}).get(learner, previous["codes"][learner]))
                current_code = str(current.get("submitted_codes", {}).get(learner, current["codes"][learner]))
                novelty = round(1.0 - code_similarity(previous_code, current_code), 4)
                previous_descriptor = previous.get("behavioral_descriptors", {}).get(learner, {})
                current_descriptor = current.get("behavioral_descriptors", {}).get(learner, {})
                descriptor_shift = behavioral_distance(previous_descriptor, current_descriptor)
                current_selection = (current.get("curriculum") or {}).get("selection") or {}
                holdout_summary = current_selection.get("holdout_summary") or {}
                holdout_delta = holdout_summary.get("mean_margin_delta_vs_incumbent")
                score_delta = float(current["scores"][learner]) - float(previous["scores"][learner])
                margin_delta = _score_margin(current, learner, opponent) - _score_margin(previous, learner, opponent)
                row = {
                    "run_name": run_dir.name,
                    "run_dir": str(run_dir),
                    "condition_name": str(condition_summary["condition_name"]),
                    "environment_name": str(current.get("environment", {}).get("name", "resource_collection")),
                    "epoch_index": int(current["epoch_index"]),
                    "learner_agent": learner,
                    "opponent_agent": opponent,
                    "code_novelty": novelty,
                    "descriptor_shift": round(descriptor_shift, 4),
                    "previous_profile": behavioral_profile_label(previous_descriptor),
                    "current_profile": behavioral_profile_label(current_descriptor),
                    "previous_cell": behavioral_cell(previous_descriptor),
                    "current_cell": behavioral_cell(current_descriptor),
                    "score_delta": round(score_delta, 4),
                    "margin_delta": round(margin_delta, 4),
                    "holdout_margin_delta_vs_incumbent": round(float(holdout_delta), 4) if holdout_delta is not None else None,
                    "classification": _classify_case(
                        novelty=novelty,
                        descriptor_shift=descriptor_shift,
                        score_delta=score_delta,
                        holdout_delta=float(holdout_delta) if holdout_delta is not None else None,
                    ),
                    "descriptor_changes": _top_descriptor_changes(previous_descriptor, current_descriptor),
                    "diff_preview": _diff_preview(previous_code, current_code),
                    "previous_map": str((condition_dir / "epochs" / f"epoch_{int(previous['epoch_index']):03d}" / "map.svg").resolve()),
                    "current_map": str((condition_dir / "epochs" / f"epoch_{int(current['epoch_index']):03d}" / "map.svg").resolve()),
                    "current_artifact": str((condition_dir / "epochs" / f"epoch_{int(current['epoch_index']):03d}" / "artifact.json").resolve()),
                }
                rows.append(row)
    rows.sort(
        key=lambda item: (
            float(item["code_novelty"]),
            float(item["descriptor_shift"]),
            float(item["holdout_margin_delta_vs_incumbent"] or 0.0),
            float(item["score_delta"]),
        ),
        reverse=True,
    )
    return rows


def _relative_path(target: str, base_dir: Path) -> str:
    return Path(os.path.relpath(Path(target), start=base_dir)).as_posix()


def _render_markdown(rows: list[dict[str, Any]], *, output_dir: Path) -> str:
    lines = [
        "# Novelty Spike Review",
        "",
        "This packet is intended for manual validation of the strongest code-novelty spikes.",
        "Each case connects code change, behavioral descriptor change, trajectory change, and score / holdout effect.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['condition_name']} / epoch {row['epoch_index']} / {row['run_name']}",
                f"- Environment: `{row['environment_name']}`.",
                f"- Learner: `{row['learner_agent']}` vs opponent role `{row['opponent_agent']}`.",
                f"- Code novelty: {row['code_novelty']}.",
                f"- Behavioral descriptor shift: {row['descriptor_shift']}.",
                f"- Behavior profile: `{row['previous_profile']}` -> `{row['current_profile']}`.",
                f"- Behavior cell: `{row['previous_cell']}` -> `{row['current_cell']}`.",
                f"- Score delta: {row['score_delta']:+.4f}.",
                f"- Margin delta: {row['margin_delta']:+.4f}.",
                f"- Holdout margin delta vs incumbent: {row['holdout_margin_delta_vs_incumbent'] if row['holdout_margin_delta_vs_incumbent'] is not None else 'N/A'}.",
                f"- Preliminary interpretation: `{row['classification']}`.",
                "- Strongest descriptor changes:",
                *[f"  - {item}" for item in row["descriptor_changes"]],
                "",
                "### Code Diff Preview",
                "```diff",
                row["diff_preview"],
                "```",
                "",
                "### Trajectory Artifacts",
                f"- Previous trajectory: ![previous map]({_relative_path(row['previous_map'], output_dir)})",
                f"- Current trajectory: ![current map]({_relative_path(row['current_map'], output_dir)})",
                f"- Full artifact: `{_relative_path(row['current_artifact'], output_dir)}`",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a manual novelty-validation packet from run artifacts.")
    parser.add_argument("--runs-root", default="runs", help="Root directory containing run_* folders.")
    parser.add_argument("--run-dir", action="append", default=None, help="Explicit run directory to include. Repeatable.")
    parser.add_argument("--pattern", default="run_*", help="Glob used under --runs-root when --run-dir is omitted.")
    parser.add_argument("--top-k", type=int, default=10, help="Number of novelty-spike epochs to include.")
    parser.add_argument("--output-dir", required=True, help="Directory where the review packet should be written.")
    args = parser.parse_args()

    run_dirs = _discover_run_dirs(Path(args.runs_root), args.run_dir, args.pattern)
    rows = _candidate_rows(run_dirs)[: max(1, int(args.top_k))]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "novelty_review.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (output_dir / "novelty_review.md").write_text(_render_markdown(rows, output_dir=output_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
