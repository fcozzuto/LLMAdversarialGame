from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from llm_grid_battle.selection import decide_candidate_acceptance
from llm_tsp.behavioral_descriptors import behavioral_distance, behavioral_profile_label
from llm_tsp.benchmark import BenchmarkBundle, TSPInstance, instance_from_dict, load_benchmark_bundle, summarize_instance
from llm_tsp.code_features import code_similarity, complexity_score, fingerprint_record
from llm_tsp.curriculum import build_curriculum_state, build_prompt_context, current_baseline_score, record_epoch_outcome, replay_pool
from llm_tsp.difficulty import baseline_reference_summary, build_difficulty_model, expected_gap, residual_failure_gap
from llm_tsp.heuristic_engine import canonicalize_heuristic_spec, solve_instance as solve_full_solver_instance
from llm_tsp.llm import judge_text, load_env_files
from llm_tsp.visualization import write_metric_plot_png, write_metric_plot_svg
from llm_tsp_operator.validation import load_validation_families
from llm_tsp_portfolio.analysis import render_markdown_report, summarize_suite
from llm_tsp_portfolio.config import Phase8ConditionConfig, Phase8SuiteConfig
from llm_tsp_portfolio.controller_schema import controller_rule_summary, controller_signature
from llm_tsp_portfolio.llm import generate_code
from llm_tsp_portfolio.portfolio_library import (
    PORTFOLIO_COMPONENT_LIBRARY,
    FROZEN_HEURISTICS,
    fit_knn_selector,
    heuristic_catalog,
    heuristic_names,
    portfolio_descriptor,
    random_portfolio_choice,
    run_controller,
    run_fixed_heuristic,
    run_static_controller,
)
from llm_tsp_portfolio.prompting import build_generation_prompt
from llm_tsp_portfolio.sandbox import materialize_controller
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


@dataclass
class Phase8Context:
    bundle: BenchmarkBundle
    validation_families: dict[str, list[TSPInstance]]
    difficulty_model: Any
    heuristic_names: list[str]
    heuristic_reference: dict[str, Any]
    train_table: dict[tuple[str, ...], dict[str, dict[str, dict[str, Any]]]]
    train_best_heuristic: str
    knn_selector: Any


def _panel_key(instances: list[TSPInstance], seed_base: int) -> tuple[str, ...]:
    names = tuple(sorted(instance.name for instance in instances))
    return (str(seed_base), *names)


def _evaluation_table(
    *,
    instances: list[TSPInstance],
    context: Phase8Context,
    seed_base: int,
) -> dict[str, dict[str, dict[str, Any]]]:
    key = _panel_key(instances, seed_base)
    if key in context.train_table:
        return context.train_table[key]
    table: dict[str, dict[str, dict[str, Any]]] = {}
    for instance_index, instance in enumerate(instances):
        per_heuristic: dict[str, dict[str, Any]] = {}
        for heuristic_index, heuristic_name in enumerate(context.heuristic_names):
            result = run_fixed_heuristic(
                instance,
                heuristic_name,
                seed=seed_base + (instance_index * 100) + heuristic_index,
            )
            per_heuristic[heuristic_name] = result
        table[instance.name] = per_heuristic
    context.train_table[key] = table
    return table


def _heuristic_reference_summary(
    training_instances: list[TSPInstance],
    table: dict[str, dict[str, dict[str, Any]]],
    heuristic_names_list: list[str],
) -> dict[str, Any]:
    rows = []
    best_name = None
    best_gap = None
    for heuristic_name in heuristic_names_list:
        results = [table[instance.name][heuristic_name] for instance in training_instances]
        mean_gap = sum(float(item["optimality_gap"]) for item in results) / len(results)
        mean_runtime = sum(float(item["trace"]["runtime_ms"]) for item in results) / len(results)
        by_structure: dict[str, list[float]] = {}
        for item in results:
            structure = str(item["instance"]["descriptors"].get("structure_class", "unknown"))
            by_structure.setdefault(structure, []).append(float(item["optimality_gap"]))
        rows.append(
            {
                "heuristic_name": heuristic_name,
                "mean_training_gap": round(mean_gap, 6),
                "mean_training_runtime_ms": round(mean_runtime, 6),
                "structure_gaps": {
                    key: round(sum(values) / len(values), 6)
                    for key, values in sorted(by_structure.items())
                },
                "components": list(FROZEN_HEURISTICS[heuristic_name]["components"]),
            }
        )
        if best_gap is None or mean_gap < best_gap:
            best_gap = mean_gap
            best_name = heuristic_name
    return {
        "frozen_components": list(PORTFOLIO_COMPONENT_LIBRARY),
        "heuristics": rows,
        "training_best_heuristic": best_name,
    }


def _oracle_results(
    *,
    instances: list[TSPInstance],
    context: Phase8Context,
    seed_base: int,
) -> list[dict[str, Any]]:
    table = _evaluation_table(instances=instances, context=context, seed_base=seed_base)
    results: list[dict[str, Any]] = []
    for instance in instances:
        options = table[instance.name]
        best_name = min(options, key=lambda name: float(options[name]["optimality_gap"]))
        best_result = dict(options[best_name])
        best_result["selected_heuristic"] = best_name
        results.append(best_result)
    return results


def _summarize_panel(
    results: list[dict[str, Any]],
    *,
    panel_name: str,
    oracle_by_instance: dict[str, float] | None = None,
) -> dict[str, Any]:
    if not results:
        return {
            "enabled": False,
            "panel_name": panel_name,
            "instance_count": 0,
            "mean_optimality_gap": 0.0,
            "mean_selector_regret": 0.0,
            "mean_runtime_ms": 0.0,
            "mean_distance_evaluations": 0.0,
            "family_means": [],
            "selected_heuristics": {},
            "worst_instances": [],
        }
    mean_gap = sum(float(item["optimality_gap"]) for item in results) / len(results)
    regrets = [
        float(item["optimality_gap"]) - float(oracle_by_instance.get(str(item["instance"]["name"]), 0.0))
        for item in results
    ] if oracle_by_instance else [0.0 for _ in results]
    mean_runtime = sum(float(item["trace"]["runtime_ms"]) for item in results) / len(results)
    mean_distance = sum(float(item["trace"]["distance_evaluations"]) for item in results) / len(results)
    by_family: dict[str, list[dict[str, Any]]] = {}
    heuristic_counts: dict[str, int] = {}
    for item in results:
        by_family.setdefault(str(item["instance"]["family"]), []).append(item)
        heuristic_name = str(item.get("selected_heuristic") or item.get("scaffold_name") or "")
        heuristic_counts[heuristic_name] = heuristic_counts.get(heuristic_name, 0) + 1
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
            "selector_regret": round(
                float(item["optimality_gap"]) - float(oracle_by_instance.get(str(item["instance"]["name"]), 0.0)),
                6,
            ) if oracle_by_instance else 0.0,
            "expected_gap": round(float(item.get("expected_gap", 0.0)), 6),
            "residual_gap": round(float(item.get("residual_gap", 0.0)), 6),
            "runtime_ms": round(float(item["trace"]["runtime_ms"]), 6),
            "distance_evaluations": int(item["trace"]["distance_evaluations"]),
            "selected_heuristic": str(item.get("selected_heuristic") or item.get("scaffold_name") or ""),
        }
        for item in sorted(results, key=lambda entry: float(entry["optimality_gap"]), reverse=True)[:5]
    ]
    return {
        "enabled": True,
        "panel_name": panel_name,
        "instance_count": len(results),
        "mean_optimality_gap": round(mean_gap, 6),
        "mean_selector_regret": round(sum(regrets) / len(regrets), 6),
        "mean_runtime_ms": round(mean_runtime, 6),
        "mean_distance_evaluations": round(mean_distance, 6),
        "family_means": family_means,
        "selected_heuristics": dict(sorted(heuristic_counts.items())),
        "worst_instances": worst_instances,
    }


def _oracle_gap_lookup(results: list[dict[str, Any]]) -> dict[str, float]:
    return {
        str(item["instance"]["name"]): float(item["optimality_gap"])
        for item in results
    }


def _evaluate_static_panel(
    *,
    selector_fn: Any,
    instances: list[TSPInstance],
    context: Phase8Context,
    panel_name: str,
    seed_base: int,
    difficulty_model: Any | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    oracle_results = _oracle_results(instances=instances, context=context, seed_base=seed_base)
    oracle_lookup = _oracle_gap_lookup(oracle_results)
    results = selector_fn(instances, seed_base)
    if difficulty_model is not None:
        _attach_difficulty_annotations(results, difficulty_model)
    summary = _summarize_panel(results, panel_name=panel_name, oracle_by_instance=oracle_lookup)
    return summary, results, oracle_results


def _combined_final_evaluation(
    *,
    selector_fn: Any,
    context: Phase8Context,
    seed_base: int,
) -> dict[str, Any]:
    tsplib_summary, tsplib_results, tsplib_oracle = _evaluate_static_panel(
        selector_fn=selector_fn,
        instances=context.bundle.holdout,
        context=context,
        panel_name="heldout_tsplib",
        seed_base=seed_base,
        difficulty_model=context.difficulty_model,
    )
    family_panels: list[dict[str, Any]] = []
    family_results: dict[str, list[dict[str, Any]]] = {}
    oracle_family_results: dict[str, list[dict[str, Any]]] = {}
    for family_index, (family_name, instances) in enumerate(sorted(context.validation_families.items())):
        summary, results, oracle_results = _evaluate_static_panel(
            selector_fn=selector_fn,
            instances=instances,
            context=context,
            panel_name=family_name,
            seed_base=seed_base + 50_000 + (family_index * 10_000),
            difficulty_model=context.difficulty_model,
        )
        family_panels.append(summary)
        family_results[family_name] = results
        oracle_family_results[family_name] = oracle_results
    family_gap = (
        sum(float(panel["mean_optimality_gap"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
        / max(1, sum(int(panel["instance_count"]) for panel in family_panels))
    ) if family_panels else 0.0
    family_regret = (
        sum(float(panel["mean_selector_regret"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
        / max(1, sum(int(panel["instance_count"]) for panel in family_panels))
    ) if family_panels else 0.0
    family_runtime = (
        sum(float(panel["mean_runtime_ms"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
        / max(1, sum(int(panel["instance_count"]) for panel in family_panels))
    ) if family_panels else 0.0
    mean_transfer = (
        (float(tsplib_summary["mean_optimality_gap"]) * max(1, len(context.bundle.holdout)))
        + sum(float(panel["mean_optimality_gap"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
    ) / max(1, len(context.bundle.holdout) + sum(int(panel["instance_count"]) for panel in family_panels))
    mean_transfer_regret = (
        (float(tsplib_summary["mean_selector_regret"]) * max(1, len(context.bundle.holdout)))
        + sum(float(panel["mean_selector_regret"]) * max(1, int(panel["instance_count"])) for panel in family_panels)
    ) / max(1, len(context.bundle.holdout) + sum(int(panel["instance_count"]) for panel in family_panels))
    return {
        "panels": [tsplib_summary, *family_panels],
        "results": {
            "heldout_tsplib": tsplib_results,
            "heldout_tsplib_oracle": tsplib_oracle,
            "validation_families": family_results,
            "validation_family_oracles": oracle_family_results,
        },
        "combined": {
            "mean_tsplib_gap": round(float(tsplib_summary["mean_optimality_gap"]), 6),
            "mean_tsplib_runtime_ms": round(float(tsplib_summary["mean_runtime_ms"]), 6),
            "mean_tsplib_selector_regret": round(float(tsplib_summary["mean_selector_regret"]), 6),
            "mean_family_gap": round(family_gap, 6),
            "mean_family_runtime_ms": round(family_runtime, 6),
            "mean_family_selector_regret": round(family_regret, 6),
            "mean_transfer_gap": round(mean_transfer, 6),
            "mean_selector_regret": round(mean_transfer_regret, 6),
        },
    }


def _selector_from_fixed_heuristic(heuristic_name: str) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        return [
            run_fixed_heuristic(instance, heuristic_name, seed=seed_base + index)
            for index, instance in enumerate(instances)
        ]
    return select


def _selector_from_random_portfolio(context: Phase8Context) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        table = _evaluation_table(instances=instances, context=context, seed_base=seed_base)
        results: list[dict[str, Any]] = []
        for index, instance in enumerate(instances):
            chosen = random_portfolio_choice(context.heuristic_names, seed=seed_base + index)
            results.append(table[instance.name][chosen])
        return results
    return select


def _selector_from_oracle(context: Phase8Context) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        return _oracle_results(instances=instances, context=context, seed_base=seed_base)
    return select


def _selector_from_supervised(context: Phase8Context) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        table = _evaluation_table(instances=instances, context=context, seed_base=seed_base)
        results: list[dict[str, Any]] = []
        for instance in instances:
            chosen = context.knn_selector.select(instance)
            results.append(table[instance.name][chosen])
        return results
    return select


def _selector_from_controller(controller_spec: dict[str, Any], *, allow_online_state: bool = True) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        return [
            run_controller(instance, controller_spec, seed=seed_base + index, allow_online_state=allow_online_state)
            for index, instance in enumerate(instances)
        ]
    return select


def _selector_from_static_controller(controller_spec: dict[str, Any]) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        return [
            run_static_controller(instance, controller_spec, seed=seed_base + index)
            for index, instance in enumerate(instances)
        ]
    return select


def _run_timed_full_solver(instance: TSPInstance, heuristic_spec: dict[str, Any], *, seed: int) -> dict[str, Any]:
    started = perf_counter()
    result = dict(solve_full_solver_instance(instance, heuristic_spec, seed=seed))
    elapsed_ms = (perf_counter() - started) * 1000.0
    trace = dict(result.get("trace", {}))
    trace["runtime_ms"] = round(elapsed_ms, 6)
    trace.setdefault("distance_evaluations", 0)
    result["trace"] = trace
    result["selected_heuristic"] = str(result.get("heuristic_name", heuristic_spec.get("name", "")))
    return result


def _selector_from_full_solver_spec(heuristic_spec: dict[str, Any]) -> Any:
    def select(instances: list[TSPInstance], seed_base: int) -> list[dict[str, Any]]:
        return [
            _run_timed_full_solver(instance, heuristic_spec, seed=seed_base + index)
            for index, instance in enumerate(instances)
        ]

    return select


def _evaluate_controller_panel(
    *,
    controller_spec: dict[str, Any],
    instances: list[TSPInstance],
    context: Phase8Context,
    panel_name: str,
    seed_base: int,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
    allow_online_state: bool = True,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    selector_fn = _selector_from_controller(controller_spec, allow_online_state=allow_online_state)
    summary, results, _ = _evaluate_static_panel(
        selector_fn=selector_fn,
        instances=instances,
        context=context,
        panel_name=panel_name,
        seed_base=seed_base,
        difficulty_model=context.difficulty_model,
    )
    if incumbent_spec is not None and tolerance is not None:
        incumbent_fn = _selector_from_controller(incumbent_spec, allow_online_state=allow_online_state)
        incumbent_summary, _, _ = _evaluate_static_panel(
            selector_fn=incumbent_fn,
            instances=instances,
            context=context,
            panel_name=panel_name,
            seed_base=seed_base + 10_000,
            difficulty_model=context.difficulty_model,
        )
        baseline_mean = float(incumbent_summary["mean_optimality_gap"])
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, results


def _evaluate_transfer_probe(
    *,
    controller_spec: dict[str, Any],
    holdout_instances: list[TSPInstance],
    adversarial_instances: list[TSPInstance],
    context: Phase8Context,
    seed_base: int,
    incumbent_spec: dict[str, Any] | None = None,
    tolerance: float | None = None,
    allow_online_state: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    holdout_summary, holdout_results = _evaluate_controller_panel(
        controller_spec=controller_spec,
        instances=holdout_instances,
        context=context,
        panel_name="heldout_probe",
        seed_base=seed_base,
        allow_online_state=allow_online_state,
    )
    adversarial_summary, adversarial_results = _evaluate_controller_panel(
        controller_spec=controller_spec,
        instances=adversarial_instances,
        context=context,
        panel_name="adversarial_probe",
        seed_base=seed_base + 20_000,
        allow_online_state=allow_online_state,
    )
    combined_results = holdout_results + adversarial_results
    combined_oracle = _oracle_gap_lookup(
        _oracle_results(instances=holdout_instances, context=context, seed_base=seed_base)
        + _oracle_results(instances=adversarial_instances, context=context, seed_base=seed_base + 20_000)
    )
    summary = _summarize_panel(combined_results, panel_name="transfer_probe", oracle_by_instance=combined_oracle)
    summary["panels"] = [holdout_summary, adversarial_summary]
    if incumbent_spec is not None and tolerance is not None:
        incumbent_fn = _selector_from_controller(incumbent_spec, allow_online_state=allow_online_state)
        incumbent_results = incumbent_fn(holdout_instances + adversarial_instances, seed_base + 50_000)
        _attach_difficulty_annotations(incumbent_results, context.difficulty_model)
        incumbent_summary = _summarize_panel(incumbent_results, panel_name="transfer_probe", oracle_by_instance=combined_oracle)
        baseline_mean = float(incumbent_summary["mean_optimality_gap"])
        candidate_mean = float(summary["mean_optimality_gap"])
        summary["baseline_mean_optimality_gap"] = baseline_mean
        summary["gap_delta"] = round(candidate_mean - baseline_mean, 6)
        summary["passed"] = bool(candidate_mean <= baseline_mean + float(tolerance))
    return summary, holdout_summary, holdout_results, adversarial_summary, adversarial_results


def _build_static_payload(
    *,
    config: Phase8ConditionConfig,
    condition_dir: Path,
    execution_mode: str,
    selector_fn: Any,
    selected_fixed_heuristic: str = "",
    controller_spec: dict[str, Any] | None = None,
    context: Phase8Context,
) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    final_evaluation = _combined_final_evaluation(
        selector_fn=selector_fn,
        context=context,
        seed_base=config.seed + 900_000,
    )
    payload = {
        "condition_name": config.name,
        "execution_mode": execution_mode,
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": config.benchmark.__dict__,
        "portfolio": config.portfolio.__dict__,
        "optimization": config.optimization.__dict__,
        "metadata": config.metadata,
        "epochs": [],
        "accepted_controller_spec": controller_spec,
        "accepted_controller_code": None,
        "controller_signature": controller_signature(controller_spec or {}) if controller_spec else "",
        "selected_fixed_heuristic": selected_fixed_heuristic,
        "final_evaluation": final_evaluation,
        "difficulty_model": {
            "reference_summary": baseline_reference_summary(context.difficulty_model),
            "reference_count": len(context.difficulty_model.references),
            "neighbor_count": context.difficulty_model.neighbor_count,
        },
    }
    _json_dump(condition_dir / "condition_summary.json", payload)
    return payload


def _build_best_fixed_payload(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    return _build_static_payload(
        config=config,
        condition_dir=condition_dir,
        execution_mode="best_fixed",
        selector_fn=_selector_from_fixed_heuristic(context.train_best_heuristic),
        selected_fixed_heuristic=context.train_best_heuristic,
        context=context,
    )


def _build_random_payload(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    return _build_static_payload(
        config=config,
        condition_dir=condition_dir,
        execution_mode="random_portfolio",
        selector_fn=_selector_from_random_portfolio(context),
        context=context,
    )


def _build_oracle_payload(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    return _build_static_payload(
        config=config,
        condition_dir=condition_dir,
        execution_mode="oracle_selector",
        selector_fn=_selector_from_oracle(context),
        context=context,
    )


def _build_supervised_payload(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    return _build_static_payload(
        config=config,
        condition_dir=condition_dir,
        execution_mode="supervised_selector",
        selector_fn=_selector_from_supervised(context),
        context=context,
    )


def _build_static_selector_payload(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_generation_prompt(
        epoch_index=1,
        history=[],
        training_panel=[summarize_instance(instance) for instance in context.bundle.train],
        heuristic_catalog=heuristic_catalog(),
        heuristic_reference=context.heuristic_reference,
        single_shot=True,
        include_online_state=False,
    )
    generation_result = generate_code(
        provider=config.agent.provider,
        model=config.agent.model,
        system_prompt=config.agent.system_prompt,
        user_prompt=prompt,
        temperature=config.agent.temperature,
        max_tokens=config.agent.max_tokens,
        repair_invalid_submissions=config.generation.repair_invalid_submissions,
    )
    materialized = materialize_controller(str(generation_result.submitted_code or generation_result.code))
    controller_spec = dict(materialized.controller_spec)
    payload = _build_static_payload(
        config=config,
        condition_dir=condition_dir,
        execution_mode="static_selector",
        selector_fn=_selector_from_static_controller(controller_spec),
        controller_spec=controller_spec,
        context=context,
    )
    payload["accepted_controller_code"] = materialized.executed_code
    payload["prompt"] = prompt
    payload["raw_response"] = generation_result.raw_text
    payload["generation_error"] = generation_result.error
    payload["validation_issues"] = generation_result.validation_issues
    payload["materialization_issues"] = materialized.issues
    payload["materialization_used_fallback"] = materialized.used_fallback
    payload["controller_rule_summary"] = controller_rule_summary(controller_spec)
    _json_dump(condition_dir / "condition_summary.json", payload)
    return payload


def _recover_full_solver_spec(full_payload: dict[str, Any]) -> dict[str, Any]:
    accepted_spec = None
    last_seen_spec = None
    for epoch in full_payload.get("epochs", []):
        spec = epoch.get("heuristic_spec")
        if not spec:
            continue
        last_seen_spec = spec
        if bool((epoch.get("selection") or {}).get("accepted", False)):
            accepted_spec = spec
    chosen = accepted_spec or last_seen_spec or {}
    return canonicalize_heuristic_spec(chosen)


def _build_full_solver_payload(
    config: Phase8ConditionConfig,
    condition_dir: Path,
    context: Phase8Context,
) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    full_payload = run_full_solver_condition(_as_full_solver_config(config), condition_dir)
    full_payload["execution_mode"] = "full_solver"
    final_spec = _recover_full_solver_spec(full_payload)
    final_evaluation = _combined_final_evaluation(
        selector_fn=_selector_from_full_solver_spec(final_spec),
        context=context,
        seed_base=config.seed + 900_000,
    )
    full_payload["final_evaluation"] = final_evaluation
    full_payload["accepted_controller_spec"] = None
    full_payload["controller_signature"] = ""
    full_payload["selected_fixed_heuristic"] = ""
    _json_dump(condition_dir / "condition_summary.json", full_payload)
    return full_payload


def _as_full_solver_config(config: Phase8ConditionConfig) -> Any:
    from llm_tsp.config import TSPConditionConfig

    data = {
        "name": config.name,
        "seed": config.seed,
        "output_root": config.output_root,
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": {
            "manifest_path": config.benchmark.manifest_path,
            "curriculum_batch_size": config.benchmark.curriculum_batch_size,
            "transfer_probe_count": config.benchmark.transfer_probe_count,
            "adversarial_probe_count": config.benchmark.adversarial_probe_count,
        },
        "optimization": config.optimization.__dict__,
        "judge": config.judge.__dict__,
        "metadata": {**config.metadata, "phase8_wrapper": True},
    }
    return TSPConditionConfig.from_dict(data)


def _build_phase8_context(config: Phase8ConditionConfig) -> Phase8Context:
    bundle = load_benchmark_bundle(Path(config.benchmark.manifest_path))
    validation_families = _select_validation_families(
        load_validation_families(config.benchmark.manifest_path),
        max_family_count=int(config.benchmark.validation_family_count),
    )
    difficulty_model = build_difficulty_model(bundle.train + bundle.adversarial, seed_base=config.seed + 700_000)
    names = list(config.portfolio.heuristic_names or heuristic_names())
    cache: dict[tuple[str, ...], dict[str, dict[str, dict[str, Any]]]] = {}
    train_table = _evaluation_table(
        instances=bundle.train,
        context=Phase8Context(bundle, validation_families, difficulty_model, names, {}, cache, "", None),
        seed_base=config.seed + int(config.portfolio.reference_seed_stride),
    )
    heuristic_reference = _heuristic_reference_summary(bundle.train, train_table, names)
    training_best = str(heuristic_reference["training_best_heuristic"])
    knn_selector = fit_knn_selector(
        training_instances=bundle.train,
        heuristic_names_list=names,
        evaluation_table=train_table,
        neighbor_count=int(config.portfolio.k_neighbors),
    )
    return Phase8Context(
        bundle=bundle,
        validation_families=validation_families,
        difficulty_model=difficulty_model,
        heuristic_names=names,
        heuristic_reference=heuristic_reference,
        train_table=cache,
        train_best_heuristic=training_best,
        knn_selector=knn_selector,
    )


def run_adaptive_condition(config: Phase8ConditionConfig, condition_dir: Path, context: Phase8Context) -> dict[str, Any]:
    condition_dir.mkdir(parents=True, exist_ok=True)
    state = build_curriculum_state(
        config,
        context.bundle.adversarial,
        reference_instances=context.bundle.train + context.bundle.adversarial,
        difficulty_model=context.difficulty_model,
    )
    history: list[dict[str, Any]] = []
    generation_cache: dict[str, str] = {}
    training_gap_series: list[float] = []
    transfer_gap_series: list[float] = []

    latest_controller_spec: dict[str, Any] | None = None
    latest_executed_code = None
    for epoch_index in range(1, int(config.optimization.epochs) + 1):
        epoch_dir = condition_dir / "epochs" / f"epoch_{epoch_index:03d}"
        epoch_dir.mkdir(parents=True, exist_ok=True)
        state["selection_epoch_cursor"] = epoch_index
        training_instances = _instance_panel(context.bundle.train, epoch_index=epoch_index, count=int(config.benchmark.curriculum_batch_size))
        training_panel_summary = []
        for instance in training_instances:
            summary = summarize_instance(instance)
            summary["expected_gap"] = round(expected_gap(context.difficulty_model, instance), 6)
            training_panel_summary.append(summary)
        prompt_context = build_prompt_context(config, state)
        prompt = build_generation_prompt(
            epoch_index=epoch_index,
            history=history,
            training_panel=training_panel_summary,
            heuristic_catalog=heuristic_catalog(),
            heuristic_reference=context.heuristic_reference,
            curriculum_context=prompt_context,
            include_online_state=bool(config.portfolio.enable_online_state),
            single_shot=False,
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

        materialized = materialize_controller(submitted_code)
        executed_code = str(materialized.executed_code or submitted_code)
        controller_spec = dict(materialized.controller_spec)
        latest_controller_spec = controller_spec
        latest_executed_code = executed_code

        training_summary, training_results = _evaluate_controller_panel(
            controller_spec=controller_spec,
            instances=training_instances,
            context=context,
            panel_name="training",
            seed_base=config.seed + (epoch_index * 1_000),
            allow_online_state=bool(config.portfolio.enable_online_state),
        )
        descriptor = portfolio_descriptor(training_results)
        code_fingerprint = fingerprint_record(executed_code)
        incumbent = state.get("incumbent")
        candidate_novelty = 0.0
        if history:
            previous_code = str(history[-1].get("accepted_controller_code") or history[-1].get("executed_code") or "")
            candidate_novelty = round(1.0 - code_similarity(previous_code, executed_code), 6)

        replay_probe_summary = None
        replay_instances = [instance_from_dict(item["instance"]) for item in replay_pool(config, state)]
        incumbent_spec = incumbent.get("controller_spec") if incumbent else None
        if replay_instances and incumbent_spec is not None:
            replay_probe_summary, _ = _evaluate_controller_panel(
                controller_spec=controller_spec,
                instances=replay_instances,
                context=context,
                panel_name="replay_probe",
                seed_base=config.seed + 200_000 + (epoch_index * 1_000),
                incumbent_spec=incumbent_spec,
                tolerance=float(config.selection.replay_gap_tolerance),
                allow_online_state=bool(config.portfolio.enable_online_state),
            )

        holdout_probe_instances = _instance_panel(context.bundle.holdout, epoch_index=epoch_index, count=int(config.benchmark.transfer_probe_count))
        adversarial_probe_instances = _instance_panel(context.bundle.adversarial, epoch_index=epoch_index, count=int(config.benchmark.adversarial_probe_count))
        (
            transfer_probe_summary,
            holdout_probe_summary,
            _holdout_probe_results,
            adversarial_probe_summary,
            adversarial_probe_results,
        ) = _evaluate_transfer_probe(
            controller_spec=controller_spec,
            holdout_instances=holdout_probe_instances,
            adversarial_instances=adversarial_probe_instances,
            context=context,
            seed_base=config.seed + 400_000 + (epoch_index * 1_000),
            incumbent_spec=incumbent_spec,
            tolerance=float(config.selection.transfer_gap_tolerance) if incumbent_spec is not None else None,
            allow_online_state=bool(config.portfolio.enable_online_state),
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
            state["incumbent"]["controller_spec"] = controller_spec
            state["incumbent"]["complexity_score"] = code_fingerprint["complexity_score"]
            state["incumbent"]["mean_runtime_ms"] = float(training_summary["mean_runtime_ms"])
            state["incumbent"]["mean_training_gap"] = float(training_summary["mean_optimality_gap"])

        training_gap_series.append(float(training_summary["mean_optimality_gap"]))
        transfer_gap_series.append(float(transfer_probe_summary["mean_optimality_gap"]))

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
            "controller_spec": controller_spec,
            "controller_signature": controller_signature(controller_spec),
            "controller_rule_summary": controller_rule_summary(controller_spec),
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
            "accepted_controller_code": (state.get("incumbent") or {}).get("code"),
        }
        history.append(epoch_payload)
        _json_dump(epoch_dir / "artifact.json", epoch_payload)

    incumbent = state.get("incumbent")
    final_spec = incumbent.get("controller_spec") if incumbent else latest_controller_spec
    final_code = incumbent.get("code") if incumbent else latest_executed_code
    if not bool(config.portfolio.enable_online_state):
        final_evaluation = _combined_final_evaluation(
            selector_fn=_selector_from_static_controller(final_spec or {}),
            context=context,
            seed_base=config.seed + 900_000,
        )
    else:
        final_evaluation = _combined_final_evaluation(
            selector_fn=_selector_from_controller(final_spec or {}, allow_online_state=True),
            context=context,
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
        "execution_mode": "adaptive_controller",
        "agent": config.agent.__dict__,
        "generation": config.generation.__dict__,
        "replay": config.replay.__dict__,
        "selection": config.selection.__dict__,
        "benchmark": config.benchmark.__dict__,
        "portfolio": config.portfolio.__dict__,
        "optimization": config.optimization.__dict__,
        "metadata": config.metadata,
        "difficulty_model": {
            "reference_summary": baseline_reference_summary(context.difficulty_model),
            "reference_count": len(context.difficulty_model.references),
            "neighbor_count": context.difficulty_model.neighbor_count,
        },
        "epochs": history,
        "accepted_controller_spec": final_spec,
        "accepted_controller_code": final_code,
        "controller_signature": controller_signature(final_spec or {}),
        "controller_rule_summary": controller_rule_summary(final_spec or {}),
        "selected_fixed_heuristic": "",
        "final_evaluation": final_evaluation,
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
    return condition_payload


def build_judge_prompt(suite_summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are reviewing a TSP adaptive heuristic portfolio suite.",
            "Interpret results conservatively and prioritize held-out TSPLIB gap, selector regret versus the oracle portfolio, runtime-adjusted gap, Pareto efficiency, and cross-family transfer.",
            "",
            "Rules:",
            "- The primary endpoint is held-out TSPLIB gap.",
            "- The oracle selector is an upper bound, not a deployable baseline.",
            "- Prefer claims about interpretable instance-adaptive control when static or adaptive selectors approach the oracle without excessive runtime inflation.",
            "- Do not claim new algorithm discovery; this phase is about hyper-heuristic control over known heuristics.",
            "",
            json.dumps(suite_summary, indent=2, sort_keys=True),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the phase-8 adaptive heuristic portfolio TSP suite.")
    parser.add_argument("--config", default="configs/tsp_phase8_suite/01_adaptive_portfolio.json", help="Path to the phase-8 suite config JSON.")
    parser.add_argument("--output-root", default=None, help="Optional override for the output root directory.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Add this offset to every condition seed.")
    parser.add_argument("--replicate-label", default=None, help="Optional replicate label.")
    parser.add_argument("--skip-judge", action="store_true", help="Skip the final analysis model call.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    load_env_files(project_root)
    suite = Phase8SuiteConfig.load(project_root / args.config)
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

    base_context = _build_phase8_context(suite.conditions[0])
    condition_payloads = []
    for condition in suite.conditions:
        condition_dir = run_dir / condition.name
        if condition.execution.mode == "best_fixed":
            condition_payloads.append(_build_best_fixed_payload(condition, condition_dir, base_context))
        elif condition.execution.mode == "random_portfolio":
            condition_payloads.append(_build_random_payload(condition, condition_dir, base_context))
        elif condition.execution.mode == "oracle_selector":
            condition_payloads.append(_build_oracle_payload(condition, condition_dir, base_context))
        elif condition.execution.mode == "supervised_selector":
            condition_payloads.append(_build_supervised_payload(condition, condition_dir, base_context))
        elif condition.execution.mode == "static_selector":
            condition_payloads.append(_build_static_selector_payload(condition, condition_dir, base_context))
        elif condition.execution.mode == "full_solver":
            condition_payloads.append(_build_full_solver_payload(condition, condition_dir, base_context))
        else:
            condition_payloads.append(run_adaptive_condition(condition, condition_dir, base_context))

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
    print(f"Completed phase-8 portfolio suite. Results written to: {run_dir}")


if __name__ == "__main__":
    main()
