from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.analysis import render_markdown_report
from llm_grid_battle.llm import judge_text, load_env_files
from run_suite import build_judge_prompt


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_latest_run_dir(project_root: Path) -> Path:
    runs_root = project_root / "runs"
    if not runs_root.exists():
        raise FileNotFoundError(f"Runs directory not found: {runs_root}")

    run_dirs = [item for item in runs_root.iterdir() if item.is_dir() and item.name.startswith("run_")]
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found under: {runs_root}")

    # run_YYYYMMDD_HHMMSS is lexicographically sortable by timestamp.
    return sorted(run_dirs, key=lambda p: p.name)[-1]


def _load_judge_config_from_run(run_dir: Path) -> dict[str, Any]:
    condition_dirs = sorted(
        item for item in run_dir.iterdir() if item.is_dir() and (item / "condition_config.json").exists()
    )
    if not condition_dirs:
        raise FileNotFoundError(
            f"No condition_config.json found in condition folders under: {run_dir}"
        )

    condition_config = _load_json(condition_dirs[0] / "condition_config.json")
    judge = condition_config.get("judge")
    if not isinstance(judge, dict):
        raise ValueError(f"Judge config missing in: {condition_dirs[0] / 'condition_config.json'}")
    return judge


def rerun_judge_for_latest_run(project_root: Path, run_dir: Path | None = None) -> Path:
    load_env_files(project_root)

    target_run_dir = run_dir if run_dir is not None else _find_latest_run_dir(project_root)
    suite_summary_path = target_run_dir / "suite_summary.json"
    if not suite_summary_path.exists():
        raise FileNotFoundError(f"Missing suite summary: {suite_summary_path}")

    suite_summary = _load_json(suite_summary_path)
    judge_config = _load_judge_config_from_run(target_run_dir)

    llm_report = judge_text(
        provider=str(judge_config.get("provider", "openai")),
        model=str(judge_config.get("model", "gpt-5-nano")),
        system_prompt="You are a careful research assistant. Answer in concise markdown.",
        user_prompt=build_judge_prompt(suite_summary),
        temperature=float(judge_config.get("temperature", 0.1)),
        max_tokens=int(judge_config.get("max_tokens", 1800)),
        timeout=float(judge_config.get("timeout_seconds", 300.0))
    )

    report = render_markdown_report(suite_summary, llm_report)
    report_path = target_run_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate report.md for the latest run (or a specific run) by rerunning judge only."
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Optional path to a specific run directory. If omitted, uses latest runs/run_*.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    run_dir = Path(args.run_dir).resolve() if args.run_dir else None

    report_path = rerun_judge_for_latest_run(project_root, run_dir)
    print(f"Regenerated report: {report_path}")


if __name__ == "__main__":
    main()
