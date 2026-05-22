from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from statistics import fmean
from typing import Any

from llm_grid_battle.pdf_report import write_pdf_report
from llm_cvrp_phase9.analysis import summarize_condition
from llm_cvrp_phase9.config import Phase9ConditionConfig, Phase9SuiteConfig
from llm_cvrp_phase9.validation import summarize_panel
from run_cvrp_phase9_suite import _evaluate_code_panel, _load_instances


CODEX_DIRECT_CVRP_SOLVER = r'''
def _route_cost(matrix, depot, route):
    if not route:
        return 0
    total = matrix[depot][route[0]]
    for left, right in zip(route, route[1:]):
        total += matrix[left][right]
    total += matrix[route[-1]][depot]
    return total


def _route_load(route, demands):
    total = 0
    for node in route:
        total += demands[node]
    return total


def _two_opt_route(route, matrix, depot):
    if len(route) < 4:
        return list(route)
    best = list(route)
    best_cost = _route_cost(matrix, depot, best)
    changed = True
    passes = 0
    while changed and passes < 2:
        changed = False
        passes += 1
        for left in range(0, len(best) - 2):
            for right in range(left + 2, len(best)):
                if right - left <= 1:
                    continue
                candidate = best[:left] + list(reversed(best[left:right])) + best[right:]
                cost = _route_cost(matrix, depot, candidate)
                if cost < best_cost:
                    best = candidate
                    best_cost = cost
                    changed = True
                    break
            if changed:
                break
    return best


def _try_insert_customer(routes, loads, source_index, source_pos, target_index, target_pos, demands, capacity):
    customer = routes[source_index][source_pos]
    if source_index != target_index and loads[target_index] + demands[customer] > capacity:
        return None
    candidate = [list(route) for route in routes]
    candidate[source_index].pop(source_pos)
    if source_index == target_index and target_pos > source_pos:
        target_pos -= 1
    candidate[target_index].insert(target_pos, customer)
    return [route for route in candidate if route]


def _local_relocate(routes, matrix, demands, capacity, depot):
    current = [list(route) for route in routes if route]
    current_cost = sum(_route_cost(matrix, depot, route) for route in current)
    for _pass_index in range(2):
        improved = False
        route_loads = [_route_load(route, demands) for route in current]
        for source_index, source in enumerate(list(current)):
            for source_pos, customer in enumerate(list(source)):
                for target_index in range(len(current)):
                    target = current[target_index]
                    positions = range(len(target) + 1)
                    for target_pos in positions:
                        candidate = _try_insert_customer(
                            current,
                            route_loads,
                            source_index,
                            source_pos,
                            target_index,
                            target_pos,
                            demands,
                            capacity,
                        )
                        if candidate is None:
                            continue
                        candidate_cost = sum(_route_cost(matrix, depot, route) for route in candidate)
                        if candidate_cost + 1 < current_cost:
                            current = candidate
                            current_cost = candidate_cost
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _clarke_wright(instance):
    matrix = instance["distance_matrix"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    routes = [[node] for node in customers]
    loads = [demands[node] for node in customers]
    route_of = {}
    for index, node in enumerate(customers):
        route_of[node] = index
    savings = []
    for i, left in enumerate(customers):
        for right in customers[i + 1:]:
            saving = matrix[depot][left] + matrix[depot][right] - matrix[left][right]
            savings.append((saving, -abs(demands[left] - demands[right]), left, right))
    savings.sort(reverse=True)
    for _saving, _demand_balance, left, right in savings:
        left_index = route_of.get(left)
        right_index = route_of.get(right)
        if left_index is None or right_index is None or left_index == right_index:
            continue
        left_route = routes[left_index]
        right_route = routes[right_index]
        if not left_route or not right_route:
            continue
        if loads[left_index] + loads[right_index] > capacity:
            continue
        merged = None
        if left_route[-1] == left and right_route[0] == right:
            merged = left_route + right_route
        elif right_route[-1] == right and left_route[0] == left:
            merged = right_route + left_route
        elif left_route[0] == left and right_route[0] == right:
            merged = list(reversed(left_route)) + right_route
        elif left_route[-1] == left and right_route[-1] == right:
            merged = left_route + list(reversed(right_route))
        if merged is None:
            continue
        routes[left_index] = merged
        loads[left_index] += loads[right_index]
        routes[right_index] = []
        loads[right_index] = 0
        for node in merged:
            route_of[node] = left_index
    return [route for route in routes if route]


def solve_cvrp(instance):
    matrix = instance["distance_matrix"]
    depot = instance["depot_index"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    routes = _clarke_wright(instance)
    routes = [_two_opt_route(route, matrix, depot) for route in routes]
    routes = _local_relocate(routes, matrix, demands, capacity, depot)
    routes = [_two_opt_route(route, matrix, depot) for route in routes]
    return [route for route in routes if route]
'''.strip()


SOURCE_LINKS = [
    {
        "name": "Henderson et al. 2018, Deep Reinforcement Learning That Matters",
        "url": "https://arxiv.org/abs/1709.06560",
        "use": "motivates replicated runs, careful reporting, and avoiding best-run-only claims",
    },
    {
        "name": "Agarwal et al. 2021, Deep RL at the Edge of the Statistical Precipice",
        "url": "https://arxiv.org/abs/2108.13264",
        "use": "motivates uncertainty-aware aggregate reporting in few-run adaptive systems",
    },
    {
        "name": "Rice 1976, The Algorithm Selection Problem",
        "url": "https://doi.org/10.1016/S0065-2458(08)60520-3",
        "use": "frames portfolio/selector phases as feature-to-algorithm mapping problems",
    },
    {
        "name": "CVRPLIB Uchoa X benchmark family",
        "url": "https://galgos.inf.puc-rio.br/cvrplib/en/instances",
        "use": "defines the real-world CVRP benchmark source used by phase 9",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _mean(values: list[float]) -> float | None:
    return round(fmean(values), 6) if values else None


def _first_mean(payload: dict[str, Any], *path: str) -> float | None:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    if isinstance(current, dict) and "mean" in current:
        return float(current["mean"])
    if isinstance(current, (int, float)):
        return float(current)
    return None


def _run_dirs(root: Path) -> list[Path]:
    return sorted(path for path in root.iterdir() if path.is_dir() and path.name.startswith("run_"))


def _score_delta(first: float | None, last: float | None, *, lower_is_better: bool) -> float | None:
    if first is None or last is None:
        return None
    return round((first - last) if lower_is_better else (last - first), 6)


def _trend_from_values(values: list[float], *, lower_is_better: bool) -> dict[str, Any]:
    if not values:
        return {"first_window_mean": None, "last_window_mean": None, "improvement": None}
    window = max(1, min(3, len(values) // 3 or 1))
    first = fmean(values[:window])
    last = fmean(values[-window:])
    return {
        "first_window_mean": round(first, 6),
        "last_window_mean": round(last, 6),
        "improvement": _score_delta(first, last, lower_is_better=lower_is_better),
    }


def _summarize_game(game_root: Path) -> dict[str, Any]:
    aggregate_path = game_root / "aggregate_20260510_072126" / "aggregate_summary.json"
    aggregate = _load_json(aggregate_path)
    run_dirs = _run_dirs(game_root)
    condition_rows = []
    epoch_rows = []
    for condition in aggregate["conditions"]:
        name = condition["condition_name"]
        learner = condition.get("learner_agent", "agent_a")
        learner_novelty = _first_mean(condition, "novelty", learner)
        win_rate = _first_mean(condition, "primary_endpoint", "mean_win_rate")
        score_margin = _first_mean(condition, "primary_endpoint", "mean_score_margin")
        generation_success = _first_mean(condition, "generation_success_rate", learner)
        behavior_cell_count = _first_mean(condition, "curriculum_metrics", learner, "behavior_cell_count")
        degradation_count = _first_mean(condition, "curriculum_metrics", learner, "degradation_count")
        escape_count = _first_mean(condition, "curriculum_metrics", learner, "escape_from_losing_regime_count")
        condition_rows.append(
            {
                "condition_name": name,
                "learner_agent": learner,
                "primary_holdout_win_rate": win_rate,
                "primary_holdout_score_margin": score_margin,
                "mean_code_novelty": learner_novelty,
                "generation_success_rate": generation_success,
                "behavior_cell_count": behavior_cell_count,
                "degradation_count": degradation_count,
                "escape_from_losing_regime_count": escape_count,
            }
        )
    for run_dir in run_dirs:
        for condition_dir in sorted(path for path in run_dir.iterdir() if path.is_dir()):
            summary_path = condition_dir / "condition_summary.json"
            if not summary_path.exists():
                continue
            summary = _load_json(summary_path)
            learner = "agent_a"
            score_margins = []
            invalid_rates = []
            fallback_count = 0
            generation_error_count = 0
            for epoch in summary.get("epochs", []):
                scores = epoch.get("scores", {})
                if learner in scores and "agent_b" in scores:
                    score_margins.append(float(scores[learner]) - float(scores["agent_b"]))
                descriptor = epoch.get("behavioral_descriptors", {}).get(learner, {})
                if "invalid_move_rate" in descriptor:
                    invalid_rates.append(float(descriptor["invalid_move_rate"]))
                generation_used_fallback = epoch.get("generation_used_fallback", {})
                if isinstance(generation_used_fallback, dict) and generation_used_fallback.get(learner):
                    fallback_count += 1
                generation_errors = epoch.get("generation_errors", {})
                if isinstance(generation_errors, dict) and generation_errors.get(learner):
                    generation_error_count += 1
            epoch_rows.append(
                {
                    "run_name": run_dir.name,
                    "condition_name": summary.get("condition_name", condition_dir.name),
                    "epoch_count": len(summary.get("epochs", [])),
                    "fallback_count": fallback_count,
                    "generation_error_count": generation_error_count,
                    "score_margin_trend": _trend_from_values(score_margins, lower_is_better=False),
                    "mean_invalid_move_rate": _mean(invalid_rates),
                }
            )
    trend_improvements = [
        row["score_margin_trend"]["improvement"]
        for row in epoch_rows
        if row["score_margin_trend"]["improvement"] is not None
    ]
    return {
        "family": "simple_grid_game",
        "runs_root": str(game_root),
        "aggregate_path": str(aggregate_path),
        "run_count": len(run_dirs),
        "condition_count": len(condition_rows),
        "total_epochs": sum(int(row["epoch_count"]) for row in epoch_rows),
        "conditions": condition_rows,
        "epoch_dynamics": {
            "mean_epoch_score_margin_improvement": _mean([float(value) for value in trend_improvements]),
            "mean_invalid_move_rate": _mean([float(row["mean_invalid_move_rate"]) for row in epoch_rows if row["mean_invalid_move_rate"] is not None]),
            "total_generation_fallbacks": sum(int(row["fallback_count"]) for row in epoch_rows),
            "total_generation_errors": sum(int(row["generation_error_count"]) for row in epoch_rows),
        },
    }


def _summarize_tsp(tsp_root: Path) -> dict[str, Any]:
    aggregate_path = tsp_root / "aggregate_20260513_155249_t" / "aggregate_summary.json"
    aggregate = _load_json(aggregate_path)
    run_dirs = _run_dirs(tsp_root)
    condition_rows = []
    epoch_rows = []
    for condition in aggregate["conditions"]:
        condition_rows.append(
            {
                "condition_name": condition["condition_name"],
                "final_tsplib_gap": _first_mean(condition, "final_tsplib_gap"),
                "final_transfer_gap": _first_mean(condition, "final_transfer_gap"),
                "final_synthetic_gap": _first_mean(condition, "final_synthetic_gap"),
                "adaptation_efficiency": _first_mean(condition, "adaptation_efficiency"),
                "mean_code_novelty": _first_mean(condition, "mean_code_novelty"),
                "mean_complexity": _first_mean(condition, "mean_complexity"),
            }
        )
    for run_dir in run_dirs:
        for condition_dir in sorted(path for path in run_dir.iterdir() if path.is_dir()):
            summary_path = condition_dir / "condition_summary.json"
            if not summary_path.exists():
                continue
            summary = _load_json(summary_path)
            training_gaps = []
            transfer_gaps = []
            novelty_values = []
            accepted_count = 0
            fallback_count = 0
            error_count = 0
            for epoch in summary.get("epochs", []):
                training_summary = epoch.get("training_summary", {})
                if "mean_optimality_gap" in training_summary:
                    training_gaps.append(float(training_summary["mean_optimality_gap"]))
                transfer_probe = epoch.get("transfer_probe", {})
                if "mean_optimality_gap" in transfer_probe:
                    transfer_gaps.append(float(transfer_probe["mean_optimality_gap"]))
                if "code_novelty" in epoch and epoch["code_novelty"] is not None:
                    novelty_values.append(float(epoch["code_novelty"]))
                if epoch.get("selection", {}).get("accepted"):
                    accepted_count += 1
                if epoch.get("generation_used_fallback") or epoch.get("materialization_used_fallback"):
                    fallback_count += 1
                if epoch.get("generation_error") or epoch.get("materialization_init_error"):
                    error_count += 1
            epoch_rows.append(
                {
                    "run_name": run_dir.name,
                    "condition_name": summary.get("condition_name", condition_dir.name),
                    "epoch_count": len(summary.get("epochs", [])),
                    "accepted_epoch_count": accepted_count,
                    "fallback_count": fallback_count,
                    "generation_or_materialization_error_count": error_count,
                    "training_gap_trend": _trend_from_values(training_gaps, lower_is_better=True),
                    "transfer_gap_trend": _trend_from_values(transfer_gaps, lower_is_better=True),
                    "mean_code_novelty": _mean(novelty_values),
                }
            )
    return {
        "family": "symmetric_tsp_replay",
        "runs_root": str(tsp_root),
        "aggregate_path": str(aggregate_path),
        "run_count": len(run_dirs),
        "condition_count": len(condition_rows),
        "total_epochs": sum(int(row["epoch_count"]) for row in epoch_rows),
        "best_transfer_condition": aggregate.get("best_transfer_condition"),
        "conditions": condition_rows,
        "paired_comparisons": aggregate.get("paired_comparisons", []),
        "epoch_dynamics": {
            "mean_training_gap_improvement": _mean([
                float(row["training_gap_trend"]["improvement"])
                for row in epoch_rows
                if row["training_gap_trend"]["improvement"] is not None
            ]),
            "mean_transfer_gap_improvement": _mean([
                float(row["transfer_gap_trend"]["improvement"])
                for row in epoch_rows
                if row["transfer_gap_trend"]["improvement"] is not None
            ]),
            "accepted_epoch_rate": round(
                sum(int(row["accepted_epoch_count"]) for row in epoch_rows) / max(1, sum(int(row["epoch_count"]) for row in epoch_rows)),
                6,
            ),
            "mean_code_novelty": _mean([float(row["mean_code_novelty"]) for row in epoch_rows if row["mean_code_novelty"] is not None]),
            "total_generation_or_materialization_errors": sum(int(row["generation_or_materialization_error_count"]) for row in epoch_rows),
            "total_fallbacks": sum(int(row["fallback_count"]) for row in epoch_rows),
        },
    }


def _summarize_cvrp(cvrp_root: Path) -> dict[str, Any]:
    aggregate_path = cvrp_root / "aggregate_20260521_220715_t" / "aggregate_summary.json"
    aggregate = _load_json(aggregate_path)
    run_dirs = _run_dirs(cvrp_root)
    condition_rows = []
    epoch_rows = []
    for condition in aggregate["conditions"]:
        condition_rows.append(
            {
                "condition_name": condition["condition_name"],
                "heldout_feasibility_rate": _first_mean(condition, "heldout_feasibility_rate"),
                "heldout_penalized_gap": _first_mean(condition, "heldout_penalized_gap"),
                "heldout_feasible_gap": _first_mean(condition, "heldout_feasible_gap"),
                "heldout_runtime_ms": _first_mean(condition, "heldout_runtime_ms"),
                "mean_code_novelty": _first_mean(condition, "mean_code_novelty"),
                "mean_complexity": _first_mean(condition, "mean_complexity"),
            }
        )
    for run_dir in run_dirs:
        summary_path = run_dir / "phase9_solver_evolution" / "condition_summary.json"
        if not summary_path.exists():
            continue
        summary = _load_json(summary_path)
        epochs = summary.get("epochs", [])
        train_gaps = []
        feasibility_values = []
        novelty_values = []
        accepted_count = 0
        invalid_generation_count = 0
        fallback_count = 0
        for epoch in epochs:
            candidate_summary = epoch.get("candidate_train_summary", {})
            if "mean_penalized_gap" in candidate_summary:
                train_gaps.append(float(candidate_summary["mean_penalized_gap"]))
            if "feasibility_rate" in candidate_summary:
                feasibility_values.append(float(candidate_summary["feasibility_rate"]))
            if "code_novelty" in epoch and epoch["code_novelty"] is not None:
                novelty_values.append(float(epoch["code_novelty"]))
            if epoch.get("accepted"):
                accepted_count += 1
            if not epoch.get("generation_valid_for_acceptance"):
                invalid_generation_count += 1
            if epoch.get("generation_fallback_used"):
                fallback_count += 1
        condition_summary = summarize_condition(summary)
        epoch_rows.append(
            {
                "run_name": run_dir.name,
                "epoch_count": len(epochs),
                "accepted_epoch_count": accepted_count,
                "fallback_count": fallback_count,
                "invalid_generation_count": invalid_generation_count,
                "candidate_train_gap_trend": _trend_from_values(train_gaps, lower_is_better=True),
                "candidate_train_feasibility_trend": _trend_from_values(feasibility_values, lower_is_better=False),
                "mean_code_novelty": _mean(novelty_values),
                "final_heldout_penalized_gap": condition_summary.get("heldout_penalized_gap"),
                "final_heldout_feasibility_rate": condition_summary.get("heldout_feasibility_rate"),
            }
        )
    return {
        "family": "real_world_cvrp_solver_evolution",
        "runs_root": str(cvrp_root),
        "aggregate_path": str(aggregate_path),
        "run_count": len(run_dirs),
        "condition_count": len(condition_rows),
        "total_epochs": sum(int(row["epoch_count"]) for row in epoch_rows),
        "best_heldout_condition": aggregate.get("best_heldout_condition"),
        "conditions": condition_rows,
        "paired_comparisons": aggregate.get("paired_comparisons", []),
        "epoch_dynamics": {
            "mean_candidate_train_gap_improvement": _mean([
                float(row["candidate_train_gap_trend"]["improvement"])
                for row in epoch_rows
                if row["candidate_train_gap_trend"]["improvement"] is not None
            ]),
            "mean_candidate_feasibility_improvement": _mean([
                float(row["candidate_train_feasibility_trend"]["improvement"])
                for row in epoch_rows
                if row["candidate_train_feasibility_trend"]["improvement"] is not None
            ]),
            "accepted_epoch_rate": round(
                sum(int(row["accepted_epoch_count"]) for row in epoch_rows) / max(1, sum(int(row["epoch_count"]) for row in epoch_rows)),
                6,
            ),
            "mean_code_novelty": _mean([float(row["mean_code_novelty"]) for row in epoch_rows if row["mean_code_novelty"] is not None]),
            "total_invalid_generations": sum(int(row["invalid_generation_count"]) for row in epoch_rows),
            "total_generation_fallbacks": sum(int(row["fallback_count"]) for row in epoch_rows),
        },
    }


def _phase9_config(config_path: Path) -> Phase9ConditionConfig:
    suite = Phase9SuiteConfig.load(config_path)
    for condition in suite.conditions:
        if condition.execution.mode == "solver_evolution":
            return condition
    raise ValueError(f"No solver_evolution condition found in {config_path}")


def _evaluate_codex_direct(config_path: Path, output_dir: Path) -> dict[str, Any]:
    config = _phase9_config(config_path)
    train_instances, holdout_instances, _manifest = _load_instances(
        config.benchmark.manifest_path,
        train_limit=int(config.benchmark.train_instance_limit),
        holdout_limit=int(config.benchmark.holdout_instance_limit),
    )
    train_results = _evaluate_code_panel(CODEX_DIRECT_CVRP_SOLVER, train_instances, config)
    holdout_results = _evaluate_code_panel(CODEX_DIRECT_CVRP_SOLVER, holdout_instances, config)
    train_summary = summarize_panel(train_results, panel_name="train")
    holdout_summary = summarize_panel(holdout_results, panel_name="holdout")
    solver_path = output_dir / "codex_direct_cvrp_solver.py"
    solver_path.write_text(CODEX_DIRECT_CVRP_SOLVER + "\n", encoding="utf-8")
    payload = {
        "experiment_type": "single_shot_codex_direct_solver",
        "description": (
            "Codex authored this deterministic CVRP solver directly in the repository. "
            "It was not produced through the API evolution loop and was evaluated through "
            "the same phase-9 sandbox, validator, and train/holdout split."
        ),
        "config_path": str(config_path),
        "solver_path": str(solver_path),
        "train_summary": train_summary,
        "holdout_summary": holdout_summary,
        "train_results": train_results,
        "holdout_results": holdout_results,
    }
    _write_json(output_dir / "codex_direct_cvrp_summary.json", payload)
    return payload


def _condition_lookup(summary: dict[str, Any], condition_name: str) -> dict[str, Any]:
    for condition in summary.get("conditions", []):
        if condition.get("condition_name") == condition_name:
            return condition
    return {}


def _meta_patterns(game: dict[str, Any], tsp: dict[str, Any], cvrp: dict[str, Any], codex_direct: dict[str, Any]) -> list[dict[str, str]]:
    game_novelty = _mean([
        float(condition["mean_code_novelty"])
        for condition in game["conditions"]
        if condition.get("mean_code_novelty") is not None
    ])
    tsp_novelty = tsp["epoch_dynamics"].get("mean_code_novelty")
    cvrp_novelty = cvrp["epoch_dynamics"].get("mean_code_novelty")
    cvrp_direct_gap = codex_direct["holdout_summary"]["mean_penalized_gap"]
    cvrp_savings = _condition_lookup(cvrp, "phase9_baseline_clarke_wright_savings")
    cvrp_evolved = _condition_lookup(cvrp, "phase9_solver_evolution")
    return [
        {
            "pattern": "Syntactic novelty is common, but not sufficient.",
            "evidence": (
                f"Mean novelty was high in the game family ({game_novelty}), TSP ({tsp_novelty}), "
                f"and CVRP candidate stream ({cvrp_novelty}), yet final wins were domain-dependent."
            ),
            "interpretation": "The loop is good at producing variants; selection and validation determine whether those variants become useful.",
        },
        {
            "pattern": "Improvement depends on available benchmark headroom.",
            "evidence": (
                "TSP random replay improved over no replay on final transfer and TSPLIB gaps, while phase 9 improved over weak CVRP baselines but not Clarke-Wright."
            ),
            "interpretation": "When a strong classical baseline already captures most structure, LLM evolution often produces bounded refinement rather than a dominant new method.",
        },
        {
            "pattern": "Failure modes shift with domain constraints.",
            "evidence": (
                "The game loop mainly exposed action/runtime behavior issues, TSP exposed replay-policy sensitivity, and CVRP exposed feasibility/scoring pressure plus low acceptance rates."
            ),
            "interpretation": "A unified framework should classify failure by domain-specific validator pressure rather than only by code novelty or final score.",
        },
        {
            "pattern": "The strongest defensible story is capability-bounded adaptation.",
            "evidence": (
                f"Codex direct CVRP held-out gap was {cvrp_direct_gap}; phase-9 evolved mean held-out gap was "
                f"{cvrp_evolved.get('heldout_penalized_gap')}; Clarke-Wright was {cvrp_savings.get('heldout_penalized_gap')}."
            ),
            "interpretation": "The current data support a framework of capabilities and limits, not a claim that LLM evolution beats mature optimization heuristics.",
        },
    ]


def _metric_table(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for condition in summary.get("conditions", []):
        row = {"condition": condition.get("condition_name")}
        for key in [
            "primary_holdout_win_rate",
            "primary_holdout_score_margin",
            "final_transfer_gap",
            "final_tsplib_gap",
            "heldout_penalized_gap",
            "heldout_feasibility_rate",
            "mean_code_novelty",
            "generation_success_rate",
            "adaptation_efficiency",
            "heldout_runtime_ms",
        ]:
            if key in condition:
                row[key] = condition[key]
        rows.append(row)
    return rows


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                values.append(f"{value:.6g}")
            elif value is None:
                values.append("")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _render_report(payload: dict[str, Any]) -> str:
    game = payload["families"]["simple_grid_game"]
    tsp = payload["families"]["symmetric_tsp_replay"]
    cvrp = payload["families"]["real_world_cvrp_solver_evolution"]
    codex_direct = payload["codex_direct_experiment"]
    lines = [
        "# Cross-Family Code-Evolution Synthesis",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Purpose",
        "",
        (
            "This artifact answers the requested cross-family question: whether comparable LLM-driven "
            "code-evolution loops show recurring capability and limitation patterns across the simple-game, "
            "TSP, and real-world CVRP experiment families."
        ),
        "",
        (
            "The analysis is intentionally conservative. It reuses completed official artifacts instead of "
            "creating a new paid campaign, normalizes only metrics that are present in the archived runs, and "
            "keeps train-time search dynamics separate from held-out endpoint evidence."
        ),
        "",
        "## Evidence Base",
        "",
        f"- Simple game transfer suite: {game['run_count']} runs, {game['condition_count']} conditions, {game['total_epochs']} epochs.",
        f"- Symmetric TSP replay suite: {tsp['run_count']} runs, {tsp['condition_count']} conditions, {tsp['total_epochs']} epochs.",
        f"- Real-world CVRP phase-9 suite: {cvrp['run_count']} runs, {cvrp['condition_count']} conditions, {cvrp['total_epochs']} solver-evolution epochs.",
        "- Direct Codex experiment: one deterministic CVRP solver authored locally by Codex and evaluated through the phase-9 sandbox/validator.",
        "",
        "## Family-Level Results",
        "",
        "### Simple Game Transfer",
        "",
        *_markdown_table(
            _metric_table(game),
            ["condition", "primary_holdout_win_rate", "primary_holdout_score_margin", "mean_code_novelty", "generation_success_rate"],
        ),
        "",
        "### TSP Replay",
        "",
        *_markdown_table(
            _metric_table(tsp),
            ["condition", "final_transfer_gap", "final_tsplib_gap", "mean_code_novelty", "adaptation_efficiency"],
        ),
        "",
        "### Real-World CVRP",
        "",
        *_markdown_table(
            _metric_table(cvrp),
            ["condition", "heldout_feasibility_rate", "heldout_penalized_gap", "heldout_runtime_ms", "mean_code_novelty"],
        ),
        "",
        "## Direct Codex Experiment",
        "",
        (
            "Codex produced a single deterministic Clarke-Wright-style CVRP solver with bounded local route "
            "improvement. This is not an API-generated candidate and not an evolved loop. It is a direct "
            "single-shot coding baseline evaluated on the same phase-9 train and held-out split."
        ),
        "",
        "| Panel | Feasibility | Mean penalized gap | Mean feasible gap | Mean runtime ms |",
        "| --- | --- | --- | --- | --- |",
        (
            f"| train | {_fmt(codex_direct['train_summary']['feasibility_rate'])} | "
            f"{_fmt(codex_direct['train_summary']['mean_penalized_gap'])} | "
            f"{_fmt(codex_direct['train_summary']['mean_feasible_gap'])} | "
            f"{_fmt(codex_direct['train_summary']['mean_runtime_ms'])} |"
        ),
        (
            f"| holdout | {_fmt(codex_direct['holdout_summary']['feasibility_rate'])} | "
            f"{_fmt(codex_direct['holdout_summary']['mean_penalized_gap'])} | "
            f"{_fmt(codex_direct['holdout_summary']['mean_feasible_gap'])} | "
            f"{_fmt(codex_direct['holdout_summary']['mean_runtime_ms'])} |"
        ),
        "",
        "Interpretation: the direct Codex solver is useful as a sanity baseline for what a single interactive Codex pass can author, but it should not be treated as a replicated stochastic condition. The fair comparison remains descriptive unless it is rerun under a frozen direct-Codex protocol.",
        "",
        "## Meta-Patterns",
        "",
    ]
    for item in payload["meta_patterns"]:
        lines.extend(
            [
                f"### {item['pattern']}",
                "",
                f"Evidence: {item['evidence']}",
                "",
                f"Interpretation: {item['interpretation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Framework Summary",
            "",
            "The current project is best summarized as a capability-and-limits framework for LLM-driven code evolution.",
            "",
            "- Capability: the loop reliably generates executable, diverse code variants under a structured interface.",
            "- Capability: when validators and baselines leave reachable heuristic headroom, selection can preserve useful refinements.",
            "- Limitation: lexical/code novelty does not reliably imply behavioral novelty or held-out improvement.",
            "- Limitation: strong classical heuristics and low portfolio/benchmark headroom cap apparent wins.",
            "- Limitation: each domain has a different dominant failure mode, so a single aggregate score hides important mechanisms.",
            "",
            "## Claim Wording",
            "",
            (
                "A defensible dissertation-level claim is: across three increasingly realistic problem families, "
                "LLM-guided code evolution can produce diverse, executable heuristic programs and sometimes "
                "preserve useful adaptations, but its current success is constrained by validator pressure, "
                "baseline strength, and benchmark headroom. The contribution is therefore a measurement framework "
                "for when the loop adapts versus when it churns, not a claim of beating mature optimization solvers."
            ),
            "",
            "## Sources",
            "",
        ]
    )
    for source in SOURCE_LINKS:
        lines.append(f"- [{source['name']}]({source['url']}): {source['use']}.")
    lines.append("")
    return "\n".join(lines)


def build_summary(args: argparse.Namespace, output_dir: Path) -> dict[str, Any]:
    game = _summarize_game(Path(args.game_root))
    tsp = _summarize_tsp(Path(args.tsp_root))
    cvrp = _summarize_cvrp(Path(args.cvrp_root))
    codex_direct = _evaluate_codex_direct(Path(args.phase9_config), output_dir)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "cross_family_code_evolution_synthesis",
        "families": {
            "simple_grid_game": game,
            "symmetric_tsp_replay": tsp,
            "real_world_cvrp_solver_evolution": cvrp,
        },
        "codex_direct_experiment": {
            "experiment_type": codex_direct["experiment_type"],
            "description": codex_direct["description"],
            "config_path": codex_direct["config_path"],
            "solver_path": codex_direct["solver_path"],
            "train_summary": codex_direct["train_summary"],
            "holdout_summary": codex_direct["holdout_summary"],
        },
        "meta_patterns": _meta_patterns(game, tsp, cvrp, codex_direct),
        "source_links": SOURCE_LINKS,
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze cross-family LLM code-evolution meta-patterns.")
    parser.add_argument("--game-root", default="runs/transfer_suite/rotating_plus_replay_aware_selection")
    parser.add_argument("--tsp-root", default="runs/tsp_suite/replay_transfer")
    parser.add_argument("--cvrp-root", default="runs/cvrp_phase9_suite/solver_evolution")
    parser.add_argument("--phase9-config", default="configs/cvrp_phase9_suite/01_solver_evolution.json")
    parser.add_argument("--output-root", default="runs/cross_family_synthesis")
    parser.add_argument("--timestamp", default="")
    args = parser.parse_args()

    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_root) / f"meta_patterns_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(args, output_dir)
    report = _render_report(summary)
    _write_json(output_dir / "cross_family_summary.json", summary)
    (output_dir / "cross_family_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=output_dir / "cross_family_report.pdf",
        run_name=output_dir.name,
        markdown_report=report,
        suite_summary=summary,
        condition_payloads=[],
    )
    print(f"Completed cross-family synthesis. Results written to: {output_dir}")


if __name__ == "__main__":
    main()
