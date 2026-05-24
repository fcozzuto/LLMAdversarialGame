from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import random
from statistics import fmean
from time import perf_counter
from typing import Any

from llm_grid_battle.config import SuiteConfig
from llm_grid_battle.llm import generate_code as generate_game_code
from llm_grid_battle.llm import load_env_files
from llm_grid_battle.opponent_library import resolve_opponent_spec
from llm_tsp.benchmark import load_benchmark_bundle
from llm_tsp.heuristic_engine import canonicalize_heuristic_spec, default_heuristic_code, solve_instance
from llm_tsp.llm import generate_code as generate_tsp_code
from llm_tsp.sandbox import materialize_heuristic
from llm_cvrp_phase9.analysis import summarize_condition
from llm_cvrp_phase9.config import Phase9SuiteConfig
from llm_cvrp_phase9.llm import default_solver_code, generate_code as generate_cvrp_code
from llm_cvrp_phase9.validation import summarize_panel
from model_strength_factorial_common import (
    MODEL_TIERS,
    TASK_FAMILIES,
    TECHNIQUES,
    code_novelty,
    load_jsonish_config,
    model_strength_columns,
    performance_columns,
    write_csv_dicts,
    write_json,
)
from run_cvrp_phase9_suite import _evaluate_code_panel, _load_instances
from run_suite import _get_or_generate_policy_code, run_epoch, run_holdout_evaluation


def _condition_suffix(model_tier: str, technique: str, seed: int) -> str:
    return f"{model_tier}__{technique}__seed_{seed:04d}"


def _task_model(model_spec: dict[str, Any], task_family: str) -> tuple[str, str]:
    provider = str(model_spec["provider"])
    model = str(model_spec["model_name"])
    overrides = model_spec.get("task_model_overrides", {})
    if isinstance(overrides, dict) and task_family in overrides:
        item = overrides[task_family]
        provider = str(item.get("provider", provider))
        model = str(item.get("model_name", model))
    return provider, model


def _candidate_budget(task_cfg: dict[str, Any], technique: str) -> tuple[int, int]:
    if technique == "single_shot":
        return 1, 1
    epochs = int(task_cfg["epochs"])
    return epochs, epochs


def _base_candidate_prompt(task_family: str, technique: str, candidate_index: int, replay_text: str) -> str:
    if task_family == "simple_games":
        return "\n".join(
            [
                "Return only raw Python source code.",
                "Define exactly this function:",
                "def choose_move(observation):",
                "    return [dx, dy]",
                "",
                "Rules:",
                "- No imports.",
                "- dx and dy must each be -1, 0, or 1.",
                "- The policy must work for resource_collection, pursuit_evasion, and territory_control observations.",
                "- Use observation fields defensively with .get where appropriate.",
                "- The goal is robust held-out play against simple builtin opponents.",
                "",
                f"Technique: {technique}. Candidate {candidate_index}.",
                replay_text,
            ]
        )
    if task_family == "tsp":
        return "\n".join(
            [
                "Return only raw Python source code.",
                "Define exactly this function:",
                "def build_heuristic():",
                "    return {...}",
                "",
                "Rules:",
                "- No imports.",
                "- Return a deterministic dictionary for the existing constrained TSP heuristic scaffold.",
                "- Favor robust held-out TSPLIB and synthetic transfer performance, not only training instances.",
                "- Keep the heuristic interpretable and not overly complex.",
                "",
                f"Technique: {technique}. Candidate {candidate_index}.",
                replay_text,
            ]
        )
    return "\n".join(
        [
            "Return only raw Python source code.",
            "Define exactly this function:",
            "def solve_cvrp(instance):",
            "    return routes",
            "",
            "Rules:",
            "- No imports.",
            "- Return a list of routes; each route is a list of customer ids and must not include the depot.",
            "- Visit every customer exactly once and respect vehicle capacity.",
            "- Build deterministic, interpretable CVRP solver logic using constructive, repair, and local-search ideas.",
            "- Do not rely on held-out data.",
            "",
            f"Technique: {technique}. Candidate {candidate_index}.",
            replay_text,
        ]
    )


def _replay_text(
    technique: str,
    archive: list[dict[str, Any]],
    incumbent_code: str | None,
    replay_rng: random.Random,
) -> str:
    if technique in {"single_shot", "budget_matched_no_replay"}:
        return "No prior candidates, replay memory, failure memory, or compression may be used."
    if not archive:
        return "No replay archive entries are available yet."
    if technique == "random_replay":
        selected = replay_rng.sample(archive, k=min(3, len(archive)))
        return _with_incumbent(
            "Random replay examples from prior candidates:\n" + json.dumps(selected, indent=2, sort_keys=True)[:5000],
            incumbent_code,
        )
    if technique == "failure_replay":
        selected = sorted(archive, key=lambda item: float(item.get("train_score_for_minimization", 0.0)), reverse=True)[:3]
        return _with_incumbent(
            "Failure replay examples prioritized by poor train validation:\n" + json.dumps(selected, indent=2, sort_keys=True)[:5000],
            incumbent_code,
        )
    selected = sorted(archive, key=lambda item: float(item.get("train_score_for_minimization", 0.0)), reverse=True)[:5]
    summary_lines = [
        "Compressed failure replay summary:",
        f"- archived_candidates: {len(archive)}",
        f"- worst_train_scores: {[round(float(item.get('train_score_for_minimization', 0.0)), 6) for item in selected]}",
        f"- common_failure_notes: {[item.get('failure_note', '') for item in selected[:3]]}",
    ]
    if incumbent_code:
        summary_lines.append("- Use the incumbent only as a reference; propose a targeted improvement.")
    return _with_incumbent("\n".join(summary_lines), incumbent_code)


def _with_incumbent(text: str, incumbent_code: str | None) -> str:
    if not incumbent_code:
        return text
    excerpt = incumbent_code.strip()
    if len(excerpt) > 5000:
        excerpt = excerpt[:5000] + "\n# ... truncated incumbent ..."
    return "\n".join(
        [
            text,
            "",
            "Current accepted incumbent code to improve:",
            excerpt,
        ]
    )


def _generate_candidate(
    *,
    task_family: str,
    model_spec: dict[str, Any],
    technique: str,
    candidate_index: int,
    archive: list[dict[str, Any]],
    incumbent_code: str | None,
    generation_cfg: dict[str, Any],
    replay_rng: random.Random,
) -> dict[str, Any]:
    provider, model = _task_model(model_spec, task_family)
    prompt = _base_candidate_prompt(
        task_family,
        technique,
        candidate_index,
        _replay_text(technique, archive, incumbent_code, replay_rng),
    )
    temperature = float(model_spec.get("temperature", generation_cfg.get("temperature", 0.2)))
    max_tokens = int(model_spec.get("max_tokens", generation_cfg.get("max_tokens", 2500)))
    timeout = float(generation_cfg.get("llm_timeout_seconds", 180.0))
    if task_family == "simple_games":
        result = generate_game_code(
            provider=provider,
            model=model,
            system_prompt="You write deterministic Python for a grid-game agent.",
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            pre_execution_validation=True,
            repair_invalid_submissions=bool(generation_cfg.get("repair_invalid_submissions", True)),
            timeout=timeout,
        )
    elif task_family == "tsp":
        result = generate_tsp_code(
            provider=provider,
            model=model,
            system_prompt="You write deterministic Python that returns TSP heuristic scaffold specifications.",
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            repair_invalid_submissions=bool(generation_cfg.get("repair_invalid_submissions", True)),
            timeout=timeout,
        )
    else:
        result = generate_cvrp_code(
            provider=provider,
            model=model,
            system_prompt="You design deterministic CVRP solvers that build feasible routes and improve them with interpretable heuristic logic.",
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            repair_invalid_submissions=bool(generation_cfg.get("repair_invalid_submissions", True)),
            timeout=timeout,
            max_non_empty_lines=int(generation_cfg.get("max_non_empty_lines", 260)),
            max_characters=int(generation_cfg.get("max_characters", 12000)),
        )
    if _fatal_generation_error(result.error):
        raise SystemExit(
            f"Fatal generation error for {provider}/{model} during {task_family} {technique} "
            f"candidate {candidate_index}: {result.error}"
        )
    return {
        "provider": provider,
        "model_name": model,
        "prompt": prompt,
        "raw_text": result.raw_text,
        "code": result.code,
        "submitted_code": result.submitted_code or result.code,
        "error": result.error,
        "validation_issues": list(result.validation_issues),
        "used_fallback": bool(result.used_fallback),
        "repair_attempted": bool(getattr(result, "repair_attempted", False)),
    }


def _fatal_generation_error(error: str | None) -> bool:
    if not error:
        return False
    normalized = error.lower()
    fatal_markers = [
        "insufficient_quota",
        "exceeded your current quota",
        "billing details",
        "rate_limit_exceeded",
        "http 429",
    ]
    return any(marker in normalized for marker in fatal_markers)


def _simple_game_configs(path: str | Path) -> list[Any]:
    suite = SuiteConfig.load(path)
    configs = []
    for condition in suite.conditions:
        copied = deepcopy(condition)
        copied.judge.enabled = False
        configs.append(copied)
    return configs


def _evaluate_simple_game_train(code: str, configs: list[Any], *, seed: int, candidate_index: int) -> dict[str, Any]:
    rows = []
    generation_cache: dict[str, Any] = {}
    for condition_index, config in enumerate(configs):
        opponent_spec = config.curriculum.opponent_pool[(candidate_index + condition_index) % len(config.curriculum.opponent_pool)]
        opponent_agent, _label, _metadata = resolve_opponent_spec(opponent_spec, slot_name=config.curriculum.opponent_agent)
        opponent_code = _get_or_generate_policy_code(
            config=config,
            generation_cache=generation_cache,
            cache_key=f"train:{config.name}:{opponent_agent.model}",
            agent=opponent_agent,
        )
        focal_agent = next(agent for agent in config.agents if agent.name == config.curriculum.focal_agent)
        epoch = run_epoch(
            config=config,
            epoch_index=candidate_index,
            map_seed=seed + (condition_index * 10_000) + candidate_index,
            codes={
                config.curriculum.focal_agent: code,
                config.curriculum.opponent_agent: opponent_code,
            },
            active_agents=[focal_agent, opponent_agent],
        )
        focal_score = float(epoch["scores"][config.curriculum.focal_agent])
        opponent_score = float(epoch["scores"][config.curriculum.opponent_agent])
        rows.append(
            {
                "condition_name": config.name,
                "score_margin": focal_score - opponent_score,
                "focal_score": focal_score,
                "opponent_score": opponent_score,
                "runtime_issue_count": sum(len(items) for items in epoch.get("runtime_events", {}).values()),
            }
        )
    return {
        "mean_score_margin": fmean([row["score_margin"] for row in rows]),
        "rows": rows,
    }


def _evaluate_simple_game_holdout(code: str, configs: list[Any]) -> dict[str, Any]:
    panels = []
    for config in configs:
        panel = run_holdout_evaluation(
            config=config,
            focal_agent_name=config.curriculum.focal_agent,
            focal_code=code,
            generation_cache={},
        )
        if panel:
            panels.append({"condition_name": config.name, "panel": panel})
    win_rates = []
    margins = []
    for panel in panels:
        for opponent in panel["panel"].get("opponents", []):
            win_rates.append(float(opponent["win_rate"]))
            margins.append(float(opponent["mean_score_margin"]))
    return {
        "primary_holdout_win_rate": fmean(win_rates) if win_rates else 0.0,
        "primary_holdout_score_margin": fmean(margins) if margins else 0.0,
        "panels": panels,
    }


def _evaluate_tsp_train(code: str, bundle: Any, *, seed: int) -> dict[str, Any]:
    materialized = materialize_heuristic(code)
    spec = canonicalize_heuristic_spec(materialized.heuristic_spec)
    results = [
        solve_instance(instance, spec, seed=seed + index)
        for index, instance in enumerate(bundle.train)
    ]
    mean_gap = fmean(float(item["optimality_gap"]) for item in results) if results else 0.0
    return {
        "mean_optimality_gap": mean_gap,
        "train_score_for_minimization": mean_gap,
        "spec": spec,
        "materialization_issues": materialized.issues,
        "materialization_used_fallback": bool(materialized.used_fallback),
        "results": results,
    }


def _summarize_tsp_panel(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {"mean_optimality_gap": 0.0, "instance_count": 0}
    return {
        "mean_optimality_gap": round(fmean(float(item["optimality_gap"]) for item in results), 6),
        "instance_count": len(results),
        "worst_instances": [
            {
                "name": item["instance"]["name"],
                "family": item["instance"]["family"],
                "optimality_gap": round(float(item["optimality_gap"]), 6),
            }
            for item in sorted(results, key=lambda row: float(row["optimality_gap"]), reverse=True)[:5]
        ],
    }


def _evaluate_tsp_holdout(code: str, bundle: Any, *, seed: int) -> dict[str, Any]:
    materialized = materialize_heuristic(code)
    spec = canonicalize_heuristic_spec(materialized.heuristic_spec)
    tsplib_results = [solve_instance(instance, spec, seed=seed + index) for index, instance in enumerate(bundle.holdout)]
    synthetic_results = [
        solve_instance(instance, spec, seed=seed + 50_000 + index)
        for index, instance in enumerate(bundle.synthetic_holdout)
    ]
    tsplib = _summarize_tsp_panel(tsplib_results)
    synthetic = _summarize_tsp_panel(synthetic_results)
    combined_count = max(1, len(tsplib_results) + len(synthetic_results))
    transfer = (
        (float(tsplib["mean_optimality_gap"]) * len(tsplib_results))
        + (float(synthetic["mean_optimality_gap"]) * len(synthetic_results))
    ) / combined_count
    return {
        "final_tsplib_gap": float(tsplib["mean_optimality_gap"]),
        "final_transfer_gap": round(transfer, 6),
        "panels": {"heldout_tsplib": tsplib, "synthetic_holdout": synthetic},
    }


def _phase9_config(path: str | Path) -> Any:
    suite = Phase9SuiteConfig.load(path)
    for condition in suite.conditions:
        if condition.execution.mode == "solver_evolution":
            return condition
    raise ValueError(f"No solver_evolution condition found in {path}")


def _evaluate_cvrp_train(code: str, instances: list[Any], config: Any) -> dict[str, Any]:
    results = _evaluate_code_panel(code, instances, config)
    summary = summarize_panel(results, panel_name="train")
    return {
        "train_score_for_minimization": float(summary["mean_penalized_gap"]),
        "summary": summary,
        "results": results,
    }


def _evaluate_cvrp_holdout(code: str, train_instances: list[Any], holdout_instances: list[Any], config: Any) -> dict[str, Any]:
    train_results = _evaluate_code_panel(code, train_instances, config)
    holdout_results = _evaluate_code_panel(code, holdout_instances, config)
    payload = {
        "condition_name": "factorial_cvrp_candidate",
        "execution_mode": "direct_factorial_candidate",
        "skipped": False,
        "epochs": [],
        "final_code": code,
        "final_evaluation": {
            "train": summarize_panel(train_results, panel_name="train"),
            "holdout": summarize_panel(holdout_results, panel_name="holdout"),
        },
    }
    summary = summarize_condition(payload)
    return {"payload": payload, "summary": summary}


def _failure_examples(task_family: str, train_summary: dict[str, Any]) -> list[dict[str, Any]]:
    if task_family == "simple_games":
        rows = sorted(train_summary.get("rows", []), key=lambda row: float(row.get("score_margin", 0.0)))[:3]
        return [
            {
                "condition_name": row.get("condition_name"),
                "score_margin": round(float(row.get("score_margin", 0.0)), 6),
                "runtime_issue_count": int(row.get("runtime_issue_count", 0)),
            }
            for row in rows
        ]
    if task_family == "tsp":
        results = sorted(train_summary.get("results", []), key=lambda row: float(row.get("optimality_gap", 0.0)), reverse=True)[:3]
        return [
            {
                "instance_name": row.get("instance", {}).get("name"),
                "family": row.get("instance", {}).get("family"),
                "optimality_gap": round(float(row.get("optimality_gap", 0.0)), 6),
            }
            for row in results
        ]
    summary = train_summary.get("summary", {})
    return [
        {
            "instance_name": row.get("instance_name"),
            "family": row.get("family"),
            "feasible": bool(row.get("feasible", False)),
            "penalized_gap": round(float(row.get("penalized_gap", 0.0)), 6),
            "errors": list(row.get("errors", []))[:3],
        }
        for row in summary.get("worst_instances", [])[:3]
    ]


def _run_cell(
    *,
    config: dict[str, Any],
    output_dir: Path,
    task_family: str,
    model_spec: dict[str, Any],
    technique: str,
    seed: int,
) -> dict[str, Any]:
    task_cfg = config["task_families"][task_family]
    epochs_budget, candidate_budget = _candidate_budget(task_cfg, technique)
    cell_dir = output_dir / "cell_artifacts" / task_family / model_spec["model_tier"] / technique / f"seed_{seed:04d}"
    cell_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = cell_dir / "candidates"
    candidates_dir.mkdir(exist_ok=True)
    generation_cfg = config.get("generation", {})

    if task_family == "simple_games":
        task_state = _simple_game_configs(task_cfg["suite_config"])
        fallback_code = None
    elif task_family == "tsp":
        task_state = load_benchmark_bundle(Path(task_cfg["manifest_path"]))
        fallback_code = default_heuristic_code()
    else:
        cvrp_config = _phase9_config(task_cfg["suite_config"])
        train_instances, holdout_instances, _manifest = _load_instances(
            cvrp_config.benchmark.manifest_path,
            train_limit=int(cvrp_config.benchmark.train_instance_limit),
            holdout_limit=int(cvrp_config.benchmark.holdout_instance_limit),
        )
        task_state = (cvrp_config, train_instances, holdout_instances)
        fallback_code = default_solver_code()

    archive: list[dict[str, Any]] = []
    previous_code: str | None = None
    incumbent_code: str | None = None
    incumbent_train_score: float | None = None
    first_train_score: float | None = None
    accepted_epochs = 0
    generation_success_count = 0
    novelty_values: list[float] = []
    accepted_novelty_values: list[float] = []
    candidate_payloads = []
    replay_rng = random.Random(seed + (17 * len(task_family)) + (31 * len(technique)))

    started = perf_counter()
    for candidate_index in range(1, candidate_budget + 1):
        generated = _generate_candidate(
            task_family=task_family,
            model_spec=model_spec,
            technique=technique,
            candidate_index=candidate_index,
            archive=archive,
            incumbent_code=incumbent_code,
            generation_cfg=generation_cfg,
            replay_rng=replay_rng,
        )
        candidate_code = generated["code"] or fallback_code or ""
        novelty = code_novelty(previous_code, candidate_code)
        novelty_values.append(novelty)
        previous_code = candidate_code
        if not generated["error"] and not generated["used_fallback"]:
            generation_success_count += 1

        if task_family == "simple_games":
            train_summary = _evaluate_simple_game_train(
                candidate_code,
                task_state,
                seed=seed + int(task_cfg.get("seed_base", 0)),
                candidate_index=candidate_index,
            )
            train_score_for_minimization = -float(train_summary["mean_score_margin"])
        elif task_family == "tsp":
            train_summary = _evaluate_tsp_train(
                candidate_code,
                task_state,
                seed=seed + int(task_cfg.get("seed_base", 0)) + (candidate_index * 1000),
            )
            train_score_for_minimization = float(train_summary["train_score_for_minimization"])
        else:
            cvrp_config, train_instances, _holdout_instances = task_state
            train_summary = _evaluate_cvrp_train(candidate_code, train_instances, cvrp_config)
            train_score_for_minimization = float(train_summary["train_score_for_minimization"])
        if first_train_score is None:
            first_train_score = train_score_for_minimization

        accept = False
        if technique == "single_shot":
            accept = candidate_index == 1
        elif incumbent_train_score is None or train_score_for_minimization < incumbent_train_score:
            accept = True
        if accept:
            incumbent_code = candidate_code
            incumbent_train_score = train_score_for_minimization
            accepted_epochs += 1
            if candidate_index > 1:
                accepted_novelty_values.append(novelty)

        failure_note = ""
        if task_family == "simple_games":
            failure_note = f"mean_train_margin={train_summary['mean_score_margin']:.4f}"
        elif task_family == "tsp":
            failure_note = f"mean_train_gap={train_score_for_minimization:.6f}"
        else:
            failure_note = f"mean_train_penalized_gap={train_score_for_minimization:.6f}"
        archive.append(
            {
                "candidate_index": candidate_index,
                "accepted": accept,
                "train_score_for_minimization": round(train_score_for_minimization, 6),
                "novelty": novelty,
                "failure_note": failure_note,
                "failure_examples": _failure_examples(task_family, train_summary),
            }
        )

        candidate_payload = {
            "candidate_index": candidate_index,
            "accepted": accept,
            "generation": generated,
            "novelty": novelty,
            "train_score_for_minimization": train_score_for_minimization,
            "train_summary": train_summary,
        }
        candidate_payloads.append(candidate_payload)
        write_json(candidates_dir / f"candidate_{candidate_index:03d}.json", candidate_payload)

    final_code = incumbent_code or previous_code or fallback_code or ""
    final_code_path = cell_dir / "final_code.py"
    final_code_path.write_text(final_code + "\n", encoding="utf-8")

    if task_family == "simple_games":
        final_eval = _evaluate_simple_game_holdout(final_code, task_state)
        performance_raw = float(final_eval["primary_holdout_win_rate"])
        secondary_raw = float(final_eval["primary_holdout_score_margin"])
        feasibility_rate = None
        runtime_ms = None
        extra_metrics = {
            "primary_holdout_win_rate": performance_raw,
            "primary_holdout_score_margin": secondary_raw,
            "final_tsplib_gap": None,
            "final_transfer_gap": None,
            "adaptation_efficiency": None,
            "heldout_feasibility_rate": None,
            "heldout_penalized_gap": None,
            "heldout_feasible_gap": None,
            "heldout_runtime_ms": None,
        }
    elif task_family == "tsp":
        final_eval = _evaluate_tsp_holdout(final_code, task_state, seed=seed + int(task_cfg.get("seed_base", 0)) + 900_000)
        performance_raw = -float(final_eval["final_tsplib_gap"])
        secondary_raw = -float(final_eval["final_transfer_gap"])
        feasibility_rate = None
        runtime_ms = None
        cumulative_accepted_novelty = sum(accepted_novelty_values)
        adaptation_efficiency = 0.0
        if (
            first_train_score is not None
            and incumbent_train_score is not None
            and cumulative_accepted_novelty >= 1e-9
        ):
            adaptation_efficiency = (first_train_score - incumbent_train_score) / cumulative_accepted_novelty
        extra_metrics = {
            "primary_holdout_win_rate": None,
            "primary_holdout_score_margin": None,
            "final_tsplib_gap": float(final_eval["final_tsplib_gap"]),
            "final_transfer_gap": float(final_eval["final_transfer_gap"]),
            "adaptation_efficiency": adaptation_efficiency,
            "heldout_feasibility_rate": None,
            "heldout_penalized_gap": None,
            "heldout_feasible_gap": None,
            "heldout_runtime_ms": None,
        }
    else:
        cvrp_config, train_instances, holdout_instances = task_state
        final_eval = _evaluate_cvrp_holdout(final_code, train_instances, holdout_instances, cvrp_config)
        summary = final_eval["summary"]
        holdout_panel = final_eval["payload"]["final_evaluation"]["holdout"]
        heldout_feasible_gap = holdout_panel.get("mean_feasible_gap")
        performance_raw = -float(summary["heldout_penalized_gap"])
        secondary_raw = -float(heldout_feasible_gap) if heldout_feasible_gap is not None else None
        feasibility_rate = float(summary["heldout_feasibility_rate"])
        runtime_ms = float(summary["heldout_runtime_ms"])
        extra_metrics = {
            "primary_holdout_win_rate": None,
            "primary_holdout_score_margin": None,
            "final_tsplib_gap": None,
            "final_transfer_gap": None,
            "adaptation_efficiency": None,
            "heldout_feasibility_rate": feasibility_rate,
            "heldout_penalized_gap": float(summary["heldout_penalized_gap"]),
            "heldout_feasible_gap": heldout_feasible_gap,
            "heldout_runtime_ms": runtime_ms,
        }

    duration_seconds = perf_counter() - started
    row = {
        "task_family": task_family,
        "model_tier": model_spec["model_tier"],
        "model_name": _task_model(model_spec, task_family)[1],
        "benchmark_strength_score": float(model_spec["benchmark_strength_score"]),
        "benchmark_score_source": model_spec["benchmark_score_source"],
        "evolution_technique": technique,
        "seed": seed,
        "epochs_budget": epochs_budget,
        "candidate_budget": candidate_budget,
        "performance_raw": performance_raw,
        "performance_z": "",
        "secondary_performance_raw": secondary_raw,
        "feasibility_rate": feasibility_rate,
        "runtime_ms": runtime_ms,
        "generation_success_rate": generation_success_count / max(1, candidate_budget),
        "accepted_epochs": accepted_epochs,
        "acceptance_rate": accepted_epochs / max(1, candidate_budget),
        "mean_code_novelty": fmean(novelty_values) if novelty_values else 0.0,
        "primary_holdout_win_rate": extra_metrics.get("primary_holdout_win_rate"),
        "primary_holdout_score_margin": extra_metrics.get("primary_holdout_score_margin"),
        "final_tsplib_gap": extra_metrics.get("final_tsplib_gap"),
        "final_transfer_gap": extra_metrics.get("final_transfer_gap"),
        "adaptation_efficiency": extra_metrics.get("adaptation_efficiency"),
        "heldout_feasibility_rate": extra_metrics.get("heldout_feasibility_rate"),
        "heldout_penalized_gap": extra_metrics.get("heldout_penalized_gap"),
        "heldout_feasible_gap": extra_metrics.get("heldout_feasible_gap"),
        "heldout_runtime_ms": extra_metrics.get("heldout_runtime_ms"),
        "artifact_path": str(cell_dir),
    }
    run_summary = {
        "row": row,
        "extra_metrics": extra_metrics,
        "final_evaluation": final_eval,
        "archive": archive,
        "candidate_count": len(candidate_payloads),
        "duration_seconds": round(duration_seconds, 3),
        "duration_hhmm": _format_duration(duration_seconds),
        "final_code_path": str(final_code_path),
    }
    write_json(cell_dir / "run_summary.json", run_summary)
    return row


def _format_duration(seconds: float) -> str:
    minutes = int(round(seconds / 60.0))
    hours, remainder = divmod(minutes, 60)
    return f"{hours:02d}:{remainder:02d}"


def _selected(items: list[str], requested: str | None, *, label: str) -> list[str]:
    if not requested:
        return items
    requested_items = [item.strip() for item in requested.split(",") if item.strip()]
    unknown = [item for item in requested_items if item not in items]
    if unknown:
        raise SystemExit(f"Unknown {label}: {', '.join(unknown)}. Valid values: {', '.join(items)}")
    if not requested_items:
        raise SystemExit(f"No {label} values were provided.")
    return requested_items


def _model_specs(config: dict[str, Any], requested: str | None) -> list[dict[str, Any]]:
    specs = list(config["model_tiers"])
    by_tier = {item["model_tier"]: item for item in specs}
    if requested:
        tiers = [item.strip() for item in requested.split(",") if item.strip()]
        unknown = [tier for tier in tiers if tier not in by_tier]
        if unknown:
            raise SystemExit(f"Unknown model-tier: {', '.join(unknown)}. Valid values: {', '.join(by_tier)}")
        if not tiers:
            raise SystemExit("No model-tier values were provided.")
        specs = [by_tier[tier] for tier in tiers]
    return specs


def _validate_config(config: dict[str, Any]) -> None:
    model_tiers = [str(item.get("model_tier", "")) for item in config.get("model_tiers", [])]
    if len(model_tiers) != len(set(model_tiers)):
        raise SystemExit("model_tiers must contain unique model_tier values.")
    required_model_fields = {"model_tier", "provider", "model_name", "benchmark_strength_score", "benchmark_score_source"}
    for spec in config.get("model_tiers", []):
        missing_fields = sorted(required_model_fields - set(spec))
        if missing_fields:
            raise SystemExit(f"Model tier {spec.get('model_tier', '<unknown>')} is missing: {', '.join(missing_fields)}")
    if "task_families" not in config or not isinstance(config["task_families"], dict):
        raise SystemExit("Config must contain a task_families object.")
    unknown_tasks = [task for task in config["task_families"] if task not in TASK_FAMILIES]
    if unknown_tasks:
        raise SystemExit(f"Unknown configured task families: {', '.join(unknown_tasks)}")
    for task, task_cfg in config["task_families"].items():
        for key in ("seeds", "epochs"):
            try:
                value = int(task_cfg[key])
            except (KeyError, TypeError, ValueError) as exc:
                raise SystemExit(f"Task family {task} must define integer {key}.") from exc
            if value < 1:
                raise SystemExit(f"Task family {task} must define {key} >= 1.")
        if "seed_base" in task_cfg:
            try:
                int(task_cfg["seed_base"])
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"Task family {task} must define integer seed_base.") from exc
    official_full_config = str(config.get("output_root", "")).replace("\\", "/").startswith("runs/") and set(config["task_families"]) == set(TASK_FAMILIES)
    if official_full_config:
        if model_tiers != MODEL_TIERS:
            raise SystemExit(f"Official factorial config must define model tiers in order: {', '.join(MODEL_TIERS)}")
        expected_budgets = {
            "simple_games": {"seeds": 10, "epochs": 100},
            "tsp": {"seeds": 20, "epochs": 8},
            "cvrp_phase9_real_world": {"seeds": 20, "epochs": 8},
        }
        for task, expected in expected_budgets.items():
            task_cfg = config["task_families"][task]
            for key, expected_value in expected.items():
                actual_value = int(task_cfg[key])
                if actual_value != expected_value:
                    raise SystemExit(
                        f"Official factorial config must define {task}.{key}={expected_value}, found {actual_value}."
                    )


def _seed_values(task_cfg: dict[str, Any], requested_seed: int | None) -> list[int]:
    if requested_seed is not None:
        return [requested_seed]
    return [int(task_cfg.get("seed_base", 0)) + offset for offset in range(int(task_cfg["seeds"]))]


def _write_model_strength_table(config: dict[str, Any], output_dir: Path) -> None:
    rows = []
    for spec in config["model_tiers"]:
        rows.append(
            {
                "model_tier": spec["model_tier"],
                "provider": spec["provider"],
                "model_name": spec["model_name"],
                "benchmark_strength_score": spec["benchmark_strength_score"],
                "benchmark_score_source": spec["benchmark_score_source"],
                "benchmark_name": spec.get("benchmark_name", ""),
                "benchmark_source_url": spec.get("benchmark_source_url", ""),
                "notes": spec.get("notes", ""),
            }
        )
    write_csv_dicts(output_dir / "model_strength_table.csv", rows, model_strength_columns())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run model-strength x evolution-technique factorial cells.")
    parser.add_argument("--config", default="configs/model_strength_factorial.yaml")
    parser.add_argument("--timestamp", default="")
    parser.add_argument("--task-family", default=None, help="Optional comma-separated subset.")
    parser.add_argument("--model-tier", default=None, help="Optional comma-separated subset.")
    parser.add_argument("--technique", default=None, help="Optional comma-separated subset.")
    parser.add_argument("--seed", type=int, default=None, help="Optional single absolute seed value.")
    parser.add_argument("--skip-existing", action="store_true", help="Do not rerun cells that already have run_summary.json.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    load_env_files(project_root)
    config = load_jsonish_config(args.config)
    _validate_config(config)
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(config.get("output_root", "runs/cross_family_model_x_evolution_factorial"))
    output_dir = output_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "factorial_config_snapshot.json", config)
    _write_model_strength_table(config, output_dir)

    configured_task_families = [task for task in TASK_FAMILIES if task in config["task_families"]]
    task_families = _selected(configured_task_families, args.task_family, label="task-family")
    techniques = _selected(TECHNIQUES, args.technique, label="technique")
    model_specs = _model_specs(config, args.model_tier)
    all_rows = []
    for task_family in task_families:
        task_cfg = config["task_families"][task_family]
        for model_spec in model_specs:
            for technique in techniques:
                for seed in _seed_values(task_cfg, args.seed):
                    cell_dir = output_dir / "cell_artifacts" / task_family / model_spec["model_tier"] / technique / f"seed_{seed:04d}"
                    if args.skip_existing and (cell_dir / "run_summary.json").exists():
                        row = json.loads((cell_dir / "run_summary.json").read_text(encoding="utf-8"))["row"]
                    else:
                        print(f"Running {task_family} {model_spec['model_tier']} {technique} seed={seed}")
                        row = _run_cell(
                            config=config,
                            output_dir=output_dir,
                            task_family=task_family,
                            model_spec=model_spec,
                            technique=technique,
                            seed=seed,
                        )
                    all_rows.append(row)
                    write_csv_dicts(output_dir / "all_runs_long.partial.csv", all_rows, performance_columns())
    write_csv_dicts(output_dir / "all_runs_long.raw.csv", all_rows, performance_columns())
    print(f"Completed factorial cells. Raw results written to: {output_dir / 'all_runs_long.raw.csv'}")
    print(f"Run aggregation with: python aggregate_model_strength_factorial.py --run-root {output_dir}")


if __name__ == "__main__":
    main()
