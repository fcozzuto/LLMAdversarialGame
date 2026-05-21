from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from llm_grid_battle.pdf_report import write_pdf_report
from llm_cvrp.benchmark import CVRPInstance, load_benchmark_bundle
from llm_cvrp.code_features import code_similarity, complexity_score, fingerprint_record
from llm_cvrp.llm import judge_text, load_env_files
from llm_cvrp.visualization import write_metric_plot_png, write_metric_plot_svg
from llm_cvrp_phase9.analysis import render_markdown_report, summarize_suite
from llm_cvrp_phase9.baselines import baseline_solver, baseline_specs
from llm_cvrp_phase9.config import Phase9ConditionConfig, Phase9SuiteConfig
from llm_cvrp_phase9.features import describe_instance, instance_payload
from llm_cvrp_phase9.llm import default_solver_code, generate_code
from llm_cvrp_phase9.prompting import build_generation_prompt
from llm_cvrp_phase9.sandbox import run_solver
from llm_cvrp_phase9.validation import summarize_panel, validate_solution


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _format_duration_hhmm(total_seconds: float) -> str:
    minutes = int(round(total_seconds / 60.0))
    hours, remainder = divmod(minutes, 60)
    return f"{hours:02d}:{remainder:02d}"


def _load_instances(manifest_path: str | Path, *, train_limit: int, holdout_limit: int) -> tuple[list[CVRPInstance], list[CVRPInstance], dict[str, Any]]:
    raw = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    bundle = load_benchmark_bundle(manifest_path)
    train = bundle.train[:train_limit] if train_limit > 0 else bundle.train
    holdout = bundle.holdout[:holdout_limit] if holdout_limit > 0 else bundle.holdout
    if not train or not holdout:
        raise ValueError("Phase-9 benchmark manifest must provide both train and holdout instances.")
    return train, holdout, raw


def _instance_summaries(instances: list[CVRPInstance]) -> list[dict[str, Any]]:
    rows = []
    for instance in instances:
        descriptors = describe_instance(instance)
        rows.append(
            {
                "name": instance.name,
                "customer_count": descriptors["customer_count"],
                "vehicle_count_hint": descriptors["vehicle_count_hint"],
                "demand_pressure": descriptors["demand_pressure"],
                "structure_class": descriptors["structure_class"],
                "corridor_score": descriptors["corridor_score"],
                "clusteredness_score": descriptors["clusteredness_score"],
                "nearest_neighbor_trap_score": descriptors["nearest_neighbor_trap_score"],
            }
        )
    return rows


def _baseline_train_summaries(train_instances: list[CVRPInstance], config: Phase9ConditionConfig) -> list[dict[str, Any]]:
    rows = []
    for index, spec in enumerate(baseline_specs()):
        solver = baseline_solver(spec["name"])
        results = _evaluate_baseline_panel(
            solver,
            train_instances,
            config,
            seed_base=config.seed + (index * 1000),
        )
        summary = summarize_panel(results, panel_name="train")
        rows.append(
            {
                "baseline_name": spec["name"],
                "description": spec["description"],
                "feasibility_rate": summary["feasibility_rate"],
                "mean_penalized_gap": summary["mean_penalized_gap"],
                "mean_feasible_gap": summary["mean_feasible_gap"],
            }
        )
    return rows


def _best_builtin_baseline(train_instances: list[CVRPInstance], holdout_instances: list[CVRPInstance], config: Phase9ConditionConfig) -> tuple[str, dict[str, Any], dict[str, Any]]:
    best_name = None
    best_train_summary = None
    best_holdout_summary = None
    for index, spec in enumerate(baseline_specs()):
        solver = baseline_solver(spec["name"])
        train_results = _evaluate_baseline_panel(
            solver,
            train_instances,
            config,
            seed_base=config.seed + (index * 1000),
        )
        train_summary = summarize_panel(train_results, panel_name="train")
        holdout_results = _evaluate_baseline_panel(
            solver,
            holdout_instances,
            config,
            seed_base=config.seed + 50_000 + (index * 1000),
        )
        holdout_summary = summarize_panel(holdout_results, panel_name="holdout")
        score = (
            -float(train_summary["feasibility_rate"]),
            float(train_summary["mean_penalized_gap"]),
            float(train_summary["mean_runtime_ms"]),
        )
        if best_train_summary is None or score < (
            -float(best_train_summary["feasibility_rate"]),
            float(best_train_summary["mean_penalized_gap"]),
            float(best_train_summary["mean_runtime_ms"]),
        ):
            best_name = spec["name"]
            best_train_summary = train_summary
            best_holdout_summary = holdout_summary
    assert best_name is not None and best_train_summary is not None and best_holdout_summary is not None
    return best_name, best_train_summary, best_holdout_summary


def _evaluate_code_panel(code: str, instances: list[CVRPInstance], config: Phase9ConditionConfig) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for instance_index, instance in enumerate(instances):
        payload = instance_payload(instance)
        run_result = run_solver(
            code,
            payload,
            timeout_seconds=float(config.generation.solver_timeout_seconds),
        )
        if not run_result["ok"]:
            validation = validate_solution(
                instance,
                [],
                enforce_vehicle_count=bool(config.benchmark.enforce_vehicle_count),
                infeasible_gap_penalty=float(config.benchmark.infeasible_gap_penalty),
            )
            validation.errors.insert(0, str(run_result.get("error") or "solver execution failed"))
            results.append(
                {
                    "instance_name": instance.name,
                    "runtime_ms": float(run_result["runtime_ms"]),
                    "validation": validation.to_dict(),
                    "descriptors": payload["descriptors"],
                }
            )
            continue
        validation = validate_solution(
            instance,
            run_result["routes"],
            enforce_vehicle_count=bool(config.benchmark.enforce_vehicle_count),
            infeasible_gap_penalty=float(config.benchmark.infeasible_gap_penalty),
        )
        results.append(
            {
                "instance_name": instance.name,
                "runtime_ms": float(run_result["runtime_ms"]),
                "validation": validation.to_dict(),
                "descriptors": payload["descriptors"],
            }
        )
    return results


def _evaluate_baseline_panel(
    solver: Callable[[CVRPInstance, int], dict[str, Any]],
    instances: list[CVRPInstance],
    config: Phase9ConditionConfig,
    *,
    seed_base: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for instance_index, instance in enumerate(instances):
        started = perf_counter()
        output = solver(instance, seed_base + instance_index)
        runtime_ms = round((perf_counter() - started) * 1000.0, 6)
        validation = validate_solution(
            instance,
            output["routes"],
            enforce_vehicle_count=bool(config.benchmark.enforce_vehicle_count),
            infeasible_gap_penalty=float(config.benchmark.infeasible_gap_penalty),
        )
        results.append(
            {
                "instance_name": instance.name,
                "runtime_ms": runtime_ms,
                "validation": validation.to_dict(),
                "descriptors": describe_instance(instance),
                "solver_metadata": dict(output.get("solver_metadata", {})),
            }
        )
    return results


def _baseline_condition_payload(config: Phase9ConditionConfig, condition_dir: Path, *, solver_name: str) -> dict[str, Any]:
    train_instances, holdout_instances, _manifest = _load_instances(
        config.benchmark.manifest_path,
        train_limit=int(config.benchmark.train_instance_limit),
        holdout_limit=int(config.benchmark.holdout_instance_limit),
    )
    solver = baseline_solver(solver_name)
    train_results = _evaluate_baseline_panel(solver, train_instances, config, seed_base=config.seed)
    holdout_results = _evaluate_baseline_panel(solver, holdout_instances, config, seed_base=config.seed + 50_000)
    train_summary = summarize_panel(train_results, panel_name="train")
    holdout_summary = summarize_panel(holdout_results, panel_name="holdout")
    payload = {
        "condition_name": config.name,
        "execution_mode": config.execution.mode,
        "skipped": False,
        "epochs": [],
        "final_code": "",
        "final_evaluation": {
            "train": train_summary,
            "holdout": holdout_summary,
        },
        "baseline_name": solver_name,
    }
    _json_dump(condition_dir / "condition_summary.json", payload)
    return payload


def _epoch_score(summary: dict[str, Any]) -> tuple[float, float, float]:
    return (
        -float(summary["feasibility_rate"]),
        float(summary["mean_penalized_gap"]),
        float(summary["mean_runtime_ms"]),
    )


def _evolution_condition_payload(config: Phase9ConditionConfig, condition_dir: Path) -> dict[str, Any]:
    train_instances, holdout_instances, _manifest = _load_instances(
        config.benchmark.manifest_path,
        train_limit=int(config.benchmark.train_instance_limit),
        holdout_limit=int(config.benchmark.holdout_instance_limit),
    )
    train_instance_summaries = _instance_summaries(train_instances)
    baseline_summaries = _baseline_train_summaries(train_instances, config)
    incumbent_code = default_solver_code()
    incumbent_train_results = _evaluate_code_panel(incumbent_code, train_instances, config)
    incumbent_train_summary = summarize_panel(incumbent_train_results, panel_name="train")
    accepted_codes = [incumbent_code]
    epochs_payload: list[dict[str, Any]] = []

    for epoch_index in range(1, int(config.optimization.epochs) + 1):
        prompt_context = {
            "train_instance_summaries": train_instance_summaries,
            "baseline_summaries": baseline_summaries,
            "incumbent_summary": incumbent_train_summary,
            "incumbent_code": incumbent_code,
            "worst_cases": incumbent_train_summary.get("worst_instances", []),
        }
        generation_result = generate_code(
            provider=config.agent.provider,
            model=config.agent.model,
            system_prompt=config.agent.system_prompt,
            user_prompt=build_generation_prompt(
                context=prompt_context,
                max_non_empty_lines=int(config.generation.max_non_empty_lines),
                max_characters=int(config.generation.max_characters),
            ),
            temperature=float(config.agent.temperature),
            max_tokens=int(config.agent.max_tokens),
            repair_invalid_submissions=bool(config.generation.repair_invalid_submissions),
            timeout=float(config.generation.llm_timeout_seconds),
            max_non_empty_lines=int(config.generation.max_non_empty_lines),
            max_characters=int(config.generation.max_characters),
        )
        candidate_train_results = _evaluate_code_panel(generation_result.code, train_instances, config)
        candidate_train_summary = summarize_panel(candidate_train_results, panel_name="train")
        candidate_score = _epoch_score(candidate_train_summary)
        incumbent_score = _epoch_score(incumbent_train_summary)
        generation_valid = generation_result.error is None and not bool(generation_result.used_fallback)
        accepted = False
        if generation_valid:
            accepted = candidate_score < incumbent_score or (
                abs(candidate_score[1] - incumbent_score[1]) <= float(config.optimization.acceptance_tolerance)
                and candidate_score[0] < incumbent_score[0]
            )
        if accepted:
            incumbent_code = generation_result.code
            incumbent_train_results = candidate_train_results
            incumbent_train_summary = candidate_train_summary
            accepted_codes.append(incumbent_code)
        epoch_payload = {
            "epoch_index": epoch_index,
            "accepted": bool(accepted),
            "generation_error": generation_result.error,
            "generation_fallback_used": bool(generation_result.used_fallback),
            "generation_valid_for_acceptance": bool(generation_valid),
            "repair_attempted": bool(generation_result.repair_attempted),
            "salvage_attempted": bool(generation_result.salvage_attempted),
            "validation_issues": list(generation_result.validation_issues),
            "raw_text": generation_result.raw_text,
            "submitted_code": generation_result.submitted_code,
            "executed_code": generation_result.code,
            "candidate_train_summary": candidate_train_summary,
            "code_novelty": round(1.0 - code_similarity(accepted_codes[-2] if len(accepted_codes) >= 2 else default_solver_code(), generation_result.code), 6)
            if accepted_codes
            else 0.0,
            "complexity": round(complexity_score(generation_result.code), 6),
            "fingerprint": fingerprint_record(generation_result.code),
        }
        epochs_payload.append(epoch_payload)
        epoch_dir = condition_dir / "epochs" / f"epoch_{epoch_index:03d}"
        epoch_dir.mkdir(parents=True, exist_ok=True)
        _json_dump(epoch_dir / "artifact.json", epoch_payload)

    holdout_results = _evaluate_code_panel(incumbent_code, holdout_instances, config)
    payload = {
        "condition_name": config.name,
        "execution_mode": config.execution.mode,
        "skipped": False,
        "epochs": epochs_payload,
        "final_code": incumbent_code,
        "final_evaluation": {
            "train": incumbent_train_summary,
            "holdout": summarize_panel(holdout_results, panel_name="holdout"),
        },
    }
    _json_dump(condition_dir / "condition_summary.json", payload)

    training_penalized_gap = [float(epoch["candidate_train_summary"]["mean_penalized_gap"]) for epoch in epochs_payload]
    training_feasibility = [float(epoch["candidate_train_summary"]["feasibility_rate"]) for epoch in epochs_payload]
    write_metric_plot_svg(
        path=condition_dir / "training_gap.svg",
        title=f"{config.name} training penalized gap",
        series={"train_penalized_gap": training_penalized_gap},
        y_label="penalized gap",
        series_labels={"train_penalized_gap": "train_penalized_gap"},
    )
    write_metric_plot_png(
        path=condition_dir / "training_gap.png",
        title=f"{config.name} training penalized gap",
        series={"train_penalized_gap": training_penalized_gap},
        y_label="penalized gap",
        series_labels={"train_penalized_gap": "train_penalized_gap"},
    )
    write_metric_plot_svg(
        path=condition_dir / "feasibility.svg",
        title=f"{config.name} training feasibility",
        series={"feasibility_rate": training_feasibility},
        y_label="feasibility",
        series_labels={"feasibility_rate": "feasibility_rate"},
    )
    write_metric_plot_png(
        path=condition_dir / "feasibility.png",
        title=f"{config.name} training feasibility",
        series={"feasibility_rate": training_feasibility},
        y_label="feasibility",
        series_labels={"feasibility_rate": "feasibility_rate"},
    )
    return payload


def build_judge_prompt(suite_summary: dict[str, Any]) -> str:
    lines = [
        "Summarize this phase-9 CVRP solver-evolution suite conservatively.",
        "Focus on feasibility, objective gap, runtime, and robustness across held-out structure families.",
        "State whether the evolved solver clearly beat the fixed baselines or not.",
        "",
        json.dumps(suite_summary, indent=2, sort_keys=True),
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the phase-9 bounded CVRP whole-solver evolution suite.")
    parser.add_argument("--config", required=True, help="Path to the phase-9 suite JSON config.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Offset added to every condition seed.")
    parser.add_argument("--replicate-label", default="", help="Optional suffix like b/c/d for replicated runs.")
    args = parser.parse_args()

    load_env_files(Path(__file__).resolve().parent)
    suite_config = Phase9SuiteConfig.load(args.config)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{args.replicate_label}" if args.replicate_label else ""
    run_root = Path(suite_config.conditions[0].output_root) / f"run_{timestamp}{suffix}"
    run_root.mkdir(parents=True, exist_ok=True)

    started = perf_counter()
    condition_payloads: list[dict[str, Any]] = []
    for base_condition in suite_config.conditions:
        data = {
            "name": base_condition.name,
            "seed": int(base_condition.seed) + int(args.seed_offset),
            "output_root": base_condition.output_root,
            "execution": base_condition.execution.__dict__,
            "agent": base_condition.agent.__dict__,
            "generation": base_condition.generation.__dict__,
            "benchmark": base_condition.benchmark.__dict__,
            "optimization": base_condition.optimization.__dict__,
            "judge": base_condition.judge.__dict__,
            "metadata": base_condition.metadata,
        }
        config = Phase9ConditionConfig.from_dict(data)
        condition_dir = run_root / config.name
        condition_dir.mkdir(parents=True, exist_ok=True)
        if config.execution.mode.startswith("baseline_"):
            payload = _baseline_condition_payload(config, condition_dir, solver_name=config.execution.mode.removeprefix("baseline_"))
        elif config.execution.mode == "solver_evolution":
            payload = _evolution_condition_payload(config, condition_dir)
        else:
            raise ValueError(f"Unsupported phase-9 execution mode: {config.execution.mode}")
        condition_payloads.append(payload)

    suite_summary = summarize_suite(condition_payloads)
    duration_seconds = perf_counter() - started
    suite_summary["duration_seconds"] = round(duration_seconds, 3)
    suite_summary["duration_hhmm"] = _format_duration_hhmm(duration_seconds)
    _json_dump(run_root / "suite_summary.json", suite_summary)
    _json_dump(
        run_root / "run_metadata.json",
        {
            "config_path": str(Path(args.config)),
            "seed_offset": int(args.seed_offset),
            "replicate_label": args.replicate_label,
            "duration_seconds": round(duration_seconds, 3),
            "duration_hhmm": _format_duration_hhmm(duration_seconds),
            "judge_status": "enabled" if any(condition.judge.enabled for condition in suite_config.conditions) else "disabled",
        },
    )

    judge_note = None
    judge_conditions = [condition for condition in suite_config.conditions if condition.judge.enabled]
    if judge_conditions:
        judge_cfg = judge_conditions[0].judge
        judge_note = judge_text(
            provider=judge_cfg.provider,
            model=judge_cfg.model,
            system_prompt="You are a careful research assistant. Answer in concise markdown.",
            user_prompt=build_judge_prompt(suite_summary),
            temperature=judge_cfg.temperature,
            max_tokens=judge_cfg.max_tokens,
            timeout=judge_cfg.timeout_seconds,
        )
    report = render_markdown_report(condition_payloads, suite_summary, judge_text_value=judge_note)
    (run_root / "report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=run_root / "report.pdf",
        run_name=run_root.name,
        markdown_report=report,
        suite_summary=suite_summary,
        condition_payloads=condition_payloads,
    )
    print(f"Completed phase-9 suite. Results written to: {run_root}")


if __name__ == "__main__":
    main()
