from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from llm_grid_battle.selection import decide_candidate_acceptance
from llm_tsp.analysis import summarize_condition as summarize_full_solver_condition
from llm_tsp.behavioral_descriptors import behavioral_distance, behavioral_profile_label
from llm_tsp.benchmark import BenchmarkBundle, TSPInstance, instance_from_dict, load_benchmark_bundle, summarize_instance
from llm_tsp.code_features import code_similarity, fingerprint_record
from llm_tsp.curriculum import build_curriculum_state, build_prompt_context, current_baseline_score, record_epoch_outcome, replay_pool
from llm_tsp.difficulty import baseline_reference_summary, build_difficulty_model, expected_gap, residual_failure_gap
from llm_tsp.llm import generate_code, judge_text, load_env_files
from llm_tsp.visualization import write_metric_plot_png, write_metric_plot_svg
from llm_tsp_operator.analysis import render_markdown_report, summarize_suite
from llm_tsp_operator.config import Phase7ConditionConfig, Phase7SuiteConfig
from llm_tsp_operator.prompting import build_generation_prompt
from llm_tsp_operator.sandbox import materialize_operator
from llm_tsp_operator.scaffold_engine import aggregate_descriptor, solve_with_portfolio, solve_with_scaffold
from llm_tsp_operator.validation import load_validation_families, render_operator_report, validate_operator_candidate
from run_tsp_suite import run_condition as run_full_solver_condition


def _json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _format_duration_hhmm(total_seconds: float) -> str:
    minutes = int(round(total_seconds / 60.0))
    hours, remainder = divmod(minutes, 60)
    return f"{hours:02d}:{remainder:02d}"


def _instance_panel(instances: list[TSPInstance], *, epoch_index: int, count: int) -> list[TSPInstance]:
    if count <= 0 or count >= len(instances):
        return list(instances)
    start = ((epoch_index - 1) * count) % len(instances)
    ordered = instances[start:] + instances[:start]
    return ordered[:count]


def _select_validation_families(
    families: dict[str, list[TSPInstance]],
    *,
    max_family_count: int,
) -> dict[str, list[TSPInstance]]:
    if max_family_count <= 0 or max_family_count >= len(families):
        return dict(families)
    selected: dict[str, list[TSPInstance]] = {}
    for family_name in sorted(families)[:max_family_count]:
        selected[family_name] = list(families[family_name])
    return selected


def _attach_difficulty_annotations(results: list[dict[str, Any]], difficulty_model: Any) -> None:
    for item in results:
        instance = instance_from_dict(item["instance"])
        predicted_gap = expected_gap(difficulty_model, instance)
        item["expected_gap"] = round(predicted_gap, 6)
        item["residual_gap"] = round(residual_failure_gap(difficulty_model, instance, float(item["optimality_gap"])), 6)


def _solve_operator_on_host(
    *,
    instance: TSPInstance,
    host_scaffold: str,
    operator_spec: dict[str, Any] | None,
    seed: int,
    stagnation_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if operator_spec is not None and str(operator_spec.get("operator_type", "")) == "scaffold_selector":
        return solve_with_portfolio(instance, operator_spec, seed=seed, stagnation_state=stagnation_state)
    if host_scaffold == "portfolio":
        if operator_spec is None:
            return solve_with_scaffold(instance, "nearest_neighbor_2opt", None, seed=seed, stagnation_state=stagnation_state)
        return solve_with_portfolio(instance, operator_spec, seed=seed, stagnation_state=stagnation_state)
    return solve_with_scaffold(instance, host_scaffold, operator_spec, seed=seed, stagnation_state=stagnation_state)


def _summarize_panel(results: list[dict[str, Any]], *, panel_name: str) -> dict[str, Any]:
    if not results:
        return {
            "enabled": False,
            "panel_name": panel_name,
            "instance_count": 0,
            "mean_optimality_gap": 0.0,
            "mean_runtime_ms": 0.0,
            "mean_distance_evaluations": 0.0,
            "family_means": [],
            "worst_instances": [],
        }
    mean_gap = sum(float(item["optimality_gap"]) for item in results) / len(results)
    mean_runtime = sum(float(item["trace"]["runtime_ms"]) for item in results) / len(results)
    mean_distance = sum(float(item["trace"]["distance_evaluations"]) for item in results) / len(results)
    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        by_family.setdefault(str(item["instance"]["family"]), []).append(item)
    family_means = [
        {
            "family": family,
            "mean_optimality_gap": round(sum(float(entry["optimality_gap"]) for entry in values) / len(values), 6),
            "count": len(values),
        }
        for family, values in sorted(by_family.items())
    ]
    worst_instances = [
        {
            "name": item["instance"]["name"],
            "family": item["instance"]["family"],
            "optimality_gap": round(float(item["optimality_gap"]), 6),
            "expected_gap": round(float(item.get("expected_gap", 0.0)), 6),
            "residual_gap": round(float(item.get("residual_gap", 0.0)), 6),
            "runtime_ms": round(float(item["trace"]["runtime_ms"]), 6),
            "distance_evaluations": int(item["trace"]["distance_evaluations"]),
            "scaffold_name": item["trace"]["scaffold_name"],
        }
        for item in sorted(results, key=lambda entry: float(entry["optimality_gap"]), reverse=True)[:5]
    ]
    return {
        "enabled": True,
        "panel_name": panel_name,
        "instance_count": len(results),
        "mean_optimality_gap": round(mean_gap, 6),
        "mean_runtime_ms": round(mean_runtime, 6),
        "mean_distance_evaluations": round(mean_distance, 6),
        "family_means": family_means,
        "worst_instances": worst_instances,
    }


def _evaluate_modular_panel(
    *,
    operator_spec: dict[str, Any] | None,
    instances: list[TSPInstance],
    panel_name: str,
    host_scaffold: str,
    seed_base: int,
    difficulty_model: Any | None = None,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    results = [
        _solve_operator_on_host(instance=instance, host_scaffold=host_scaffold, operator_spec=operator_spec, seed=seed_base + index)
        for index, instance in enumerate(instances)
    ]
    if difficulty_model is not None:
        _attach_difficulty_annotations(results, difficulty_model)
    summary = _summarize_panel(results, panel_name=panel_name)
    if incumbent_spec is not None and tolerance is not None:
        incumbent_results = [
            _solve_operator_on_host(instance=instance, host_scaffold=host_scaffold, operator_spec=incumbent_spec, seed=seed_base + 10_000 + index)
            for index, instance in enumerate(instances)
        ]
        if difficulty_model is not None:
            _attach_difficulty_annotations(incumbent_results, difficulty_model)
        baseline_mean = _summarize_panel(incumbent_results, panel_name=panel_name)["mean_optimality_gap"]
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, results


def _evaluate_transfer_probe(
    *,
    operator_spec: dict[str, Any] | None,
    holdout_instances: list[TSPInstance],
    adversarial_instances: list[TSPInstance],
    host_scaffold: str,
    seed_base: int,
    difficulty_model: Any | None = None,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    holdout_summary, holdout_results = _evaluate_modular_panel(
        operator_spec=operator_spec,
        instances=holdout_instances,
        panel_name="heldout_probe",
        host_scaffold=host_scaffold,
        seed_base=seed_base,
        difficulty_model=difficulty_model,
    )
    adversarial_summary, adversarial_results = _evaluate_modular_panel(
        operator_spec=operator_spec,
        instances=adversarial_instances,
        panel_name="adversarial_probe",
        host_scaffold=host_scaffold,
        seed_base=seed_base + 20_000,
        difficulty_model=difficulty_model,
    )
    combined_results = holdout_results + adversarial_results
    summary = _summarize_panel(combined_results, panel_name="transfer_probe")
    summary["panels"] = [holdout_summary, adversarial_summary]
    if incumbent_spec is not None and tolerance is not None:
        incumbent_results = [
            _solve_operator_on_host(instance=instance, host_scaffold=host_scaffold, operator_spec=incumbent_spec, seed=seed_base + 10_000 + index)
            for index, instance in enumerate(holdout_instances + adversarial_instances)
        ]
        if difficulty_model is not None:
            _attach_difficulty_annotations(incumbent_results, difficulty_model)
        baseline_summary = _summarize_panel(incumbent_results, panel_name="transfer_probe")
        baseline_mean = float(baseline_summary["mean_optimality_gap"])
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, holdout_summary, holdout_results, adversarial_summary, adversarial_results


def _combined_final_evaluation(
    *,
    operator_spec: dict[str, Any] | None,
    bundle: BenchmarkBundle,
    validation_families: dict[str, list[TSPInstance]],
    host_scaffold: str,
    seed_base: int,
    difficulty_model: Any | None = None,
) -> dict[str, Any]:
    tsplib_summary, tsplib_results = _evaluate_modular_panel(
        operator_spec=operator_spec,
        instances=bundle.holdout,
        panel_name="heldout_tsplib",
        host_scaffold=host_scaffold,
        seed_base=seed_base,
        difficulty_model=difficulty_model,
    )
    family_panels: list[dict[str, Any]] = []
    family_results: dict[str, list[dict[str, Any]]] = {}
    for family_index, (family_name, instances) in enumerate(sorted(validation_families.items())):
        summary, results = _evaluate_modular_panel(
            operator_spec=operator_spec,
            instances=instances,
            panel_name=family_name,
            host_scaffold=host_scaffold,
            seed_base=seed_base + 50_000 + (family_index * 10_000),
            difficulty_model=difficulty_model,
        )
        family_panels.append(summary)
        family_results[family_name] = results
    family_gap = (
        sum(float(panel["mean_optimality_gap"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
        / max(1, sum(int(panel["instance_count"]) for panel in family_panels))
    ) if family_panels else 0.0
    mean_transfer = (
        (float(tsplib_summary["mean_optimality_gap"]) * max(1, len(bundle.holdout)))
        + sum(float(panel["mean_optimality_gap"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
    ) / max(1, len(bundle.holdout) + sum(int(panel["instance_count"]) for panel in family_panels))
    return {
        "panels": [tsplib_summary, *family_panels],
        "results": {
            "heldout_tsplib": tsplib_results,
            "validation_families": family_results,
        },
        "combined": {
            "mean_tsplib_gap": round(float(tsplib_summary["mean_optimality_gap"]), 6),
            "mean_family_gap": round(family_gap, 6),
            "mean_transfer_gap": round(mean_transfer, 6),
        },
    }


def _replay_instances(config: Phase7ConditionConfig, state: dict[str, Any]) -> list[TSPInstance]:
    selected = replay_pool(config, state)
    return [instance_from_dict(item["instance"]) for item in selected]


def _apply_compression_pressure(
    *,
    decision: dict[str, Any],
    config: Phase7ConditionConfig,
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


def _apply_pareto_pressure(
    *,
    decision: dict[str, Any],
    config: Phase7ConditionConfig,
    incumbent: dict[str, Any] | None,
    candidate_training_summary: dict[str, Any],
    candidate_fingerprint: dict[str, Any],
) -> dict[str, Any]:
    if not decision.get("accepted") or config.selection.mode != "pareto" or not incumbent:
        return decision
    gap = float(candidate_training_summary.get("mean_optimality_gap", 0.0))
    runtime = float(candidate_training_summary.get("mean_runtime_ms", 0.0))
    incumbent_gap = float(incumbent.get("mean_training_gap", gap))
    incumbent_runtime = float(incumbent.get("mean_runtime_ms", runtime))
    incumbent_complexity = float(incumbent.get("complexity_score", candidate_fingerprint.get("complexity_score", 0.0)))
    complexity = float(candidate_fingerprint.get("complexity_score", 0.0))

    gap_ok = gap <= incumbent_gap + float(config.selection.pareto_gap_tolerance)
    runtime_ok = runtime <= incumbent_runtime * (1.0 + float(config.selection.pareto_runtime_tolerance))
    complexity_ok = complexity <= incumbent_complexity + float(config.selection.pareto_complexity_tolerance)
    strict_gain = (
        gap < incumbent_gap
        or runtime < incumbent_runtime
        or complexity < incumbent_complexity
    )
    if not (gap_ok and runtime_ok and complexity_ok and strict_gain):
        decision["accepted"] = False
        decision["reason"] = "rejected_by_pareto_gate"
    return decision


def _build_baseline_payload(config: Phase7ConditionConfig, condition_dir: Path) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    bundle = load_benchmark_bundle(Path(config.benchmark.manifest_path))
    validation_families = _select_validation_families(
        load_validation_families(config.benchmark.manifest_path),
        max_family_count=int(config.benchmark.validation_family_count),
    )
    final_evaluation = _combined_final_evaluation(
        operator_spec=None,
        bundle=bundle,
        validation_families=validation_families,
        host_scaffold=config.operator.host_scaffold,
        seed_base=config.seed + 900_000,
        difficulty_model=build_difficulty_model(bundle.train + bundle.adversarial, seed_base=config.seed + 700_000),
    )
    payload = {
        "condition_name": config.name,
        "execution_mode": "baseline_only",
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": config.benchmark.__dict__,
        "operator": config.operator.__dict__,
        "validation": config.validation.__dict__,
        "optimization": config.optimization.__dict__,
        "metadata": config.metadata,
        "epochs": [],
        "accepted_operator_spec": None,
        "accepted_operator_code": None,
        "final_evaluation": final_evaluation,
        "operator_validation": {},
        "curriculum_trace": [],
    }
    _json_dump(condition_dir / "condition_summary.json", payload)
    return payload


def _build_full_solver_payload(config: Phase7ConditionConfig, condition_dir: Path) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    full_payload = run_full_solver_condition(_as_full_solver_config(config), condition_dir)
    full_payload["execution_mode"] = "full_solver"
    if "combined" in (full_payload.get("final_evaluation") or {}):
        combined = dict(full_payload["final_evaluation"]["combined"])
        if "mean_synthetic_gap" in combined and "mean_family_gap" not in combined:
            combined["mean_family_gap"] = combined["mean_synthetic_gap"]
        full_payload["final_evaluation"]["combined"] = combined
    full_payload["operator"] = {"host_scaffold": "whole_solver"}
    full_payload["accepted_operator_spec"] = None
    full_payload["operator_validation"] = {}
    _json_dump(condition_dir / "condition_summary.json", full_payload)
    return full_payload


def _as_full_solver_config(config: Phase7ConditionConfig) -> Any:
    from llm_tsp.config import TSPConditionConfig

    data = {
        "name": config.name,
        "seed": config.seed,
        "output_root": config.output_root,
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": {
            **config.selection.__dict__,
            "mode": "score_only" if config.selection.mode == "pareto" else config.selection.mode,
        },
        "benchmark": {
            "manifest_path": config.benchmark.manifest_path,
            "curriculum_batch_size": config.benchmark.curriculum_batch_size,
            "transfer_probe_count": config.benchmark.transfer_probe_count,
            "adversarial_probe_count": config.benchmark.adversarial_probe_count,
        },
        "optimization": config.optimization.__dict__,
        "judge": config.judge.__dict__,
        "metadata": {**config.metadata, "phase7_wrapper": True},
    }
    return TSPConditionConfig.from_dict(data)


def run_modular_condition(config: Phase7ConditionConfig, condition_dir: Path) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    bundle = load_benchmark_bundle(Path(config.benchmark.manifest_path))
    validation_families = _select_validation_families(
        load_validation_families(config.benchmark.manifest_path),
        max_family_count=int(config.benchmark.validation_family_count),
    )
    difficulty_model = build_difficulty_model(bundle.train + bundle.adversarial, seed_base=config.seed + 700_000)
    state = build_curriculum_state(
        config,
        bundle.adversarial,
        reference_instances=bundle.train + bundle.adversarial,
        difficulty_model=difficulty_model,
    )
    history: list[dict[str, Any]] = []
    generation_cache: dict[str, str] = {}

    training_gap_series: list[float] = []
    transfer_gap_series: list[float] = []
    novelty_series: list[float] = []
    complexity_series: list[float] = []

    latest_operator_spec: dict[str, Any] | None = None
    latest_executed_code = None
    for epoch_index in range(1, int(config.optimization.epochs) + 1):
        epoch_dir = condition_dir / "epochs" / f"epoch_{epoch_index:03d}"
        epoch_dir.mkdir(parents=True, exist_ok=True)
        state["selection_epoch_cursor"] = epoch_index
        training_instances = _instance_panel(bundle.train, epoch_index=epoch_index, count=int(config.benchmark.curriculum_batch_size))
        training_panel_summary = []
        for instance in training_instances:
            summary = summarize_instance(instance)
            summary["expected_gap"] = round(expected_gap(difficulty_model, instance), 6)
            training_panel_summary.append(summary)
        prompt_context = build_prompt_context(config, state)
        prompt = build_generation_prompt(
            epoch_index=epoch_index,
            history=history,
            training_panel=training_panel_summary,
            host_scaffold=config.operator.host_scaffold,
            allowed_operator_types=config.operator.allowed_operator_types,
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

        materialized = materialize_operator(submitted_code)
        executed_code = str(materialized.executed_code or submitted_code)
        operator_spec = dict(materialized.operator_spec)
        if operator_spec.get("operator_type") not in config.operator.allowed_operator_types:
            operator_spec = dict(materialize_operator("").operator_spec)
            executed_code = materialize_operator("").executed_code
        latest_operator_spec = operator_spec
        latest_executed_code = executed_code

        training_summary, training_results = _evaluate_modular_panel(
            operator_spec=operator_spec,
            instances=training_instances,
            panel_name="training",
            host_scaffold=config.operator.host_scaffold,
            seed_base=config.seed + (epoch_index * 1_000),
            difficulty_model=difficulty_model,
        )
        descriptor = aggregate_descriptor(training_results)
        code_fingerprint = fingerprint_record(executed_code)
        incumbent = state.get("incumbent")
        candidate_novelty = 0.0
        if history:
            previous_code = str(history[-1].get("accepted_operator_code") or history[-1].get("executed_code") or "")
            candidate_novelty = round(1.0 - code_similarity(previous_code, executed_code), 6)

        replay_probe_summary = None
        replay_instances = _replay_instances(config, state)
        incumbent_spec = incumbent.get("operator_spec") if incumbent else None
        if replay_instances and incumbent_spec is not None:
            replay_probe_summary, _ = _evaluate_modular_panel(
                operator_spec=operator_spec,
                instances=replay_instances,
                panel_name="replay_probe",
                host_scaffold=config.operator.host_scaffold,
                seed_base=config.seed + 200_000 + (epoch_index * 1_000),
                difficulty_model=difficulty_model,
                incumbent_spec=incumbent_spec,
                tolerance=float(config.selection.replay_gap_tolerance),
            )

        holdout_probe_instances = _instance_panel(bundle.holdout, epoch_index=epoch_index, count=int(config.benchmark.transfer_probe_count))
        adversarial_probe_instances = _instance_panel(bundle.adversarial, epoch_index=epoch_index, count=int(config.benchmark.adversarial_probe_count))
        (
            transfer_probe_summary,
            holdout_probe_summary,
            _holdout_probe_results,
            adversarial_probe_summary,
            adversarial_probe_results,
        ) = _evaluate_transfer_probe(
            operator_spec=operator_spec,
            holdout_instances=holdout_probe_instances,
            adversarial_instances=adversarial_probe_instances,
            host_scaffold=config.operator.host_scaffold,
            seed_base=config.seed + 400_000 + (epoch_index * 1_000),
            difficulty_model=difficulty_model,
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
            selection_decision = _apply_pareto_pressure(
                decision=selection_decision,
                config=config,
                incumbent=incumbent,
                candidate_training_summary=training_summary,
                candidate_fingerprint=code_fingerprint,
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
            state["incumbent"]["operator_spec"] = operator_spec
            state["incumbent"]["complexity_score"] = code_fingerprint["complexity_score"]
            state["incumbent"]["mean_runtime_ms"] = float(training_summary["mean_runtime_ms"])
            state["incumbent"]["mean_training_gap"] = float(training_summary["mean_optimality_gap"])

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
            "operator_spec": operator_spec,
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
            "accepted_operator_code": (state.get("incumbent") or {}).get("code"),
        }
        history.append(epoch_payload)
        _json_dump(epoch_dir / "artifact.json", epoch_payload)

    incumbent = state.get("incumbent")
    final_spec = incumbent.get("operator_spec") if incumbent else latest_operator_spec
    final_code = incumbent.get("code") if incumbent else latest_executed_code
    final_evaluation = _combined_final_evaluation(
        operator_spec=final_spec,
        bundle=bundle,
        validation_families=validation_families,
        host_scaffold=config.operator.host_scaffold,
        seed_base=config.seed + 900_000,
        difficulty_model=difficulty_model,
    )
    operator_validation = validate_operator_candidate(
        operator_code=str(final_code or ""),
        operator_spec=dict(final_spec or {}),
        holdout_instances=bundle.holdout,
        family_panels=validation_families,
        host_scaffold=config.operator.host_scaffold,
        validation_config=config.validation,
        seed_base=config.seed + 1_200_000,
    ) if final_spec else {}

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
        "execution_mode": "modular_operator",
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": config.benchmark.__dict__,
        "operator": config.operator.__dict__,
        "validation": config.validation.__dict__,
        "optimization": config.optimization.__dict__,
        "metadata": config.metadata,
        "difficulty_model": {
            "reference_summary": baseline_reference_summary(difficulty_model),
            "reference_count": len(difficulty_model.references),
            "neighbor_count": difficulty_model.neighbor_count,
        },
        "epochs": history,
        "accepted_operator_spec": final_spec,
        "accepted_operator_code": final_code,
        "final_evaluation": final_evaluation,
        "operator_validation": operator_validation,
        "replay_archives": {
            "experience_cases": state["experience_archive"].to_list(),
            "worst_cases": state["worst_archive"].to_list(),
            "failure_cases": state["failure_archive"].to_list(),
            "residual_failures": state["residual_archive"].to_list(),
            "adversarial_layouts": state["adversarial_archive"].to_list(),
        },
        "elite_archive": state["elite_archive"].to_list(),
        "curriculum_trace": state["trace"],
    }
    _json_dump(condition_dir / "condition_summary.json", condition_payload)
    if operator_validation:
        _json_dump(condition_dir / "operator_report.json", operator_validation)
        (condition_dir / "operator_report.md").write_text(render_operator_report(operator_validation), encoding="utf-8")
    return condition_payload


def build_judge_prompt(suite_summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are reviewing a TSP modular-operator discovery suite.",
            "Interpret results conservatively and prioritize held-out gap, transfer, transplant, ablation, and Pareto tradeoffs over narrative speculation.",
            "",
            "Rules:",
            "- Treat held-out TSPLIB gap and family holdout gap as the main transfer evidence.",
            "- A modular operator is only interesting if validation survives transplant or ablation checks.",
            "- Prefer claims about reusable operator structure over full-solver performance when the modular conditions support them.",
            "- Do not claim algorithm discovery unless the operator survives the scaffold and family tests.",
            "",
            json.dumps(suite_summary, indent=2, sort_keys=True),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the phase-7 modular TSP operator-discovery suite.")
    parser.add_argument("--config", default="configs/tsp_phase7_suite/01_operator_discovery.json", help="Path to the phase-7 suite config JSON.")
    parser.add_argument("--output-root", default=None, help="Optional override for the output root directory.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Add this offset to every condition seed.")
    parser.add_argument("--replicate-label", default=None, help="Optional replicate label.")
    parser.add_argument("--skip-judge", action="store_true", help="Skip the final analysis model call.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    load_env_files(project_root)
    suite = Phase7SuiteConfig.load(project_root / args.config)
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
        condition_dir = run_dir / condition.name
        if condition.execution.mode == "baseline_only":
            condition_payloads.append(_build_baseline_payload(condition, condition_dir))
        elif condition.execution.mode == "full_solver":
            condition_payloads.append(_build_full_solver_payload(condition, condition_dir))
        else:
            condition_payloads.append(run_modular_condition(condition, condition_dir))

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
    print(f"Completed phase-7 operator suite. Results written to: {run_dir}")


if __name__ == "__main__":
    main()
