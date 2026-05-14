from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from llm_atsp.analysis import render_markdown_report, summarize_suite
from llm_atsp.behavioral_descriptors import behavioral_distance, behavioral_profile_label
from llm_atsp.benchmark import BenchmarkBundle, ATSPInstance, instance_from_dict, load_benchmark_bundle, summarize_instance
from llm_atsp.code_features import code_similarity, fingerprint_record
from llm_atsp.config import ATSPConditionConfig, ATSPSuiteConfig
from llm_atsp.curriculum import build_curriculum_state, build_prompt_context, current_baseline_score, record_epoch_outcome, replay_pool
from llm_atsp.heuristic_engine import aggregate_descriptor, canonicalize_heuristic_spec, default_heuristic_code, solve_instance
from llm_atsp.llm import generate_code, judge_text, load_env_files
from llm_atsp.prompting import build_generation_prompt
from llm_atsp.sandbox import materialize_heuristic
from llm_atsp.visualization import write_metric_plot_png, write_metric_plot_svg
from llm_grid_battle.pdf_report import write_pdf_report
from llm_grid_battle.selection import decide_candidate_acceptance


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _format_duration_hhmm(total_seconds: float) -> str:
    minutes = int(round(total_seconds / 60.0))
    hours, remainder = divmod(minutes, 60)
    return f"{hours:02d}:{remainder:02d}"


def _instance_panel(instances: list[ATSPInstance], *, epoch_index: int, count: int) -> list[ATSPInstance]:
    if count <= 0 or count >= len(instances):
        return list(instances)
    start = ((epoch_index - 1) * count) % len(instances)
    ordered = instances[start:] + instances[:start]
    return ordered[:count]


def _summarize_panel(results: list[dict[str, Any]], *, panel_name: str) -> dict[str, Any]:
    if not results:
        return {
            "enabled": False,
            "panel_name": panel_name,
            "instance_count": 0,
            "mean_optimality_gap": 0.0,
            "family_means": [],
            "worst_instances": [],
        }
    mean_gap = sum(float(item["optimality_gap"]) for item in results) / len(results)
    by_family: dict[str, list[float]] = {}
    for item in results:
        family = str(item["instance"]["family"])
        by_family.setdefault(family, []).append(float(item["optimality_gap"]))
    family_means = [
        {"family": family, "mean_optimality_gap": round(sum(values) / len(values), 6), "count": len(values)}
        for family, values in sorted(by_family.items())
    ]
    worst_instances = [
        {
            "name": item["instance"]["name"],
            "family": item["instance"]["family"],
            "optimality_gap": round(float(item["optimality_gap"]), 6),
            "best_known_cost": int(item["best_known_cost"]),
            "cost": int(item["cost"]),
        }
        for item in sorted(results, key=lambda item: float(item["optimality_gap"]), reverse=True)[:5]
    ]
    return {
        "enabled": True,
        "panel_name": panel_name,
        "instance_count": len(results),
        "mean_optimality_gap": round(mean_gap, 6),
        "family_means": family_means,
        "worst_instances": worst_instances,
    }


def _evaluate_panel(
    *,
    spec: dict[str, Any],
    instances: list[ATSPInstance],
    panel_name: str,
    seed_base: int,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    results = [solve_instance(instance, spec, seed=seed_base + index) for index, instance in enumerate(instances)]
    summary = _summarize_panel(results, panel_name=panel_name)
    if incumbent_spec is not None and tolerance is not None:
        incumbent_results = [solve_instance(instance, incumbent_spec, seed=seed_base + 10_000 + index) for index, instance in enumerate(instances)]
        baseline_mean = _summarize_panel(incumbent_results, panel_name=panel_name)["mean_optimality_gap"]
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, results


def _evaluate_transfer_probe(
    *,
    spec: dict[str, Any],
    holdout_instances: list[ATSPInstance],
    adversarial_instances: list[ATSPInstance],
    seed_base: int,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    holdout_results = [solve_instance(instance, spec, seed=seed_base + index) for index, instance in enumerate(holdout_instances)]
    adversarial_results = [
        solve_instance(instance, spec, seed=seed_base + 20_000 + index) for index, instance in enumerate(adversarial_instances)
    ]
    holdout_summary = _summarize_panel(holdout_results, panel_name="heldout_probe")
    adversarial_summary = _summarize_panel(adversarial_results, panel_name="adversarial_probe")
    combined_results = holdout_results + adversarial_results
    summary = _summarize_panel(combined_results, panel_name="transfer_probe")
    summary["panels"] = [holdout_summary, adversarial_summary]
    if incumbent_spec is not None and tolerance is not None:
        incumbent_holdout_results = [
            solve_instance(instance, incumbent_spec, seed=seed_base + 10_000 + index)
            for index, instance in enumerate(holdout_instances)
        ]
        incumbent_adversarial_results = [
            solve_instance(instance, incumbent_spec, seed=seed_base + 30_000 + index)
            for index, instance in enumerate(adversarial_instances)
        ]
        baseline_summary = _summarize_panel(incumbent_holdout_results + incumbent_adversarial_results, panel_name="transfer_probe")
        baseline_mean = float(baseline_summary["mean_optimality_gap"])
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, holdout_summary, holdout_results, adversarial_summary, adversarial_results


def _combined_final_evaluation(
    *,
    spec: dict[str, Any],
    bundle: BenchmarkBundle,
    seed_base: int,
) -> dict[str, Any]:
    tsplib_summary, _ = _evaluate_panel(spec=spec, instances=bundle.holdout, panel_name="heldout_tsplib", seed_base=seed_base)
    synthetic_summary, _ = _evaluate_panel(spec=spec, instances=bundle.synthetic_holdout, panel_name="synthetic_holdout", seed_base=seed_base + 50_000)
    mean_transfer = (
        (float(tsplib_summary["mean_optimality_gap"]) * max(1, len(bundle.holdout)))
        + (float(synthetic_summary["mean_optimality_gap"]) * max(1, len(bundle.synthetic_holdout)))
    ) / max(1, len(bundle.holdout) + len(bundle.synthetic_holdout))
    return {
        "panels": [tsplib_summary, synthetic_summary],
        "combined": {
            "mean_tsplib_gap": round(float(tsplib_summary["mean_optimality_gap"]), 6),
            "mean_synthetic_gap": round(float(synthetic_summary["mean_optimality_gap"]), 6),
            "mean_transfer_gap": round(mean_transfer, 6),
        },
    }


def _replay_instances(config: ATSPConditionConfig, state: dict[str, Any]) -> list[ATSPInstance]:
    selected = replay_pool(config, state)
    return [instance_from_dict(item["instance"]) for item in selected]


def _apply_compression_pressure(
    *,
    decision: dict[str, Any],
    config: ATSPConditionConfig,
    incumbent: dict[str, Any] | None,
    candidate_fingerprint: dict[str, Any],
    candidate_novelty: float,
    transfer_probe_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not decision.get("accepted") or not config.selection.compression_pressure or not incumbent:
        return decision
    complexity_delta = float(candidate_fingerprint.get("complexity_score", 0.0)) - float(incumbent.get("complexity_score", 0.0))
    transfer_delta = None
    if transfer_probe_summary and transfer_probe_summary.get("enabled"):
        transfer_delta = float(transfer_probe_summary.get("gap_delta", 0.0))
    if complexity_delta > float(config.selection.max_complexity_increase) and (transfer_delta is None or transfer_delta >= -0.002):
        decision["accepted"] = False
        decision["reason"] = "rejected_by_complexity_pressure"
        decision["complexity_delta"] = round(complexity_delta, 6)
        return decision
    if candidate_novelty > 0.35 and (transfer_delta is None or transfer_delta >= -0.001):
        decision["accepted"] = False
        decision["reason"] = "rejected_by_novelty_pressure"
        decision["complexity_delta"] = round(complexity_delta, 6)
    return decision


def run_condition(config: ATSPConditionConfig, condition_dir: Path) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    bundle = load_benchmark_bundle(Path(config.benchmark.manifest_path))
    state = build_curriculum_state(config, bundle.adversarial)
    history: list[dict[str, Any]] = []
    generation_cache: dict[str, str] = {}

    training_gap_series: list[float] = []
    transfer_gap_series: list[float] = []
    novelty_series: list[float] = []
    complexity_series: list[float] = []

    for epoch_index in range(1, int(config.optimization.epochs) + 1):
        epoch_dir = condition_dir / "epochs" / f"epoch_{epoch_index:03d}"
        epoch_dir.mkdir(parents=True, exist_ok=True)
        training_instances = _instance_panel(bundle.train, epoch_index=epoch_index, count=int(config.benchmark.curriculum_batch_size))
        training_panel_summary = [summarize_instance(instance) for instance in training_instances]
        prompt_context = build_prompt_context(config, state)
        prompt = build_generation_prompt(
            epoch_index=epoch_index,
            history=history,
            training_panel=training_panel_summary,
            curriculum_context=prompt_context,
        )
        if not config.agent.regenerate_each_epoch and generation_cache.get(config.agent.name):
            submitted_code = generation_cache[config.agent.name]
            generation_result = None
        else:
            generation_result = generate_code(
                provider=config.agent.provider,
                model=config.agent.model,
                system_prompt=config.agent.system_prompt,
                user_prompt=prompt,
                temperature=config.agent.temperature,
                max_tokens=config.agent.max_tokens,
                repair_invalid_submissions=config.generation.repair_invalid_submissions,
            )
            submitted_code = str(generation_result.submitted_code or generation_result.code)
            if not config.agent.regenerate_each_epoch:
                generation_cache[config.agent.name] = submitted_code

        materialized = materialize_heuristic(submitted_code)
        executed_code = str(materialized.executed_code or default_heuristic_code())
        heuristic_spec = canonicalize_heuristic_spec(materialized.heuristic_spec)
        training_summary, training_results = _evaluate_panel(
            spec=heuristic_spec,
            instances=training_instances,
            panel_name="training",
            seed_base=config.seed + (epoch_index * 1_000),
        )
        descriptor = aggregate_descriptor(training_results)
        code_fingerprint = fingerprint_record(executed_code)
        incumbent = state.get("incumbent")
        candidate_novelty = 0.0
        if history:
            previous_code = str(history[-1].get("accepted_code") or history[-1].get("executed_code") or "")
            candidate_novelty = round(1.0 - code_similarity(previous_code, executed_code), 6)

        replay_probe_summary = None
        replay_instances = _replay_instances(config, state)
        incumbent_spec = canonicalize_heuristic_spec(incumbent["heuristic_spec"]) if incumbent and incumbent.get("heuristic_spec") else None
        if replay_instances and incumbent_spec is not None:
            replay_probe_summary, _ = _evaluate_panel(
                spec=heuristic_spec,
                instances=replay_instances,
                panel_name="replay_probe",
                seed_base=config.seed + 200_000 + (epoch_index * 1_000),
                incumbent_spec=incumbent_spec,
                tolerance=float(config.selection.replay_gap_tolerance),
            )

        holdout_probe_instances = _instance_panel(
            bundle.holdout,
            epoch_index=epoch_index,
            count=int(config.benchmark.transfer_probe_count),
        )
        adversarial_probe_instances = _instance_panel(
            bundle.adversarial,
            epoch_index=epoch_index,
            count=int(config.benchmark.adversarial_probe_count),
        )
        (
            transfer_probe_summary,
            holdout_probe_summary,
            _holdout_probe_results,
            adversarial_probe_summary,
            adversarial_probe_results,
        ) = _evaluate_transfer_probe(
            spec=heuristic_spec,
            holdout_instances=holdout_probe_instances,
            adversarial_instances=adversarial_probe_instances,
            seed_base=config.seed + 400_000 + (epoch_index * 1_000),
            incumbent_spec=incumbent_spec,
            tolerance=float(config.selection.transfer_gap_tolerance) if incumbent_spec is not None else None,
        )

        baseline_score = current_baseline_score(state)
        if config.selection.mode == "accept_all":
            selection_decision = {"accepted": True, "reason": "accept_all"}
        else:
            elite_archive = state["elite_archive"]
            elite_entry = elite_archive.get(descriptor)
            selection_decision = decide_candidate_acceptance(
                policy=config.selection,
                candidate_score=-float(training_summary["mean_optimality_gap"]),
                baseline_score=baseline_score,
                behavioral_distance=behavioral_distance(descriptor, incumbent.get("descriptor") if incumbent else None),
                elite_distance=elite_archive.nearest_distance(descriptor),
                opens_new_elite_cell=elite_archive.would_open_cell(descriptor),
                elite_cell_score=float(elite_entry.score) if elite_entry else None,
                replay_summary=replay_probe_summary if incumbent_spec is not None else None,
                holdout_summary=transfer_probe_summary if incumbent_spec is not None else None,
            )
            selection_decision = _apply_compression_pressure(
                decision=selection_decision,
                config=config,
                incumbent=incumbent,
                candidate_fingerprint=code_fingerprint,
                candidate_novelty=candidate_novelty,
                transfer_probe_summary=transfer_probe_summary,
            )

        curriculum_trace = record_epoch_outcome(
            config=config,
            state=state,
            epoch_index=epoch_index,
            executed_code=executed_code,
            descriptor=descriptor,
            selection_decision=selection_decision,
            training_results=training_results,
            adversarial_probe_results=adversarial_probe_results,
            mean_training_score=-float(training_summary["mean_optimality_gap"]),
        )
        if selection_decision and selection_decision.get("accepted"):
            state["incumbent"]["heuristic_spec"] = heuristic_spec
            state["incumbent"]["complexity_score"] = code_fingerprint["complexity_score"]

        training_gap_series.append(float(training_summary["mean_optimality_gap"]))
        transfer_gap_series.append(float(transfer_probe_summary["mean_optimality_gap"]))
        novelty_series.append(candidate_novelty)
        complexity_series.append(float(code_fingerprint["complexity_score"]))

        epoch_payload = {
            "epoch_index": epoch_index,
            "prompt": prompt,
            "raw_response": generation_result.raw_text if generation_result else None,
            "submitted_code": submitted_code,
            "executed_code": executed_code,
            "generation_error": generation_result.error if generation_result else None,
            "generation_used_fallback": bool(generation_result.used_fallback) if generation_result else False,
            "validation_issues": generation_result.validation_issues if generation_result else [],
            "materialization_issues": materialized.issues,
            "materialization_init_error": materialized.init_error,
            "materialization_used_fallback": materialized.used_fallback,
            "heuristic_spec": heuristic_spec,
            "code_fingerprint": code_fingerprint,
            "code_novelty": candidate_novelty,
            "behavioral_descriptor": descriptor,
            "behavior_profile": behavioral_profile_label(descriptor),
            "training_panel": training_panel_summary,
            "training_results": training_results,
            "training_summary": training_summary,
            "replay_probe": replay_probe_summary,
            "transfer_probe": transfer_probe_summary,
            "holdout_probe": holdout_probe_summary,
            "adversarial_probe": adversarial_probe_summary,
            "selection": selection_decision,
            "curriculum": curriculum_trace,
            "accepted_code": (state.get("incumbent") or {}).get("code"),
        }
        history.append(epoch_payload)
        _json_dump(epoch_dir / "artifact.json", epoch_payload)

    incumbent = state.get("incumbent")
    final_spec = incumbent.get("heuristic_spec") if incumbent else heuristic_spec
    final_evaluation = _combined_final_evaluation(
        spec=final_spec,
        bundle=bundle,
        seed_base=config.seed + 900_000,
    )

    write_metric_plot_svg(
        path=condition_dir / "training_gap.svg",
        title=f"{config.name} training gap",
        series={"mean_training_gap": training_gap_series},
        y_label="Mean optimality gap",
    )
    write_metric_plot_png(
        path=condition_dir / "training_gap.png",
        title=f"{config.name} training gap",
        series={"mean_training_gap": training_gap_series},
        y_label="Mean optimality gap",
    )
    write_metric_plot_svg(
        path=condition_dir / "transfer_gap.svg",
        title=f"{config.name} transfer probe gap",
        series={"transfer_probe_gap": transfer_gap_series},
        y_label="Mean optimality gap",
    )
    write_metric_plot_png(
        path=condition_dir / "transfer_gap.png",
        title=f"{config.name} transfer probe gap",
        series={"transfer_probe_gap": transfer_gap_series},
        y_label="Mean optimality gap",
    )

    condition_payload = {
        "condition_name": config.name,
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": config.benchmark.__dict__,
        "optimization": config.optimization.__dict__,
        "metadata": config.metadata,
        "epochs": history,
        "final_evaluation": final_evaluation,
        "archive": state["failure_archive"].to_list(),
        "replay_archives": {
            "worst_cases": state["worst_archive"].to_list(),
            "failure_cases": state["failure_archive"].to_list(),
            "adversarial_layouts": state["adversarial_archive"].to_list(),
        },
        "elite_archive": state["elite_archive"].to_list(),
        "curriculum_trace": state["trace"],
    }
    _json_dump(condition_dir / "condition_summary.json", condition_payload)
    return condition_payload


def build_judge_prompt(suite_summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are reviewing a replay-aware ATSP benchmark suite.",
            "Interpret results conservatively and prioritize optimality-gap and transfer metrics over narrative speculation.",
            "",
            "Rules:",
            "- Treat held-out TSPLIB ATSP gap and synthetic holdout gap as the main evidence for transfer.",
            "- If code novelty falls while transfer improves, say that explicitly.",
            "- Do not equate lexical novelty with algorithmic invention unless the deterministic metrics support it.",
            "- Distinguish no replay, random replay, failure replay, and compression-aware replay conditions carefully.",
            "",
            json.dumps(suite_summary, indent=2, sort_keys=True),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a replay-aware ATSP suite.")
    parser.add_argument("--config", default="configs/atsp_suite/01_replay_transfer.json", help="Path to the ATSP suite config JSON.")
    parser.add_argument("--output-root", default=None, help="Optional override for the output root directory.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Add this offset to every condition seed.")
    parser.add_argument("--replicate-label", default=None, help="Optional replicate label.")
    parser.add_argument("--skip-judge", action="store_true", help="Skip the final analysis model call.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    load_env_files(project_root)
    suite = ATSPSuiteConfig.load(project_root / args.config)
    if args.seed_offset or args.replicate_label:
        for condition in suite.conditions:
            if args.seed_offset:
                condition.seed += int(args.seed_offset)
            if args.replicate_label:
                condition.metadata = {
                    **condition.metadata,
                    "replicate_label": str(args.replicate_label),
                    "seed_offset": int(args.seed_offset),
                }

    started_at = datetime.now()
    timestamp = started_at.strftime("%Y%m%d_%H%M%S")
    base_output_root = Path(args.output_root) if args.output_root else project_root / suite.conditions[0].output_root
    run_name = f"run_{timestamp}"
    if args.replicate_label:
        run_name = f"{run_name}_{args.replicate_label}"
    run_dir = base_output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    condition_payloads = []
    for condition in suite.conditions:
        condition_payloads.append(run_condition(condition, run_dir / condition.name))

    suite_summary = summarize_suite(condition_payloads)
    _json_dump(run_dir / "suite_summary.json", suite_summary)

    llm_report = None
    judge_config = suite.conditions[0].judge
    if judge_config.enabled and not args.skip_judge:
        llm_report = judge_text(
            provider=judge_config.provider,
            model=judge_config.model,
            system_prompt="You are a careful research assistant. Answer in concise markdown.",
            user_prompt=build_judge_prompt(suite_summary),
            temperature=judge_config.temperature,
            max_tokens=judge_config.max_tokens,
            timeout=judge_config.timeout_seconds,
        )

    finished_at = datetime.now()
    run_metadata = {
        "run_name": run_dir.name,
        "started_at_local": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at_local": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_hhmm": _format_duration_hhmm((finished_at - started_at).total_seconds()),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
        "seed_offset": int(args.seed_offset),
        "replicate_label": str(args.replicate_label) if args.replicate_label else None,
        "judge_status": "enabled" if llm_report is not None else ("skipped" if args.skip_judge else "disabled"),
        "judge_provider": judge_config.provider if llm_report is not None else None,
        "judge_model": judge_config.model if llm_report is not None else None,
    }
    _json_dump(run_dir / "run_metadata.json", run_metadata)

    report = render_markdown_report(suite_summary, llm_report, run_metadata=run_metadata)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=run_dir / "report.pdf",
        run_name=run_dir.name,
        markdown_report=report,
        suite_summary=suite_summary,
        condition_payloads=condition_payloads,
    )
    print(f"Completed ATSP suite. Results written to: {run_dir}")


if __name__ == "__main__":
    main()
