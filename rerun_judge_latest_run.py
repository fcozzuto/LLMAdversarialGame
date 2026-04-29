from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.analysis import render_markdown_report
from llm_grid_battle.llm import judge_text, load_env_files
from llm_grid_battle.pdf_report import write_pdf_report
from llm_grid_battle.visualization import write_score_plot_png, write_score_plot_svg
from run_suite import build_judge_prompt


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_or_infer_run_metadata(run_dir: Path) -> dict[str, Any] | None:
    metadata_path = run_dir / "run_metadata.json"
    if metadata_path.exists():
        return _load_json(metadata_path)

    started_at = None
    if run_dir.name.startswith("run_"):
        suffix = run_dir.name.removeprefix("run_")
        try:
            started_at = datetime.strptime(suffix, "%Y%m%d_%H%M%S")
        except ValueError:
            started_at = None

    finished_source = run_dir / "report.md"
    if not finished_source.exists():
        finished_source = run_dir / "suite_summary.json"
    if not finished_source.exists():
        return None
    finished_at = datetime.fromtimestamp(finished_source.stat().st_mtime)

    if started_at is None:
        duration_hhmm = "-"
        started_value = "-"
    else:
        total_seconds = max(0.0, (finished_at - started_at).total_seconds())
        minutes = int(round(total_seconds / 60.0))
        hours, remainder = divmod(minutes, 60)
        duration_hhmm = f"{hours:02d}:{remainder:02d}"
        started_value = started_at.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "run_name": run_dir.name,
        "started_at_local": started_value,
        "finished_at_local": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_hhmm": duration_hhmm,
    }


def _agent_label(agent: dict[str, Any]) -> str:
    return f"{agent['name']} ({agent['provider']}:{agent['model']})"


def _regenerate_score_charts(run_dir: Path, condition_payloads: list[dict[str, Any]]) -> None:
    for payload in condition_payloads:
        condition_name = str(payload["condition_name"])
        agents = payload.get("agents", [])
        series: dict[str, list[float]] = {str(agent["name"]): [] for agent in agents}
        for epoch in payload.get("epochs", []):
            scores = epoch.get("scores", {})
            for agent_name in list(series):
                series[agent_name].append(float(scores.get(agent_name, 0.0)))
        labels = {str(agent["name"]): _agent_label(agent) for agent in agents}
        condition_dir = run_dir / condition_name
        write_score_plot_svg(
            path=condition_dir / "scores.svg",
            title=f"{condition_name} scores",
            series=series,
            series_labels=labels,
        )
        write_score_plot_png(
            path=condition_dir / "scores.png",
            title=f"{condition_name} scores",
            series=series,
            series_labels=labels,
        )


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


def _persist_judge_config_to_run(run_dir: Path, judge_config: dict[str, Any]) -> None:
    condition_config_paths = sorted(run_dir.glob("*/condition_config.json"))
    for config_path in condition_config_paths:
        condition_config = _load_json(config_path)
        judge = condition_config.get("judge")
        if not isinstance(judge, dict):
            continue
        judge["provider"] = str(judge_config.get("provider", judge.get("provider", "openai")))
        judge["model"] = str(judge_config.get("model", judge.get("model", "gpt-4.1-mini")))
        condition_config["judge"] = judge
        config_path.write_text(
            json.dumps(condition_config, indent=2),
            encoding="utf-8",
        )


def rerun_judge_for_latest_run(
    project_root: Path,
    run_dir: Path | None = None,
    *,
    judge_provider_override: str | None = None,
    judge_model_override: str | None = None,
) -> Path:
    load_env_files(project_root)

    target_run_dir = run_dir if run_dir is not None else _find_latest_run_dir(project_root)
    suite_summary_path = target_run_dir / "suite_summary.json"
    if not suite_summary_path.exists():
        raise FileNotFoundError(f"Missing suite summary: {suite_summary_path}")

    suite_summary = _load_json(suite_summary_path)
    judge_config = _load_judge_config_from_run(target_run_dir)
    if judge_provider_override:
        judge_config["provider"] = judge_provider_override
    if judge_model_override:
        judge_config["model"] = judge_model_override
    _persist_judge_config_to_run(target_run_dir, judge_config)
    run_metadata = _load_or_infer_run_metadata(target_run_dir)
    if run_metadata is None:
        run_metadata = {"run_name": target_run_dir.name}
    run_metadata["judge_status"] = "enabled"
    run_metadata["judge_provider"] = str(judge_config.get("provider", "openai"))
    run_metadata["judge_model"] = str(judge_config.get("model", "gpt-4.1-mini"))

    llm_report = judge_text(
        provider=str(judge_config.get("provider", "openai")),
        model=str(judge_config.get("model", "gpt-4.1-mini")),
        system_prompt="You are a careful research assistant. Answer in concise markdown.",
        user_prompt=build_judge_prompt(suite_summary),
        temperature=float(judge_config.get("temperature", 0.1)),
        max_tokens=int(judge_config.get("max_tokens", 1800)),
        timeout=float(judge_config.get("timeout_seconds", 300.0))
    )

    report = render_markdown_report(suite_summary, llm_report, run_metadata=run_metadata)
    report_path = target_run_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    (target_run_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    condition_payloads = [
        _load_json(path)
        for path in sorted(target_run_dir.glob("*/condition_summary.json"))
    ]
    _regenerate_score_charts(target_run_dir, condition_payloads)
    write_pdf_report(
        path=target_run_dir / "report.pdf",
        run_name=target_run_dir.name,
        markdown_report=report,
        suite_summary=suite_summary,
        condition_payloads=condition_payloads,
    )
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
    parser.add_argument(
        "--judge-provider",
        default=None,
        help="Optional provider override for rerunning the judge on an existing run.",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Optional model override for rerunning the judge on an existing run.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    run_dir = Path(args.run_dir).resolve() if args.run_dir else None

    report_path = rerun_judge_for_latest_run(
        project_root,
        run_dir,
        judge_provider_override=args.judge_provider,
        judge_model_override=args.judge_model,
    )
    print(f"Regenerated report: {report_path}")


if __name__ == "__main__":
    main()
