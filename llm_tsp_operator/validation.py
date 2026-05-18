from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm_tsp.benchmark import _load_manifest_group, TSPInstance
from llm_tsp.code_features import complexity_score, fingerprint_record

from .operator_schema import novelty_classification, operator_pseudocode, operator_signature
from .scaffold_engine import SCAFFOLD_LIBRARY, solve_with_portfolio, solve_with_scaffold


def load_validation_families(manifest_path: str | Path) -> dict[str, list[TSPInstance]]:
    manifest_path = Path(manifest_path)
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    families: dict[str, list[TSPInstance]] = {}
    for family_name, records in (raw.get("phase7_validation_families") or {}).items():
        families[str(family_name)] = _load_manifest_group(root, list(records))
    return families


def validate_operator_candidate(
    *,
    operator_code: str,
    operator_spec: dict[str, Any],
    holdout_instances: list[TSPInstance],
    family_panels: dict[str, list[TSPInstance]],
    host_scaffold: str,
    validation_config: Any,
    seed_base: int,
) -> dict[str, Any]:
    scaffold_names = [name for name in validation_config.scaffold_names if name in SCAFFOLD_LIBRARY]
    transplant = _transplant_test(
        operator_spec=operator_spec,
        scaffold_names=scaffold_names,
        instances=holdout_instances,
        seed_base=seed_base,
    )
    family_test = _family_test(
        operator_spec=operator_spec,
        host_scaffold=host_scaffold,
        holdout_instances=holdout_instances,
        family_panels=family_panels,
        seed_base=seed_base + 200_000,
    )
    ablation = _ablation_test(
        operator_spec=operator_spec,
        host_scaffold=host_scaffold,
        holdout_instances=holdout_instances,
        family_panels=family_panels,
        seed_base=seed_base + 400_000,
    )
    pareto = _pareto_summary(
        host_scaffold=host_scaffold,
        operator_spec=operator_spec,
        holdout_instances=holdout_instances,
        family_panels=family_panels,
        code=operator_code,
        seed_base=seed_base + 600_000,
    )
    family_signal = _family_signal(family_test)
    ablation_signal = _ablation_signal(ablation)
    surviving = bool(
        transplant["mean_gap_delta"] <= -float(validation_config.survivor_min_transplant_gain)
        and transplant["positive_scaffold_count"] >= int(validation_config.survivor_min_scaffold_wins)
        and pareto["runtime_inflation"] <= float(validation_config.survivor_max_runtime_inflation)
        and family_signal["best_family_gain"] >= float(validation_config.survivor_min_family_gain)
        and family_signal["severe_regression_count"] <= int(validation_config.survivor_max_severe_family_regressions)
        and ablation_signal["disabled_gap_delta_vs_full"] >= float(validation_config.survivor_min_disabled_ablation_drop)
    )
    report = {
        "operator_name": str(operator_spec.get("name", "unnamed_operator")),
        "operator_type": str(operator_spec.get("operator_type", "candidate_ranker")),
        "core_idea": str(operator_spec.get("description", "")),
        "host_scaffold": host_scaffold,
        "problem_class_where_it_helps": family_signal["helpful_families"],
        "pseudocode": operator_pseudocode(operator_spec),
        "complexity": {
            "code_length_lines": _non_empty_line_count(operator_code),
            "complexity_score": complexity_score(operator_code),
            "fingerprint": fingerprint_record(operator_code)["fingerprint"],
        },
        "why_it_should_help": _why_it_should_help(operator_spec),
        "failure_cases": _failure_cases(
            family_test=family_test,
            transplant=transplant,
            family_signal=family_signal,
            ablation_signal=ablation_signal,
            pareto=pareto,
        ),
        "transplant_results": transplant,
        "instance_family_results": family_test,
        "family_signal": family_signal,
        "pareto_results": pareto,
        "ablation_results": ablation,
        "ablation_signal": ablation_signal,
        "novelty_classification": novelty_classification(operator_spec),
        "rediscovery_signature": operator_signature(operator_spec),
        "surviving_candidate": surviving,
    }
    return report


def render_operator_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Operator Discovery Report: {report.get('operator_name', 'unnamed_operator')}",
        "",
        f"- Operator type: `{report.get('operator_type', 'unknown')}`.",
        f"- Host scaffold: `{report.get('host_scaffold', 'unknown')}`.",
        f"- Core idea: {report.get('core_idea', '')}",
        f"- Novelty classification: `{report.get('novelty_classification', 'unknown')}`.",
        f"- Rediscovery signature: `{report.get('rediscovery_signature', 'unknown')}`.",
        f"- Surviving candidate: `{report.get('surviving_candidate', False)}`.",
        f"- Problem class where it helps: `{', '.join(report.get('problem_class_where_it_helps', [])) or 'none confirmed'}`.",
        "",
        "## Pseudocode",
        *[f"- {line}" for line in report.get("pseudocode", [])],
        "",
        "## Complexity",
        f"- Non-empty lines: {report.get('complexity', {}).get('code_length_lines', 0)}.",
        f"- Complexity score: {report.get('complexity', {}).get('complexity_score', 0.0)}.",
        f"- Fingerprint: `{report.get('complexity', {}).get('fingerprint', '')}`.",
        "",
        "## Why It Should Help",
        f"- {report.get('why_it_should_help', '')}",
        "",
        "## Failure Cases",
        *[f"- {item}" for item in report.get("failure_cases", [])],
        "",
        "## Transplant Results",
    ]
    for item in report.get("transplant_results", {}).get("scaffolds", []):
        lines.append(
            f"- `{item['scaffold_name']}` gap delta `{item['mean_gap_delta']}`, runtime delta `{item['mean_runtime_delta']}`, distance-eval delta `{item['mean_distance_eval_delta']}`."
        )
    lines.extend(
        [
            "",
            "## Instance-Family Results",
        ]
    )
    for item in report.get("instance_family_results", {}).get("families", []):
        lines.append(
            f"- `{item['family_name']}` operator gap `{item['operator_mean_gap']}` vs baseline `{item['baseline_mean_gap']}`."
        )
    lines.extend(
        [
            "",
            "## Pareto Results",
            f"- Gap delta: {report.get('pareto_results', {}).get('gap_delta', 0.0)}.",
            f"- Runtime inflation: {report.get('pareto_results', {}).get('runtime_inflation', 0.0)}.",
            f"- Distance-evaluation inflation: {report.get('pareto_results', {}).get('distance_eval_inflation', 0.0)}.",
            f"- Same-gap-faster flag: `{report.get('pareto_results', {}).get('same_gap_faster', False)}`.",
            f"- Better-gap-same-runtime flag: `{report.get('pareto_results', {}).get('better_gap_same_runtime', False)}`.",
            "",
            "## Ablation Results",
        ]
    )
    for item in report.get("ablation_results", {}).get("variants", []):
        lines.append(
            f"- `{item['variant_name']}` mean gap `{item['mean_gap']}` and delta vs full operator `{item['gap_delta_vs_full']}`."
        )
    return "\n".join(lines).strip() + "\n"


def _transplant_test(
    *,
    operator_spec: dict[str, Any],
    scaffold_names: list[str],
    instances: list[TSPInstance],
    seed_base: int,
) -> dict[str, Any]:
    scaffold_summaries: list[dict[str, Any]] = []
    positive = 0
    selector_results = None
    selector_runtime = 0.0
    selector_distance = 0.0
    selector_mode = str(operator_spec.get("operator_type", "")) == "scaffold_selector"
    if selector_mode:
        selector_results = [
            solve_with_portfolio(instance, operator_spec, seed=seed_base + index, candidate_scaffolds=scaffold_names)
            for index, instance in enumerate(instances)
        ]
        selector_runtime = _mean(item["trace"]["runtime_ms"] for item in selector_results)
        selector_distance = _mean(item["trace"]["distance_evaluations"] for item in selector_results)
    for scaffold_index, scaffold_name in enumerate(scaffold_names):
        if selector_results is None:
            operator_results = [
                solve_with_scaffold(instance, scaffold_name, operator_spec, seed=seed_base + (scaffold_index * 10_000) + index)
                for index, instance in enumerate(instances)
            ]
            operator_runtime = _mean(item["trace"]["runtime_ms"] for item in operator_results)
            operator_distance = _mean(item["trace"]["distance_evaluations"] for item in operator_results)
        else:
            operator_results = selector_results
            operator_runtime = selector_runtime
            operator_distance = selector_distance
        baseline_results = [
            solve_with_scaffold(instance, scaffold_name, None, seed=seed_base + 50_000 + (scaffold_index * 10_000) + index)
            for index, instance in enumerate(instances)
        ]
        operator_gap = _mean(item["optimality_gap"] for item in operator_results)
        baseline_gap = _mean(item["optimality_gap"] for item in baseline_results)
        baseline_runtime = _mean(item["trace"]["runtime_ms"] for item in baseline_results)
        baseline_distance = _mean(item["trace"]["distance_evaluations"] for item in baseline_results)
        gap_delta = operator_gap - baseline_gap
        if gap_delta < 0.0:
            positive += 1
        scaffold_summaries.append(
            {
                "scaffold_name": scaffold_name,
                "operator_mean_gap": round(operator_gap, 6),
                "baseline_mean_gap": round(baseline_gap, 6),
                "mean_gap_delta": round(gap_delta, 6),
                "mean_runtime_delta": round(operator_runtime - baseline_runtime, 6),
                "mean_distance_eval_delta": round(operator_distance - baseline_distance, 6),
            }
        )
    return {
        "scaffolds": scaffold_summaries,
        "positive_scaffold_count": positive,
        "mean_gap_delta": round(_mean(item["mean_gap_delta"] for item in scaffold_summaries), 6),
    }


def _family_test(
    *,
    operator_spec: dict[str, Any],
    host_scaffold: str,
    holdout_instances: list[TSPInstance],
    family_panels: dict[str, list[TSPInstance]],
    seed_base: int,
) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    families.append(
        _family_summary(
            family_name="heldout_tsplib",
            instances=holdout_instances,
            host_scaffold=host_scaffold,
            operator_spec=operator_spec,
            seed_base=seed_base,
        )
    )
    for family_index, (family_name, instances) in enumerate(sorted(family_panels.items())):
        families.append(
            _family_summary(
                family_name=family_name,
                instances=instances,
                host_scaffold=host_scaffold,
                operator_spec=operator_spec,
                seed_base=seed_base + ((family_index + 1) * 10_000),
            )
        )
    return {
        "families": families,
        "mean_gap_delta": round(_mean(item["gap_delta"] for item in families), 6),
    }


def _family_summary(
    *,
    family_name: str,
    instances: list[TSPInstance],
    host_scaffold: str,
    operator_spec: dict[str, Any],
    seed_base: int,
) -> dict[str, Any]:
    operator_results = [
        _solve_operator_instance(
            instance=instance,
            host_scaffold=host_scaffold,
            operator_spec=operator_spec,
            seed=seed_base + index,
        )
        for index, instance in enumerate(instances)
    ]
    baseline_results = [
        solve_with_scaffold(instance, host_scaffold, None, seed=seed_base + 5_000 + index)
        for index, instance in enumerate(instances)
    ]
    operator_gap = _mean(item["optimality_gap"] for item in operator_results)
    baseline_gap = _mean(item["optimality_gap"] for item in baseline_results)
    return {
        "family_name": family_name,
        "instance_count": len(instances),
        "operator_mean_gap": round(operator_gap, 6),
        "baseline_mean_gap": round(baseline_gap, 6),
        "gap_delta": round(operator_gap - baseline_gap, 6),
        "operator_mean_runtime_ms": round(_mean(item["trace"]["runtime_ms"] for item in operator_results), 6),
        "baseline_mean_runtime_ms": round(_mean(item["trace"]["runtime_ms"] for item in baseline_results), 6),
    }


def _pareto_summary(
    *,
    host_scaffold: str,
    operator_spec: dict[str, Any],
    holdout_instances: list[TSPInstance],
    family_panels: dict[str, list[TSPInstance]],
    code: str,
    seed_base: int,
) -> dict[str, Any]:
    evaluation_pool = list(holdout_instances)
    for instances in family_panels.values():
        evaluation_pool.extend(instances)
    operator_results = [
        _solve_operator_instance(
            instance=instance,
            host_scaffold=host_scaffold,
            operator_spec=operator_spec,
            seed=seed_base + index,
        )
        for index, instance in enumerate(evaluation_pool)
    ]
    baseline_results = [
        solve_with_scaffold(instance, host_scaffold, None, seed=seed_base + 20_000 + index)
        for index, instance in enumerate(evaluation_pool)
    ]
    operator_gap = _mean(item["optimality_gap"] for item in operator_results)
    baseline_gap = _mean(item["optimality_gap"] for item in baseline_results)
    operator_runtime = _mean(item["trace"]["runtime_ms"] for item in operator_results)
    baseline_runtime = _mean(item["trace"]["runtime_ms"] for item in baseline_results)
    operator_distance = _mean(item["trace"]["distance_evaluations"] for item in operator_results)
    baseline_distance = _mean(item["trace"]["distance_evaluations"] for item in baseline_results)
    gap_delta = operator_gap - baseline_gap
    runtime_inflation = (operator_runtime - baseline_runtime) / max(1e-9, baseline_runtime)
    distance_inflation = (operator_distance - baseline_distance) / max(1.0, baseline_distance)
    return {
        "gap_delta": round(gap_delta, 6),
        "runtime_inflation": round(runtime_inflation, 6),
        "distance_eval_inflation": round(distance_inflation, 6),
        "same_gap_faster": bool(gap_delta <= 0.001 and runtime_inflation < 0.0),
        "better_gap_same_runtime": bool(gap_delta < 0.0 and runtime_inflation <= 0.05),
        "code_length_lines": _non_empty_line_count(code),
        "complexity_score": complexity_score(code),
    }


def _ablation_test(
    *,
    operator_spec: dict[str, Any],
    host_scaffold: str,
    holdout_instances: list[TSPInstance],
    family_panels: dict[str, list[TSPInstance]],
    seed_base: int,
) -> dict[str, Any]:
    evaluation_pool: list[TSPInstance] = list(holdout_instances)
    for instances in family_panels.values():
        evaluation_pool.extend(instances)
    full_results = [
        _solve_operator_instance(
            instance=instance,
            host_scaffold=host_scaffold,
            operator_spec=operator_spec,
            seed=seed_base + index,
        )
        for index, instance in enumerate(evaluation_pool)
    ]
    full_gap = _mean(item["optimality_gap"] for item in full_results)
    variants: list[dict[str, Any]] = []
    for variant_index, (variant_name, variant_spec) in enumerate(_ablation_variants(operator_spec).items()):
        variant_results = [
            _solve_operator_instance(
                instance=instance,
                host_scaffold=host_scaffold,
                operator_spec=variant_spec,
                seed=seed_base + 20_000 + (variant_index * 5_000) + index,
            )
            for index, instance in enumerate(evaluation_pool)
        ]
        mean_gap = _mean(item["optimality_gap"] for item in variant_results)
        variants.append(
            {
                "variant_name": variant_name,
                "mean_gap": round(mean_gap, 6),
                "gap_delta_vs_full": round(mean_gap - full_gap, 6),
            }
        )
    return {
        "full_operator_mean_gap": round(full_gap, 6),
        "variants": variants,
    }


def _ablation_variants(operator_spec: dict[str, Any]) -> dict[str, dict[str, Any] | None]:
    operator_type = str(operator_spec.get("operator_type", "candidate_ranker"))
    variants: dict[str, dict[str, Any] | None] = {"disabled": None}
    if operator_type == "candidate_ranker":
        simplified = dict(operator_spec)
        simplified["crossing_bonus"] = 0.0
        simplified["trap_bonus"] = 0.0
        variants["simplified_delta_ranker"] = simplified
        shuffled = dict(operator_spec)
        shuffled["move_delta_weight"] = 0.2
        shuffled["nn_rank_penalty"] = 0.0
        shuffled["span_bonus"] = -0.1
        variants["shuffled_ranker"] = shuffled
    elif operator_type == "perturbation":
        simplified = dict(operator_spec)
        simplified["strength"] = 1
        simplified["attempts"] = 1
        variants["simplified_perturbation"] = simplified
        randomized = dict(operator_spec)
        randomized["primary_mode"] = "shuffle_window"
        randomized["secondary_mode"] = "double_bridge"
        variants["alternate_perturbation"] = randomized
    elif operator_type == "candidate_pruner":
        simplified = dict(operator_spec)
        simplified["trap_bonus"] = 0
        simplified["cluster_bonus"] = 0
        variants["constant_pruner"] = simplified
        widened = dict(operator_spec)
        widened["base_candidate_limit"] = min(32, int(operator_spec.get("base_candidate_limit", 16)) + 8)
        variants["wide_pruner"] = widened
    elif operator_type == "acceptance":
        simplified = dict(operator_spec)
        simplified["mode"] = "improving_only"
        simplified["base_threshold"] = 0.0
        simplified["temperature"] = 0.0
        variants["improving_only_acceptance"] = simplified
        thresholded = dict(operator_spec)
        thresholded["mode"] = "threshold"
        thresholded["base_threshold"] = 0.001
        variants["tight_threshold_acceptance"] = thresholded
    elif operator_type == "restart_controller":
        simplified = dict(operator_spec)
        simplified["restart_growth"] = 0
        simplified["max_restart_count"] = int(operator_spec.get("base_restart_count", 1))
        variants["fixed_restart_budget"] = simplified
        wider = dict(operator_spec)
        wider["base_restart_count"] = min(8, int(operator_spec.get("base_restart_count", 1)) + 2)
        variants["wider_restart_budget"] = wider
    elif operator_type == "scaffold_selector":
        flattened = dict(operator_spec)
        fallback = str(operator_spec.get("fallback", "nearest_neighbor_2opt"))
        flattened["preferred_random_like"] = fallback
        flattened["preferred_clustered"] = fallback
        flattened["preferred_grid_like"] = fallback
        flattened["preferred_two_cluster_bottleneck"] = fallback
        flattened["preferred_elongated"] = fallback
        flattened["preferred_nearest_neighbor_trap"] = fallback
        variants["flattened_selector"] = flattened
        shuffled = dict(operator_spec)
        shuffled["preferred_clustered"] = str(operator_spec.get("preferred_random_like", fallback))
        shuffled["preferred_nearest_neighbor_trap"] = str(operator_spec.get("preferred_grid_like", fallback))
        shuffled["preferred_grid_like"] = str(operator_spec.get("preferred_clustered", fallback))
        variants["shuffled_selector"] = shuffled
    return variants


def _why_it_should_help(operator_spec: dict[str, Any]) -> str:
    operator_type = str(operator_spec.get("operator_type", "candidate_ranker"))
    if operator_type == "candidate_ranker":
        return "The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver."
    if operator_type == "perturbation":
        return "The operator targets local-minimum escape directly by controlling when and how restarts are perturbed."
    if operator_type == "candidate_pruner":
        return "The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way."
    if operator_type == "acceptance":
        return "The operator only changes restart acceptance, so any gain is attributable to a narrow exploration-vs-stability decision rule."
    if operator_type == "restart_controller":
        return "The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals."
    return "The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping."


def _failure_cases(
    *,
    family_test: dict[str, Any],
    transplant: dict[str, Any],
    family_signal: dict[str, Any],
    ablation_signal: dict[str, Any],
    pareto: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    for item in family_test.get("families", []):
        if float(item.get("gap_delta", 0.0)) > 0.005:
            failures.append(f"Underperforms on `{item['family_name']}` with gap delta {item['gap_delta']}.")
    for item in transplant.get("scaffolds", []):
        if float(item.get("mean_gap_delta", 0.0)) > 0.003:
            failures.append(f"Does not transplant cleanly into `{item['scaffold_name']}`.")
    if int(family_signal.get("positive_family_count", 0)) <= 0:
        failures.append("No validation family shows a clear improvement over the host baseline.")
    if float(ablation_signal.get("disabled_gap_delta_vs_full", 0.0)) <= 0.0:
        failures.append("Disabling the operator does not hurt, so the ablation does not support a real operator effect.")
    if float(pareto.get("runtime_inflation", 0.0)) > 0.2:
        failures.append(f"Runtime inflation is high at `{pareto['runtime_inflation']}`.")
    if not failures:
        failures.append("No large validation regressions were detected on the configured family and transplant panels.")
    return failures


def _solve_operator_instance(
    *,
    instance: TSPInstance,
    host_scaffold: str,
    operator_spec: dict[str, Any] | None,
    seed: int,
) -> dict[str, Any]:
    if operator_spec is not None and str(operator_spec.get("operator_type", "")) == "scaffold_selector":
        return solve_with_portfolio(instance, operator_spec, seed=seed)
    if host_scaffold == "portfolio":
        if operator_spec is None:
            return solve_with_scaffold(instance, "nearest_neighbor_2opt", None, seed=seed)
        return solve_with_portfolio(instance, operator_spec, seed=seed)
    return solve_with_scaffold(instance, host_scaffold, operator_spec, seed=seed)


def _family_signal(family_test: dict[str, Any]) -> dict[str, Any]:
    families = list(family_test.get("families", []))
    helpful = [str(item["family_name"]) for item in families if float(item.get("gap_delta", 0.0)) <= -0.002]
    severe_regressions = [
        str(item["family_name"])
        for item in families
        if float(item.get("gap_delta", 0.0)) > 0.005
    ]
    best_gain = max((-float(item.get("gap_delta", 0.0)) for item in families), default=0.0)
    return {
        "positive_family_count": len(helpful),
        "helpful_families": helpful,
        "severe_regression_count": len(severe_regressions),
        "severe_regression_families": severe_regressions,
        "best_family_gain": round(best_gain, 6),
        "mean_gap_delta": round(float(family_test.get("mean_gap_delta", 0.0)), 6),
    }


def _ablation_signal(ablation: dict[str, Any]) -> dict[str, Any]:
    disabled_delta = 0.0
    best_variant_delta = 0.0
    for item in ablation.get("variants", []):
        delta = float(item.get("gap_delta_vs_full", 0.0))
        if str(item.get("variant_name")) == "disabled":
            disabled_delta = delta
        best_variant_delta = max(best_variant_delta, delta)
    return {
        "disabled_gap_delta_vs_full": round(disabled_delta, 6),
        "best_variant_gap_delta_vs_full": round(best_variant_delta, 6),
    }


def _mean(values: Any) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


def _non_empty_line_count(code: str) -> int:
    return sum(1 for line in code.splitlines() if line.strip())
