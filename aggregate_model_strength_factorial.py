from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from llm_grid_battle.pdf_report import write_pdf_report
from model_strength_factorial_common import (
    TASK_FAMILIES,
    TECHNIQUES,
    bootstrap_ci,
    mean_or_none,
    model_strength_columns,
    performance_columns,
    read_csv_dicts,
    safe_float,
    sem_or_zero,
    std_or_zero,
    write_csv_dicts,
    write_json,
)


def _load_rows(run_root: Path) -> list[dict[str, Any]]:
    summaries = sorted(run_root.glob("cell_artifacts/*/*/*/seed_*/run_summary.json"))
    rows = []
    for path in summaries:
        payload = json.loads(path.read_text(encoding="utf-8"))
        row = dict(payload["row"])
        row["artifact_path"] = str(path.parent)
        rows.append(row)
    if not rows and (run_root / "all_runs_long.raw.csv").exists():
        rows = list(read_csv_dicts(run_root / "all_runs_long.raw.csv"))
    return rows


def _write_model_strength_table_if_missing(run_root: Path, rows: list[dict[str, Any]]) -> None:
    path = run_root / "model_strength_table.csv"
    if path.exists():
        return
    observed_tiers = {str(row.get("model_tier")) for row in rows}
    table_rows = []
    config_path = run_root / "factorial_config_snapshot.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            config = {}
        for spec in config.get("model_tiers", []):
            if str(spec.get("model_tier")) not in observed_tiers:
                continue
            table_rows.append(
                {
                    "model_tier": spec.get("model_tier", ""),
                    "provider": spec.get("provider", ""),
                    "model_name": spec.get("model_name", ""),
                    "benchmark_strength_score": spec.get("benchmark_strength_score", ""),
                    "benchmark_score_source": spec.get("benchmark_score_source", ""),
                    "benchmark_name": spec.get("benchmark_name", ""),
                    "benchmark_source_url": spec.get("benchmark_source_url", ""),
                    "notes": spec.get("notes", ""),
                }
            )
    if not table_rows:
        by_tier = {}
        for row in rows:
            tier = str(row.get("model_tier", ""))
            if tier and tier not in by_tier:
                by_tier[tier] = {
                    "model_tier": tier,
                    "provider": "",
                    "model_name": row.get("model_name", ""),
                    "benchmark_strength_score": row.get("benchmark_strength_score", ""),
                    "benchmark_score_source": row.get("benchmark_score_source", ""),
                    "benchmark_name": "",
                    "benchmark_source_url": "",
                    "notes": "Reconstructed by aggregate_model_strength_factorial.py from all_runs_long rows.",
                }
        table_rows = [by_tier[tier] for tier in _model_tiers(rows) if tier in by_tier]
    write_csv_dicts(path, table_rows, model_strength_columns())


def _model_tiers(rows: list[dict[str, Any]]) -> list[str]:
    by_tier: dict[str, float] = {}
    for row in rows:
        tier = str(row.get("model_tier", ""))
        if not tier:
            continue
        if tier not in by_tier:
            by_tier[tier] = float(safe_float(row.get("benchmark_strength_score"), len(by_tier) + 1) or len(by_tier) + 1)
    return [tier for tier, _score in sorted(by_tier.items(), key=lambda item: (item[1], item[0]))]


def _techniques(rows: list[dict[str, Any]]) -> list[str]:
    observed = {str(row.get("evolution_technique", "")) for row in rows if row.get("evolution_technique")}
    ordered = [technique for technique in TECHNIQUES if technique in observed]
    return ordered + sorted(observed - set(ordered))


def _task_families(rows: list[dict[str, Any]]) -> list[str]:
    observed = {str(row.get("task_family", "")) for row in rows if row.get("task_family")}
    ordered = [task for task in TASK_FAMILIES if task in observed]
    return ordered + sorted(observed - set(ordered))


def _add_performance_z(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, list[float]] = {}
    for row in rows:
        value = safe_float(row.get("performance_raw"))
        if value is not None:
            by_task.setdefault(str(row["task_family"]), []).append(value)
    stats = {}
    for task, values in by_task.items():
        mean_value = fmean(values) if values else 0.0
        sd = std_or_zero(values)
        stats[task] = (mean_value, sd)
    output = []
    for row in rows:
        copied = dict(row)
        value = safe_float(copied.get("performance_raw"))
        mean_value, sd = stats.get(str(copied.get("task_family")), (0.0, 0.0))
        copied["performance_z"] = 0.0 if value is None or sd == 0 else (value - mean_value) / sd
        output.append(copied)
    return output


def _group_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return str(row["task_family"]), str(row["model_tier"]), str(row["evolution_technique"])


def _cell_means(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(_group_key(row), []).append(row)
    output = []
    for index, (key, group) in enumerate(sorted(grouped.items())):
        task_family, model_tier, technique = key
        performance = [safe_float(row.get("performance_raw")) for row in group]
        performance = [value for value in performance if value is not None]
        z_values = [safe_float(row.get("performance_z")) for row in group]
        z_values = [value for value in z_values if value is not None]
        ci_low, ci_high = bootstrap_ci(performance, seed=7000 + index)
        output.append(
            {
                "task_family": task_family,
                "model_tier": model_tier,
                "evolution_technique": technique,
                "n_runs": len(group),
                "mean_performance_raw": mean_or_none(performance),
                "std_performance_raw": std_or_zero(performance),
                "sem_performance_raw": sem_or_zero(performance),
                "ci95_low_performance_raw": ci_low,
                "ci95_high_performance_raw": ci_high,
                "mean_performance_z": mean_or_none(z_values),
                "mean_novelty": mean_or_none([safe_float(row.get("mean_code_novelty"), 0.0) or 0.0 for row in group]),
                "mean_runtime_ms": mean_or_none([safe_float(row.get("runtime_ms")) for row in group if safe_float(row.get("runtime_ms")) is not None]),
                "mean_feasibility_rate": mean_or_none([safe_float(row.get("feasibility_rate")) for row in group if safe_float(row.get("feasibility_rate")) is not None]),
                "mean_generation_success_rate": mean_or_none([safe_float(row.get("generation_success_rate"), 0.0) or 0.0 for row in group]),
                "mean_successful_generations": mean_or_none([safe_float(row.get("successful_generations"), 0.0) or 0.0 for row in group]),
                "mean_generation_error_count": mean_or_none([safe_float(row.get("generation_error_count"), 0.0) or 0.0 for row in group]),
                "mean_repair_attempt_count": mean_or_none([safe_float(row.get("repair_attempt_count"), 0.0) or 0.0 for row in group]),
                "mean_salvage_attempt_count": mean_or_none([safe_float(row.get("salvage_attempt_count"), 0.0) or 0.0 for row in group]),
                "mean_executable_candidate_count": mean_or_none([safe_float(row.get("executable_candidate_count"), 0.0) or 0.0 for row in group]),
                "mean_fallback_generation_count": mean_or_none([safe_float(row.get("fallback_generation_count"), 0.0) or 0.0 for row in group]),
                "mean_materialization_fallback_count": mean_or_none([safe_float(row.get("materialization_fallback_count"), 0.0) or 0.0 for row in group]),
                "mean_materialization_timeout_count": mean_or_none([safe_float(row.get("materialization_timeout_count"), 0.0) or 0.0 for row in group]),
                "mean_accepted_fallback_epochs": mean_or_none([safe_float(row.get("accepted_fallback_epochs"), 0.0) or 0.0 for row in group]),
                "mean_accepted_executable_epochs": mean_or_none([safe_float(row.get("accepted_executable_epochs"), 0.0) or 0.0 for row in group]),
                "mean_acceptance_rate": mean_or_none([safe_float(row.get("acceptance_rate"), 0.0) or 0.0 for row in group]),
            }
        )
    return output


def _is_full_factorial(rows: list[dict[str, Any]]) -> bool:
    expected_seed_counts = {
        "simple_games": 10,
        "tsp": 20,
        "cvrp_phase9_real_world": 20,
    }
    model_tiers = _model_tiers(rows)
    techniques = _techniques(rows)
    task_families = _task_families(rows)
    if set(task_families) != set(TASK_FAMILIES):
        return False
    if len(model_tiers) < 2:
        return False
    if set(techniques) != set(TECHNIQUES):
        return False
    if len(rows) != sum(expected_seed_counts[task] * len(model_tiers) * len(techniques) for task in TASK_FAMILIES):
        return False
    for task, expected_seed_count in expected_seed_counts.items():
        for tier in model_tiers:
            for technique in techniques:
                seeds = [
                    str(row.get("seed"))
                    for row in rows
                    if str(row.get("task_family")) == task
                    and str(row.get("model_tier")) == tier
                    and str(row.get("evolution_technique")) == technique
                ]
                if len(seeds) != expected_seed_count or len(set(seeds)) != expected_seed_count:
                    return False
    return True


def _write_matrices(rows: list[dict[str, Any]], run_root: Path) -> None:
    matrix_dir = run_root / "model_x_evolution_matrices"
    matrix_dir.mkdir(exist_ok=True)
    figure_dir = run_root / "figures"
    figure_dir.mkdir(exist_ok=True)
    model_tiers = _model_tiers(rows)
    techniques = _techniques(rows)
    for task in _task_families(rows):
        task_rows = [row for row in rows if row["task_family"] == task]
        matrix_rows = []
        for tier in model_tiers:
            row_payload = {"model_tier": tier}
            for technique in techniques:
                values = [
                    safe_float(row.get("performance_raw"))
                    for row in task_rows
                    if row["model_tier"] == tier and row["evolution_technique"] == technique
                ]
                values = [value for value in values if value is not None]
                row_payload[technique] = mean_or_none(values)
            matrix_rows.append(row_payload)
        path = matrix_dir / f"{_task_slug(task)}_model_x_evolution.csv"
        write_csv_dicts(path, matrix_rows, ["model_tier", *techniques])
        _write_heatmap(
            matrix_rows,
            path=matrix_dir / f"{_task_slug(task)}_model_x_evolution.png",
            title=f"{task} model x evolution",
        )
        _write_heatmap(
            matrix_rows,
            path=figure_dir / f"heatmap_{_task_slug(task)}_model_x_evolution.png",
            title=f"{task} model x evolution",
        )


def _task_slug(task: str) -> str:
    if task == "cvrp_phase9_real_world":
        return "cvrp"
    return task


def _write_heatmap(matrix_rows: list[dict[str, Any]], *, path: Path, title: str) -> None:
    techniques = [key for key in matrix_rows[0] if key != "model_tier"] if matrix_rows else TECHNIQUES
    cell_w = 150
    cell_h = 58
    left = 160
    top = 80
    width = left + (len(techniques) * cell_w) + 40
    height = top + (len(matrix_rows) * cell_h) + 60
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), title, fill=(20, 20, 20), font=font)
    values = [
        safe_float(row.get(technique))
        for row in matrix_rows
        for technique in techniques
        if safe_float(row.get(technique)) is not None
    ]
    low = min(values) if values else 0.0
    high = max(values) if values else 1.0
    span = high - low if high != low else 1.0
    for col, technique in enumerate(techniques):
        draw.text((left + col * cell_w + 6, top - 24), technique.replace("_", "\n"), fill=(20, 20, 20), font=font)
    for row_index, row in enumerate(matrix_rows):
        y = top + row_index * cell_h
        draw.text((20, y + 18), str(row["model_tier"]), fill=(20, 20, 20), font=font)
        for col, technique in enumerate(techniques):
            x = left + col * cell_w
            value = safe_float(row.get(technique))
            if value is None:
                color = (230, 230, 230)
                text = "NA"
            else:
                ratio = (value - low) / span
                color = (int(245 - 120 * ratio), int(245 - 60 * ratio), int(255 - 180 * ratio))
                text = f"{value:.3g}"
            draw.rectangle((x, y, x + cell_w - 4, y + cell_h - 4), fill=color, outline=(90, 90, 90))
            draw.text((x + 8, y + 20), text, fill=(10, 10, 10), font=font)
    image.save(path)


def _design_matrix(rows: list[dict[str, Any]], *, categorical_model: bool, pooled: bool) -> tuple[np.ndarray, np.ndarray, dict[str, list[int]], list[str]]:
    columns: list[list[float]] = []
    names: list[str] = []
    terms: dict[str, list[int]] = {}

    def add_column(name: str, values: list[float], term: str) -> None:
        columns.append(values)
        names.append(name)
        terms.setdefault(term, []).append(len(columns) - 1)

    n = len(rows)
    add_column("intercept", [1.0] * n, "intercept")
    task_levels = sorted({str(row["task_family"]) for row in rows})
    task_base = task_levels[0] if task_levels else ""
    tech_levels = _techniques(rows)
    tech_base = "single_shot"
    tier_levels = _model_tiers(rows)
    tier_base = tier_levels[0] if tier_levels else ""
    score = [float(safe_float(row["benchmark_strength_score"], 0.0) or 0.0) for row in rows]

    task_cols: list[tuple[str, list[float]]] = []
    if pooled:
        for task in task_levels:
            if task == task_base:
                continue
            values = [1.0 if row["task_family"] == task else 0.0 for row in rows]
            task_cols.append((task, values))
            add_column(f"task:{task}", values, "task_family")

    if categorical_model:
        model_cols = []
        for tier in tier_levels:
            if tier == tier_base:
                continue
            values = [1.0 if row["model_tier"] == tier else 0.0 for row in rows]
            model_cols.append((tier, values))
            add_column(f"model:{tier}", values, "model_tier")
    else:
        model_cols = [("benchmark_strength_score", score)]
        add_column("benchmark_strength_score", score, "benchmark_strength_score")

    tech_cols = []
    for technique in tech_levels:
        if technique == tech_base:
            continue
        values = [1.0 if row["evolution_technique"] == technique else 0.0 for row in rows]
        tech_cols.append((technique, values))
        add_column(f"tech:{technique}", values, "evolution_technique")

    if pooled:
        for task_name, task_values in task_cols:
            for model_name, model_values in model_cols:
                add_column(
                    f"task:{task_name}*model:{model_name}",
                    [a * b for a, b in zip(task_values, model_values)],
                    "task_family:model",
                )
            for tech_name, tech_values in tech_cols:
                add_column(
                    f"task:{task_name}*tech:{tech_name}",
                    [a * b for a, b in zip(task_values, tech_values)],
                    "task_family:evolution_technique",
                )
    for model_name, model_values in model_cols:
        for tech_name, tech_values in tech_cols:
            add_column(
                f"model:{model_name}*tech:{tech_name}",
                [a * b for a, b in zip(model_values, tech_values)],
                "model:evolution_technique",
            )
    if pooled:
        for task_name, task_values in task_cols:
            for model_name, model_values in model_cols:
                for tech_name, tech_values in tech_cols:
                    add_column(
                        f"task:{task_name}*model:{model_name}*tech:{tech_name}",
                        [a * b * c for a, b, c in zip(task_values, model_values, tech_values)],
                        "task_family:model:evolution_technique",
                    )

    x = np.array(columns, dtype=float).T
    y = np.array([float(safe_float(row["performance_z"], 0.0) or 0.0) for row in rows], dtype=float)
    return x, y, terms, names


def _fit_sse(x: np.ndarray, y: np.ndarray) -> tuple[float, int, int]:
    if len(y) == 0 or x.size == 0:
        return 0.0, 0, 0
    rank = int(np.linalg.matrix_rank(x))
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    residuals = y - x.dot(beta)
    sse = float(np.sum(residuals ** 2))
    df_resid = max(0, len(y) - rank)
    return sse, rank, df_resid


def _anova(rows: list[dict[str, Any]], *, categorical_model: bool, pooled: bool, label: str) -> list[dict[str, Any]]:
    if len(rows) < 4:
        return [
            {
                "analysis": label,
                "term": "insufficient_data",
                "df": 0,
                "ss_effect": None,
                "semi_partial_r2": None,
                "partial_eta_squared": None,
                "f_stat": None,
                "p_value": None,
                "residual_variance": None,
                "n": len(rows),
            }
        ]
    x, y, terms, _names = _design_matrix(rows, categorical_model=categorical_model, pooled=pooled)
    full_sse, full_rank, df_resid = _fit_sse(x, y)
    sst = float(np.sum((y - np.mean(y)) ** 2))
    residual_variance = full_sse / df_resid if df_resid > 0 else None
    output = []
    for term, indexes in terms.items():
        if term == "intercept":
            continue
        keep = [index for index in range(x.shape[1]) if index not in indexes]
        if not keep:
            continue
        reduced_sse, reduced_rank, _reduced_df = _fit_sse(x[:, keep], y)
        ss_effect = max(0.0, reduced_sse - full_sse)
        df_effect = max(1, full_rank - reduced_rank)
        f_stat = None
        p_value = None
        if df_resid > 0 and residual_variance is not None and residual_variance > 0:
            f_stat = (ss_effect / df_effect) / residual_variance
            p_value = _f_sf(f_stat, df_effect, df_resid)
        output.append(
            {
                "analysis": label,
                "term": term,
                "df": df_effect,
                "ss_effect": ss_effect,
                "semi_partial_r2": ss_effect / sst if sst > 0 else None,
                "partial_eta_squared": ss_effect / (ss_effect + full_sse) if (ss_effect + full_sse) > 0 else None,
                "f_stat": f_stat,
                "p_value": p_value,
                "residual_variance": residual_variance,
                "n": len(rows),
            }
        )
    return output


def _f_sf(f_value: float, df1: int, df2: int) -> float | None:
    if f_value < 0 or df1 <= 0 or df2 <= 0:
        return None
    x = df2 / (df2 + df1 * f_value)
    return _regularized_beta(x, df2 / 2.0, df1 / 2.0)


def _regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(log_beta + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return front * _beta_cf(a, b, x) / a
    return 1 - front * _beta_cf(b, a, 1 - x) / b


def _beta_cf(a: float, b: float, x: float) -> float:
    max_iter = 200
    eps = 3e-7
    fpmin = 1e-30
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _variance_decomposition(rows: list[dict[str, Any]], run_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    variance_dir = run_root / "variance_decomposition"
    variance_dir.mkdir(exist_ok=True)
    task_specific = []
    for task in _task_families(rows):
        task_rows = [row for row in rows if row["task_family"] == task]
        task_specific.extend(_anova(task_rows, categorical_model=False, pooled=False, label=f"{task}:continuous"))
        task_specific.extend(_anova(task_rows, categorical_model=True, pooled=False, label=f"{task}:categorical"))
    pooled = []
    pooled.extend(_anova(rows, categorical_model=False, pooled=True, label="pooled:continuous"))
    pooled.extend(_anova(rows, categorical_model=True, pooled=True, label="pooled:categorical"))
    no_tsp_rows = [row for row in rows if str(row.get("task_family")) != "tsp"]
    if no_tsp_rows:
        pooled.extend(_anova(no_tsp_rows, categorical_model=False, pooled=True, label="pooled_without_tsp:continuous"))
        pooled.extend(_anova(no_tsp_rows, categorical_model=True, pooled=True, label="pooled_without_tsp:categorical"))
    summary = _partition_summary(task_specific + pooled)
    common_fields = [
        "analysis",
        "term",
        "df",
        "ss_effect",
        "semi_partial_r2",
        "partial_eta_squared",
        "f_stat",
        "p_value",
        "residual_variance",
        "n",
    ]
    write_csv_dicts(variance_dir / "task_specific_anova.csv", task_specific, common_fields)
    write_csv_dicts(variance_dir / "pooled_anova.csv", pooled, common_fields)
    write_csv_dicts(
        variance_dir / "variance_partition_summary.csv",
        summary,
        ["analysis_scope", "model_strength_r2", "evolution_technique_r2", "interaction_r2", "residual_variance", "n"],
    )
    return task_specific, pooled, summary


def _partition_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_analysis: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_analysis.setdefault(str(row["analysis"]), []).append(row)
    output = []
    for analysis, group in sorted(by_analysis.items()):
        model_terms = [row for row in group if row["term"] in {"benchmark_strength_score", "model_tier"}]
        evolution_terms = [row for row in group if row["term"] == "evolution_technique"]
        interaction_terms = [row for row in group if "evolution_technique" in str(row["term"]) and row["term"] != "evolution_technique"]
        output.append(
            {
                "analysis_scope": analysis,
                "model_strength_r2": sum(float(row.get("semi_partial_r2") or 0.0) for row in model_terms),
                "evolution_technique_r2": sum(float(row.get("semi_partial_r2") or 0.0) for row in evolution_terms),
                "interaction_r2": sum(float(row.get("semi_partial_r2") or 0.0) for row in interaction_terms),
                "residual_variance": next((row.get("residual_variance") for row in group if row.get("residual_variance") not in (None, "")), None),
                "n": next((row.get("n") for row in group), 0),
            }
        )
    return output


def _effect_sizes(rows: list[dict[str, Any]], run_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    effect_dir = run_root / "effect_sizes"
    effect_dir.mkdir(exist_ok=True)
    vs_single = []
    vs_budget = []
    for task in _task_families(rows):
        for tier in _model_tiers(rows):
            subset = [row for row in rows if row["task_family"] == task and row["model_tier"] == tier]
            for reference in ["single_shot", "budget_matched_no_replay"]:
                ref_rows = [row for row in subset if row["evolution_technique"] == reference]
                for technique in TECHNIQUES:
                    if technique == reference:
                        continue
                    if reference == "budget_matched_no_replay" and technique == "single_shot":
                        continue
                    cand_rows = [row for row in subset if row["evolution_technique"] == technique]
                    effect = _compare_effect(task, tier, technique, reference, cand_rows, ref_rows)
                    if reference == "single_shot":
                        vs_single.append(effect)
                    else:
                        vs_budget.append(effect)
    fields = [
        "task_family",
        "model_tier",
        "evolution_technique",
        "reference_condition",
        "test_type",
        "n_candidate",
        "n_reference",
        "mean_candidate",
        "mean_reference",
        "mean_delta",
        "percent_delta",
        "cohens_d",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "beats_reference",
    ]
    write_csv_dicts(effect_dir / "evolution_vs_single_shot_effects.csv", vs_single, fields)
    write_csv_dicts(effect_dir / "evolution_vs_budget_matched_effects.csv", vs_budget, fields)
    return vs_single, vs_budget


def _cvrp_metric_decomposition(rows: list[dict[str, Any]], run_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cvrp_rows = [row for row in rows if str(row.get("task_family")) == "cvrp_phase9_real_world"]
    output_dir = run_root / "cvrp_decomposition"
    output_dir.mkdir(exist_ok=True)
    metric_specs = [
        ("feasibility_escape_rate", "heldout_feasibility_rate", 1.0),
        ("penalized_objective_quality", "heldout_penalized_gap", -1.0),
        ("feasible_only_objective_quality", "heldout_feasible_gap", -1.0),
    ]
    cell_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []
    for tier in _model_tiers(cvrp_rows):
        tier_rows = [row for row in cvrp_rows if str(row.get("model_tier")) == tier]
        for technique in _techniques(tier_rows):
            group = [row for row in tier_rows if str(row.get("evolution_technique")) == technique]
            payload = {"model_tier": tier, "evolution_technique": technique, "n_runs": len(group)}
            for metric_name, column, direction in metric_specs:
                values = [safe_float(row.get(column)) for row in group]
                values = [value for value in values if value is not None]
                oriented = [direction * value for value in values]
                payload[f"mean_{metric_name}"] = mean_or_none(values)
                payload[f"mean_oriented_{metric_name}"] = mean_or_none(oriented)
                low, high = bootstrap_ci(oriented, seed=42000 + sum(ord(char) for char in f"{tier}|{technique}|{metric_name}"))
                payload[f"ci95_low_oriented_{metric_name}"] = low
                payload[f"ci95_high_oriented_{metric_name}"] = high
            cell_rows.append(payload)
        reference_rows = [row for row in tier_rows if str(row.get("evolution_technique")) == "budget_matched_no_replay"]
        for technique in _techniques(tier_rows):
            if technique in {"single_shot", "budget_matched_no_replay"}:
                continue
            candidate_rows = [row for row in tier_rows if str(row.get("evolution_technique")) == technique]
            for metric_name, column, direction in metric_specs:
                effect_rows.append(_compare_metric_effect(tier, technique, candidate_rows, reference_rows, metric_name, column, direction))
    cell_fields = ["model_tier", "evolution_technique", "n_runs"]
    for metric_name, _column, _direction in metric_specs:
        cell_fields.extend(
            [
                f"mean_{metric_name}",
                f"mean_oriented_{metric_name}",
                f"ci95_low_oriented_{metric_name}",
                f"ci95_high_oriented_{metric_name}",
            ]
        )
    effect_fields = [
        "model_tier",
        "evolution_technique",
        "reference_condition",
        "metric",
        "metric_column",
        "direction",
        "test_type",
        "n_candidate",
        "n_reference",
        "mean_candidate_raw",
        "mean_reference_raw",
        "mean_oriented_delta",
        "cohens_d",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "beats_budget_matched_control",
    ]
    write_csv_dicts(output_dir / "cvrp_metric_cell_means.csv", cell_rows, cell_fields)
    write_csv_dicts(output_dir / "cvrp_vs_budget_matched_metric_effects.csv", effect_rows, effect_fields)
    return cell_rows, effect_rows


def _compare_metric_effect(
    tier: str,
    technique: str,
    cand_rows: list[dict[str, Any]],
    ref_rows: list[dict[str, Any]],
    metric_name: str,
    column: str,
    direction: float,
) -> dict[str, Any]:
    cand_by_seed = {str(row["seed"]): safe_float(row.get(column)) for row in cand_rows}
    ref_by_seed = {str(row["seed"]): safe_float(row.get(column)) for row in ref_rows}
    paired_seeds = sorted(seed for seed in cand_by_seed if seed in ref_by_seed and cand_by_seed[seed] is not None and ref_by_seed[seed] is not None)
    if paired_seeds:
        candidate_values = [float(cand_by_seed[seed]) for seed in paired_seeds]
        reference_values = [float(ref_by_seed[seed]) for seed in paired_seeds]
        deltas = [direction * (candidate - reference) for candidate, reference in zip(candidate_values, reference_values)]
        test_type = "paired_by_seed"
    else:
        candidate_values = [safe_float(row.get(column)) for row in cand_rows]
        reference_values = [safe_float(row.get(column)) for row in ref_rows]
        candidate_values = [value for value in candidate_values if value is not None]
        reference_values = [value for value in reference_values if value is not None]
        deltas = [direction * (candidate - reference) for candidate in candidate_values for reference in reference_values]
        test_type = "unpaired_all_pairs"
    mean_delta = mean_or_none(deltas)
    pooled_sd = std_or_zero(deltas) if test_type == "paired_by_seed" else math.sqrt(
        (std_or_zero([direction * value for value in candidate_values]) ** 2 + std_or_zero([direction * value for value in reference_values]) ** 2) / 2.0
    )
    seed = 47000 + sum(ord(char) for char in f"{tier}|{technique}|{metric_name}")
    ci_low, ci_high = bootstrap_ci(deltas, seed=seed)
    return {
        "model_tier": tier,
        "evolution_technique": technique,
        "reference_condition": "budget_matched_no_replay",
        "metric": metric_name,
        "metric_column": column,
        "direction": "higher_is_better" if direction > 0 else "lower_is_better",
        "test_type": test_type,
        "n_candidate": len(candidate_values),
        "n_reference": len(reference_values),
        "mean_candidate_raw": mean_or_none(candidate_values),
        "mean_reference_raw": mean_or_none(reference_values),
        "mean_oriented_delta": mean_delta,
        "cohens_d": mean_delta / pooled_sd if mean_delta is not None and pooled_sd > 0 else None,
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "beats_budget_matched_control": bool(mean_delta is not None and ci_low is not None and mean_delta > 0 and ci_low > 0),
    }


def _tsp_diagnostics(rows: list[dict[str, Any]], run_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tsp_rows = [row for row in rows if str(row.get("task_family")) == "tsp"]
    output_dir = run_root / "tsp_diagnostics"
    output_dir.mkdir(exist_ok=True)
    metric_columns = ["final_tsplib_gap", "final_transfer_gap", "final_synthetic_holdout_gap", "final_worst_gap", "performance_raw"]
    saturation_rows: list[dict[str, Any]] = []
    for column in metric_columns:
        values = [safe_float(row.get(column)) for row in tsp_rows]
        values = [value for value in values if value is not None]
        rounded_unique = len({round(value, 6) for value in values})
        saturation_rows.append(
            {
                "metric": column,
                "n": len(values),
                "mean": mean_or_none(values),
                "std": std_or_zero(values),
                "rounded_unique_values": rounded_unique,
                "saturated_flag": bool(values and (std_or_zero(values) <= 1e-6 or rounded_unique <= max(2, int(0.02 * len(values))))),
            }
        )
    audit_rows: list[dict[str, Any]] = []
    for row in tsp_rows:
        artifact_path = Path(str(row.get("artifact_path", "")))
        for candidate_path in sorted((artifact_path / "candidates").glob("candidate_*.json")):
            try:
                payload = json.loads(candidate_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            train_summary = payload.get("train_summary", {})
            generation = payload.get("generation", {})
            issues = [str(item) for item in train_summary.get("materialization_issues", [])]
            used_fallback = bool(train_summary.get("materialization_used_fallback"))
            timeout = any("timeout" in item.lower() for item in issues)
            if used_fallback or timeout or generation.get("used_fallback"):
                audit_rows.append(
                    {
                        "model_tier": row.get("model_tier"),
                        "model_name": row.get("model_name"),
                        "evolution_technique": row.get("evolution_technique"),
                        "seed": row.get("seed"),
                        "candidate_index": payload.get("candidate_index"),
                        "accepted": payload.get("accepted"),
                        "generation_used_fallback": generation.get("used_fallback"),
                        "generation_error": generation.get("error"),
                        "materialization_used_fallback": used_fallback,
                        "materialization_timeout": timeout,
                        "materialization_issues": "; ".join(issues),
                        "candidate_path": str(candidate_path),
                    }
                )
    write_csv_dicts(
        output_dir / "tsp_saturation_diagnostics.csv",
        saturation_rows,
        ["metric", "n", "mean", "std", "rounded_unique_values", "saturated_flag"],
    )
    write_csv_dicts(
        output_dir / "tsp_materialization_audit.csv",
        audit_rows,
        [
            "model_tier",
            "model_name",
            "evolution_technique",
            "seed",
            "candidate_index",
            "accepted",
            "generation_used_fallback",
            "generation_error",
            "materialization_used_fallback",
            "materialization_timeout",
            "materialization_issues",
            "candidate_path",
        ],
    )
    return saturation_rows, audit_rows


def _compare_effect(
    task: str,
    tier: str,
    technique: str,
    reference: str,
    cand_rows: list[dict[str, Any]],
    ref_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    cand_by_seed = {str(row["seed"]): safe_float(row.get("performance_raw")) for row in cand_rows}
    ref_by_seed = {str(row["seed"]): safe_float(row.get("performance_raw")) for row in ref_rows}
    paired_seeds = sorted(seed for seed in cand_by_seed if seed in ref_by_seed and cand_by_seed[seed] is not None and ref_by_seed[seed] is not None)
    if paired_seeds:
        deltas = [float(cand_by_seed[seed]) - float(ref_by_seed[seed]) for seed in paired_seeds]
        candidate_values = [float(cand_by_seed[seed]) for seed in paired_seeds]
        reference_values = [float(ref_by_seed[seed]) for seed in paired_seeds]
        test_type = "paired_by_seed"
    else:
        candidate_values = [safe_float(row.get("performance_raw")) for row in cand_rows]
        reference_values = [safe_float(row.get("performance_raw")) for row in ref_rows]
        candidate_values = [value for value in candidate_values if value is not None]
        reference_values = [value for value in reference_values if value is not None]
        deltas = [cand - ref for cand in candidate_values for ref in reference_values]
        test_type = "unpaired_all_pairs"
    mean_candidate = mean_or_none(candidate_values)
    mean_reference = mean_or_none(reference_values)
    mean_delta = mean_or_none(deltas)
    if test_type == "paired_by_seed":
        pooled_sd = std_or_zero(deltas)
    else:
        pooled_sd = math.sqrt((std_or_zero(candidate_values) ** 2 + std_or_zero(reference_values) ** 2) / 2.0)
    stable_seed = 9001 + sum(ord(char) for char in f"{task}|{tier}|{technique}|{reference}")
    ci_low, ci_high = bootstrap_ci(deltas, seed=stable_seed)
    return {
        "task_family": task,
        "model_tier": tier,
        "evolution_technique": technique,
        "reference_condition": reference,
        "test_type": test_type,
        "n_candidate": len(candidate_values),
        "n_reference": len(reference_values),
        "mean_candidate": mean_candidate,
        "mean_reference": mean_reference,
        "mean_delta": mean_delta,
        "percent_delta": (100.0 * mean_delta / abs(mean_reference)) if mean_delta is not None and mean_reference not in (None, 0.0) else None,
        "cohens_d": mean_delta / pooled_sd if mean_delta is not None and pooled_sd > 0 else None,
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "beats_reference": bool(mean_delta is not None and ci_low is not None and mean_delta > 0 and ci_low > 0),
    }


def _write_barplot(rows: list[dict[str, Any]], *, path: Path, title: str, keys: list[str]) -> None:
    width = 1000
    height = 460
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), title, fill=(20, 20, 20), font=font)
    subset = rows[:12]
    max_value = max([float(row.get(key) or 0.0) for row in subset for key in keys] or [1.0]) or 1.0
    group_w = 72
    bar_w = 16
    base_y = 390
    colors = [(79, 129, 189), (192, 80, 77), (155, 187, 89)]
    for index, row in enumerate(subset):
        x0 = 80 + index * group_w
        for key_index, key in enumerate(keys):
            value = float(row.get(key) or 0.0)
            bar_h = int((value / max_value) * 280)
            x = x0 + key_index * (bar_w + 3)
            draw.rectangle((x, base_y - bar_h, x + bar_w, base_y), fill=colors[key_index % len(colors)])
        draw.text((x0, base_y + 8), str(row.get("analysis_scope", ""))[:10], fill=(20, 20, 20), font=font)
    for key_index, key in enumerate(keys):
        draw.rectangle((760, 60 + key_index * 22, 774, 74 + key_index * 22), fill=colors[key_index % len(colors)])
        draw.text((782, 58 + key_index * 22), key, fill=(20, 20, 20), font=font)
    image.save(path)


def _write_line_figures(rows: list[dict[str, Any]], effects_budget: list[dict[str, Any]], run_root: Path) -> None:
    figure_dir = run_root / "figures"
    figure_dir.mkdir(exist_ok=True)
    _write_interaction_plot(rows, figure_dir / "interaction_plot_by_task.png")
    _write_scaling_curves(rows, figure_dir / "model_strength_scaling_curves.png")
    _write_gain_plot(effects_budget, figure_dir / "evolution_gain_over_budget_control.png")


def _mean_by(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[tuple[str, ...], float]:
    grouped: dict[tuple[str, ...], list[float]] = {}
    for row in rows:
        value = safe_float(row.get("performance_z"))
        if value is None:
            continue
        grouped.setdefault(tuple(str(row[key]) for key in keys), []).append(value)
    return {key: fmean(values) for key, values in grouped.items()}


def _write_interaction_plot(rows: list[dict[str, Any]], path: Path) -> None:
    means = _mean_by(rows, ("task_family", "model_tier", "evolution_technique"))
    task_families = _task_families(rows)
    model_tiers = _model_tiers(rows)
    techniques = _techniques(rows)
    image = Image.new("RGB", (1100, 620), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), "Interaction plot by task (mean performance_z)", fill=(20, 20, 20), font=font)
    colors = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189)]
    for task_index, task in enumerate(task_families):
        x0 = 70 + task_index * 340
        y0 = 90
        tier_spacing = 260 / max(1, len(model_tiers) - 1) if len(model_tiers) > 1 else 0
        draw.text((x0, y0 - 24), task, fill=(20, 20, 20), font=font)
        draw.line((x0, y0 + 220, x0 + 260, y0 + 220), fill=(0, 0, 0))
        draw.line((x0, y0, x0, y0 + 220), fill=(0, 0, 0))
        for tech_index, technique in enumerate(techniques):
            points = []
            for tier_index, tier in enumerate(model_tiers):
                value = means.get((task, tier, technique))
                if value is None:
                    continue
                x = x0 + int(tier_index * tier_spacing)
                y = y0 + 110 - int(value * 45)
                points.append((x, y))
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=colors[tech_index])
            if len(points) >= 2:
                draw.line(points, fill=colors[tech_index], width=2)
        for tier_index, tier in enumerate(model_tiers):
            draw.text((x0 + int(tier_index * tier_spacing), y0 + 230), str(tier).replace("_model", "")[:8], fill=(20, 20, 20), font=font)
    for tech_index, technique in enumerate(techniques):
        draw.rectangle((750, 420 + tech_index * 24, 764, 434 + tech_index * 24), fill=colors[tech_index])
        draw.text((772, 418 + tech_index * 24), technique, fill=(20, 20, 20), font=font)
    image.save(path)


def _write_scaling_curves(rows: list[dict[str, Any]], path: Path) -> None:
    means = _mean_by(rows, ("benchmark_strength_score", "evolution_technique"))
    techniques = _techniques(rows)
    image = Image.new("RGB", (900, 520), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), "Model strength scaling curves (pooled performance_z)", fill=(20, 20, 20), font=font)
    x0, y0, w, h = 80, 80, 650, 340
    draw.rectangle((x0, y0, x0 + w, y0 + h), outline=(0, 0, 0))
    scores = sorted({float(row["benchmark_strength_score"]) for row in rows})
    min_score, max_score = (min(scores), max(scores)) if scores else (0.0, 1.0)
    span_score = max_score - min_score if max_score != min_score else 1.0
    values = list(means.values())
    min_value, max_value = (min(values), max(values)) if values else (-1.0, 1.0)
    span_value = max_value - min_value if max_value != min_value else 1.0
    colors = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189)]
    for tech_index, technique in enumerate(techniques):
        points = []
        for score in scores:
            value = means.get((str(score), technique)) or means.get((f"{score}", technique))
            if value is None:
                continue
            x = x0 + int(((score - min_score) / span_score) * w)
            y = y0 + h - int(((value - min_value) / span_value) * h)
            points.append((x, y))
        if len(points) >= 2:
            draw.line(points, fill=colors[tech_index], width=2)
        for point in points:
            draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill=colors[tech_index])
        draw.rectangle((760, 90 + tech_index * 24, 774, 104 + tech_index * 24), fill=colors[tech_index])
        draw.text((782, 88 + tech_index * 24), technique, fill=(20, 20, 20), font=font)
    image.save(path)


def _write_gain_plot(effects: list[dict[str, Any]], path: Path) -> None:
    image = Image.new("RGB", (1100, 560), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), "Evolution gain over budget-matched no-replay control", fill=(20, 20, 20), font=font)
    valid = [row for row in effects if row["evolution_technique"] not in {"single_shot", "budget_matched_no_replay"}]
    values = [float(row.get("mean_delta") or 0.0) for row in valid]
    max_abs = max([abs(value) for value in values] or [1.0]) or 1.0
    base_y = 280
    draw.line((60, base_y, 1040, base_y), fill=(0, 0, 0))
    for index, row in enumerate(valid[:35]):
        x = 70 + index * 28
        value = float(row.get("mean_delta") or 0.0)
        bar_h = int((abs(value) / max_abs) * 210)
        color = (44, 160, 44) if value >= 0 else (214, 39, 40)
        if value >= 0:
            draw.rectangle((x, base_y - bar_h, x + 16, base_y), fill=color)
        else:
            draw.rectangle((x, base_y, x + 16, base_y + bar_h), fill=color)
    image.save(path)


def _final_report(
    rows: list[dict[str, Any]],
    cell_means: list[dict[str, Any]],
    variance_summary: list[dict[str, Any]],
    effects_single: list[dict[str, Any]],
    effects_budget: list[dict[str, Any]],
    cvrp_metric_effects: list[dict[str, Any]],
    tsp_saturation_rows: list[dict[str, Any]],
    tsp_audit_rows: list[dict[str, Any]],
    run_root: Path,
) -> str:
    full_design_complete = _is_full_factorial(rows)
    model_tiers = _model_tiers(rows)
    lines = [
        "# Clean Model-Strength Continuum with Saturation and Feasibility Decomposition",
        "",
        "## Purpose",
        "",
        "This factorial analysis tests whether evolutionary code search adds performance above base model coding strength across simple games, symmetric TSP, and real-world CVRP.",
        "",
        "## Experimental design",
        "",
        f"Rows analyzed: {len(rows)}. Task families present: {', '.join(sorted({row['task_family'] for row in rows}))}.",
        "",
        f"The planned full design is {len(model_tiers)} model tiers x 5 techniques with 10 simple-game seeds and 20 TSP/CVRP seeds per cell. Partial or smoke outputs are marked by their row counts.",
        "",
        "## Model tiers and benchmark strength scores",
        "",
        "See `model_strength_table.csv`. The analysis supports both categorical `model_tier` and continuous `benchmark_strength_score`.",
        "",
        "## Evolutionary techniques",
        "",
        "Techniques: `single_shot`, `budget_matched_no_replay`, `random_replay`, `failure_replay`, and `failure_replay_compression`.",
        "",
        "## Task-specific results",
        "",
        _markdown_cell_table(cell_means),
        "",
        "## Model x evolution matrices",
        "",
        "CSV matrices and matching matrix heatmaps are in `model_x_evolution_matrices/`; duplicated report heatmaps are in `figures/`.",
        "",
        "## Variance decomposition",
        "",
        "This is a secondary diagnostic; paired/bootstrap comparisons below are the primary inferential layer for replay and budget-control claims.",
        "",
        "Formulas:",
        "",
        "- Task continuous: `performance_z ~ benchmark_strength_score + C(evolution_technique) + benchmark_strength_score:C(evolution_technique)`.",
        "- Task categorical: `performance_z ~ C(model_tier) * C(evolution_technique)`.",
        "- Pooled continuous: `performance_z ~ C(task_family) * benchmark_strength_score * C(evolution_technique)`.",
        "- Pooled categorical: `performance_z ~ C(task_family) * C(model_tier) * C(evolution_technique)`.",
        "",
        _variance_answer(variance_summary, full_design_complete=full_design_complete),
        "",
        _variance_without_tsp_answer(variance_summary, full_design_complete=full_design_complete),
        "",
        "## Effect sizes relative to single-shot",
        "",
        "Primary paired/bootstrap inference starts here.",
        "",
        _effect_answer(effects_single, "single-shot"),
        "",
        "## Effect sizes relative to budget-matched no-replay",
        "",
        _effect_answer(effects_budget, "budget-matched no-replay"),
        "",
        "## CVRP feasibility and optimization decomposition",
        "",
        _cvrp_decomposition_answer(cvrp_metric_effects),
        "",
        "Detailed CVRP metric tables are in `cvrp_decomposition/`.",
        "",
        "## TSP saturation and materialization audit",
        "",
        _tsp_diagnostics_answer(tsp_saturation_rows, tsp_audit_rows),
        "",
        "Detailed TSP saturation and materialization audit tables are in `tsp_diagnostics/`.",
        "",
        "## Cross-family interpretation",
        "",
        _interpretation(rows, variance_summary, effects_budget, full_design_complete=full_design_complete),
        "",
        "## Main conclusion",
        "",
        _main_conclusion(variance_summary, effects_budget, full_design_complete=full_design_complete),
        "",
        "## Limitations",
        "",
        "- Do not overclaim algorithmic discovery; this phase compares model strength and search technique, not novelty of discovered algorithms.",
        "- Replay/failure/compression should be claimed useful only when they beat `budget_matched_no_replay`, not merely when they beat `single_shot`.",
        "- Smoke runs validate schema only; scientific conclusions require the full paid campaign.",
        "- P-values use reduced-model OLS/ANOVA approximations implemented locally to avoid adding heavy statistics dependencies.",
        "- The primary inferential layer is the paired/bootstrap effect table; pooled OLS/ANOVA is retained as a secondary variance-decomposition diagnostic.",
        "",
        "## Required Questions",
        "",
        _required_questions(variance_summary, effects_budget, full_design_complete=full_design_complete),
        "",
        "## Artifact Paths",
        "",
        f"- `all_runs_long.csv`: `{run_root / 'all_runs_long.csv'}`",
        f"- `variance_partition_summary.csv`: `{run_root / 'variance_decomposition' / 'variance_partition_summary.csv'}`",
        f"- `cvrp_vs_budget_matched_metric_effects.csv`: `{run_root / 'cvrp_decomposition' / 'cvrp_vs_budget_matched_metric_effects.csv'}`",
        f"- `tsp_materialization_audit.csv`: `{run_root / 'tsp_diagnostics' / 'tsp_materialization_audit.csv'}`",
    ]
    return "\n".join(lines)


def _markdown_cell_table(rows: list[dict[str, Any]]) -> str:
    lines = ["| task | model | technique | n | mean performance_z | mean raw | mean novelty |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(
            f"| {row['task_family']} | {row['model_tier']} | {row['evolution_technique']} | {row['n_runs']} | "
            f"{_fmt(row.get('mean_performance_z'))} | {_fmt(row.get('mean_performance_raw'))} | {_fmt(row.get('mean_novelty'))} |"
        )
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    parsed = safe_float(value)
    return "" if parsed is None else f"{parsed:.4g}"


def _variance_answer(summary: list[dict[str, Any]], *, full_design_complete: bool) -> str:
    pooled = [row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"]
    if not pooled:
        return "Insufficient data for pooled variance decomposition."
    row = pooled[0]
    if not full_design_complete:
        return "Incomplete factorial data: this output validates the schema and analysis pipeline only. Scientific variance conclusions require the full crossed campaign."
    return (
        f"Pooled continuous model: model-strength R2={_fmt(row.get('model_strength_r2'))}, "
        f"evolution-technique R2={_fmt(row.get('evolution_technique_r2'))}, "
        f"interaction R2={_fmt(row.get('interaction_r2'))}, residual variance={_fmt(row.get('residual_variance'))}."
    )


def _variance_without_tsp_answer(summary: list[dict[str, Any]], *, full_design_complete: bool) -> str:
    pooled = [row for row in summary if str(row["analysis_scope"]) == "pooled_without_tsp:continuous"]
    if not pooled:
        return "Pooled-without-TSP variance decomposition was not available."
    if not full_design_complete:
        return "Pooled-without-TSP variance decomposition is schema-only until the full campaign is complete."
    row = pooled[0]
    return (
        f"Pooled without TSP: model-strength R2={_fmt(row.get('model_strength_r2'))}, "
        f"evolution-technique R2={_fmt(row.get('evolution_technique_r2'))}, "
        f"interaction R2={_fmt(row.get('interaction_r2'))}, residual variance={_fmt(row.get('residual_variance'))}."
    )


def _effect_answer(effects: list[dict[str, Any]], label: str) -> str:
    beating = [row for row in effects if str(row.get("beats_reference")).lower() == "true"]
    return f"{len(beating)} comparisons have bootstrap CIs above zero relative to {label}."


def _cvrp_decomposition_answer(effects: list[dict[str, Any]]) -> str:
    if not effects:
        return "No CVRP metric-decomposition effects are available."
    by_metric: dict[str, int] = {}
    for row in effects:
        if str(row.get("beats_budget_matched_control")).lower() == "true":
            metric = str(row.get("metric"))
            by_metric[metric] = by_metric.get(metric, 0) + 1
    return (
        "CVRP is analyzed as three separate outcomes: feasibility/penalty escape, penalized objective quality, "
        "and feasible-only objective quality. Positive paired/bootstrap comparisons versus budget-matched no-replay by metric: "
        f"{by_metric if by_metric else 'none'}."
    )


def _tsp_diagnostics_answer(saturation_rows: list[dict[str, Any]], audit_rows: list[dict[str, Any]]) -> str:
    if not saturation_rows:
        return "No TSP rows were available for saturation diagnostics."
    saturated_metrics = [str(row.get("metric")) for row in saturation_rows if str(row.get("saturated_flag")).lower() == "true"]
    timeout_count = sum(1 for row in audit_rows if str(row.get("materialization_timeout")).lower() == "true")
    fallback_count = sum(1 for row in audit_rows if str(row.get("materialization_used_fallback")).lower() == "true")
    return (
        f"Saturation flags: {saturated_metrics if saturated_metrics else 'none at the configured threshold'}. "
        f"Materialization audit rows: {len(audit_rows)} total, {fallback_count} materialization fallbacks, {timeout_count} timeout-marked rows."
    )


def _interpretation(
    rows: list[dict[str, Any]],
    summary: list[dict[str, Any]],
    effects_budget: list[dict[str, Any]],
    *,
    full_design_complete: bool,
) -> str:
    if not full_design_complete:
        return (
            f"Incomplete factorial data: {len(rows)} rows are present. "
            "Use this report for schema validation only; do not interpret replay, model-strength, or interaction effects until the full paid campaign is aggregated."
        )
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    return (
        "The interpretation should focus on the budget control. "
        f"Replay/failure/compression techniques beat budget-matched no-replay in {len(positive_budget)} tested task/model comparisons with positive bootstrap support; "
        "therefore, gains over single-shot should be interpreted primarily as effects of extra search budget unless a task-specific budget-control comparison supports a stronger claim. "
        + _variance_answer(summary, full_design_complete=full_design_complete)
    )


def _main_conclusion(
    summary: list[dict[str, Any]],
    effects_budget: list[dict[str, Any]],
    *,
    full_design_complete: bool,
) -> str:
    pooled = next((row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"), None)
    if pooled is None:
        return "Smoke data validate the schema, but the full paid campaign is required for the empirical conclusion."
    if not full_design_complete:
        return "Smoke or partial data validate the schema, but the full paid campaign is required for the empirical conclusion."
    model_r2 = float(pooled.get("model_strength_r2") or 0.0)
    evo_r2 = float(pooled.get("evolution_technique_r2") or 0.0)
    interaction_r2 = float(pooled.get("interaction_r2") or 0.0)
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    if model_r2 > evo_r2 and positive_budget:
        return "Model strength explains the largest share of variance, while evolutionary technique adds task/model-dependent value beyond budget-matched search."
    if model_r2 > evo_r2:
        return "Model strength dominates, and replay/failure/compression do not yet show reliable value beyond budget-matched search."
    if positive_budget:
        return (
            "The configured model continuum does not show clean model-strength dominance; "
            f"model-strength R2={_fmt(model_r2)}, evolution-technique R2={_fmt(evo_r2)}, "
            f"and interaction R2={_fmt(interaction_r2)}. Some evolutionary conditions beat the budget control, "
            "so any positive claim should be restricted to those task/model regimes."
        )
    return (
        "The configured model continuum does not show clean model-strength dominance, and replay/failure/compression "
        f"do not beat the budget-matched no-replay control. Pooled model-strength R2={_fmt(model_r2)}, "
        f"evolution-technique R2={_fmt(evo_r2)}, and interaction R2={_fmt(interaction_r2)}; the strongest conclusion is "
        "that apparent gains over single-shot mostly reflect search budget and task/model-specific interactions rather than robust replay-specific value."
    )


def _required_questions(
    summary: list[dict[str, Any]],
    effects_budget: list[dict[str, Any]],
    *,
    full_design_complete: bool,
) -> str:
    pooled = next((row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"), {})
    model_r2 = _fmt(pooled.get("model_strength_r2")) if full_design_complete else "requires full campaign"
    evo_r2 = _fmt(pooled.get("evolution_technique_r2")) if full_design_complete else "requires full campaign"
    interaction_r2 = _fmt(pooled.get("interaction_r2")) if full_design_complete else "requires full campaign"
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    by_tier: dict[str, int] = {}
    for row in positive_budget:
        by_tier[str(row["model_tier"])] = by_tier.get(str(row["model_tier"]), 0) + 1
    return "\n".join(
        [
            f"1. How much variance is explained by model strength? {model_r2 or 'insufficient data'}.",
            f"2. How much variance is explained by evolutionary technique? {evo_r2 or 'insufficient data'}.",
            f"3. Is there a model strength x technique interaction? {interaction_r2 or 'insufficient data'}.",
            f"4. Do replay/failure/compression techniques beat a budget-matched no-replay control? {len(positive_budget)} comparisons beat budget-matched no-replay with positive bootstrap support.",
            f"5. Are evolutionary gains larger for lower-scored models than higher-scored models? {by_tier if by_tier else 'insufficient or no positive budget-control gains'}.",
            f"6. Is the strongest conclusion model strength dominates, evolution adds independent value, or evolution only helps under certain task/model regimes? {_main_conclusion(summary, effects_budget, full_design_complete=full_design_complete)}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate model-strength x evolution-technique factorial outputs.")
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()
    run_root = Path(args.run_root)
    rows = _add_performance_z(_load_rows(run_root))
    if not rows:
        raise SystemExit(f"No run summaries found under {run_root}")
    _write_model_strength_table_if_missing(run_root, rows)
    write_csv_dicts(run_root / "all_runs_long.csv", rows, performance_columns())
    cell_means = _cell_means(rows)
    write_csv_dicts(
        run_root / "cell_means.csv",
        cell_means,
        [
            "task_family",
            "model_tier",
            "evolution_technique",
            "n_runs",
            "mean_performance_raw",
            "std_performance_raw",
            "sem_performance_raw",
            "ci95_low_performance_raw",
            "ci95_high_performance_raw",
            "mean_performance_z",
            "mean_novelty",
            "mean_runtime_ms",
            "mean_feasibility_rate",
            "mean_generation_success_rate",
            "mean_successful_generations",
            "mean_generation_error_count",
            "mean_repair_attempt_count",
            "mean_salvage_attempt_count",
            "mean_executable_candidate_count",
            "mean_fallback_generation_count",
            "mean_materialization_fallback_count",
            "mean_materialization_timeout_count",
            "mean_accepted_fallback_epochs",
            "mean_accepted_executable_epochs",
            "mean_acceptance_rate",
        ],
    )
    _write_matrices(rows, run_root)
    task_anova, pooled_anova, variance_summary = _variance_decomposition(rows, run_root)
    effects_single, effects_budget = _effect_sizes(rows, run_root)
    cvrp_metric_cells, cvrp_metric_effects = _cvrp_metric_decomposition(rows, run_root)
    tsp_saturation_rows, tsp_audit_rows = _tsp_diagnostics(rows, run_root)
    figure_dir = run_root / "figures"
    _write_barplot(
        [row for row in variance_summary if str(row["analysis_scope"]).startswith("pooled")],
        path=figure_dir / "pooled_variance_partition_barplot.png",
        title="Pooled variance partition",
        keys=["model_strength_r2", "evolution_technique_r2", "interaction_r2"],
    )
    _write_barplot(
        [row for row in variance_summary if not str(row["analysis_scope"]).startswith("pooled")],
        path=figure_dir / "task_specific_variance_partition_barplot.png",
        title="Task-specific variance partition",
        keys=["model_strength_r2", "evolution_technique_r2", "interaction_r2"],
    )
    _write_line_figures(rows, effects_budget, run_root)
    report = _final_report(
        rows,
        cell_means,
        variance_summary,
        effects_single,
        effects_budget,
        cvrp_metric_effects,
        tsp_saturation_rows,
        tsp_audit_rows,
        run_root,
    )
    (run_root / "final_report.md").write_text(report, encoding="utf-8")
    write_pdf_report(
        path=run_root / "final_report.pdf",
        run_name=run_root.name,
        markdown_report=report,
        suite_summary={},
        condition_payloads=[],
    )
    write_json(
        run_root / "aggregation_metadata.json",
        {
            "row_count": len(rows),
            "task_specific_anova_rows": len(task_anova),
            "pooled_anova_rows": len(pooled_anova),
            "effect_vs_single_rows": len(effects_single),
            "effect_vs_budget_rows": len(effects_budget),
            "cvrp_metric_cell_rows": len(cvrp_metric_cells),
            "cvrp_metric_effect_rows": len(cvrp_metric_effects),
            "tsp_saturation_rows": len(tsp_saturation_rows),
            "tsp_materialization_audit_rows": len(tsp_audit_rows),
        },
    )
    print(f"final_report.md: {run_root / 'final_report.md'}")
    print(f"all_runs_long.csv: {run_root / 'all_runs_long.csv'}")
    print(f"variance_partition_summary.csv: {run_root / 'variance_decomposition' / 'variance_partition_summary.csv'}")
    print(_main_conclusion(variance_summary, effects_budget, full_design_complete=_is_full_factorial(rows)))


if __name__ == "__main__":
    main()
