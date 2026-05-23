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
    MODEL_TIERS,
    TASK_FAMILIES,
    TECHNIQUES,
    bootstrap_ci,
    mean_or_none,
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
                "mean_acceptance_rate": mean_or_none([safe_float(row.get("acceptance_rate"), 0.0) or 0.0 for row in group]),
            }
        )
    return output


def _write_matrices(rows: list[dict[str, Any]], run_root: Path) -> None:
    matrix_dir = run_root / "model_x_evolution_matrices"
    matrix_dir.mkdir(exist_ok=True)
    figure_dir = run_root / "figures"
    figure_dir.mkdir(exist_ok=True)
    for task in TASK_FAMILIES:
        task_rows = [row for row in rows if row["task_family"] == task]
        matrix_rows = []
        for tier in MODEL_TIERS:
            row_payload = {"model_tier": tier}
            for technique in TECHNIQUES:
                values = [
                    safe_float(row.get("performance_raw"))
                    for row in task_rows
                    if row["model_tier"] == tier and row["evolution_technique"] == technique
                ]
                values = [value for value in values if value is not None]
                row_payload[technique] = mean_or_none(values)
            matrix_rows.append(row_payload)
        path = matrix_dir / f"{_task_slug(task)}_model_x_evolution.csv"
        write_csv_dicts(path, matrix_rows, ["model_tier", *TECHNIQUES])
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
    cell_w = 150
    cell_h = 58
    left = 160
    top = 80
    width = left + (len(TECHNIQUES) * cell_w) + 40
    height = top + (len(matrix_rows) * cell_h) + 60
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), title, fill=(20, 20, 20), font=font)
    values = [
        safe_float(row.get(technique))
        for row in matrix_rows
        for technique in TECHNIQUES
        if safe_float(row.get(technique)) is not None
    ]
    low = min(values) if values else 0.0
    high = max(values) if values else 1.0
    span = high - low if high != low else 1.0
    for col, technique in enumerate(TECHNIQUES):
        draw.text((left + col * cell_w + 6, top - 24), technique.replace("_", "\n"), fill=(20, 20, 20), font=font)
    for row_index, row in enumerate(matrix_rows):
        y = top + row_index * cell_h
        draw.text((20, y + 18), str(row["model_tier"]), fill=(20, 20, 20), font=font)
        for col, technique in enumerate(TECHNIQUES):
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
    tech_levels = TECHNIQUES
    tech_base = "single_shot"
    tier_levels = MODEL_TIERS
    tier_base = "weak_model"
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
    for task in TASK_FAMILIES:
        task_rows = [row for row in rows if row["task_family"] == task]
        task_specific.extend(_anova(task_rows, categorical_model=False, pooled=False, label=f"{task}:continuous"))
        task_specific.extend(_anova(task_rows, categorical_model=True, pooled=False, label=f"{task}:categorical"))
    pooled = []
    pooled.extend(_anova(rows, categorical_model=False, pooled=True, label="pooled:continuous"))
    pooled.extend(_anova(rows, categorical_model=True, pooled=True, label="pooled:categorical"))
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
    for task in TASK_FAMILIES:
        for tier in MODEL_TIERS:
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
    image = Image.new("RGB", (1100, 620), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((20, 20), "Interaction plot by task (mean performance_z)", fill=(20, 20, 20), font=font)
    colors = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189)]
    for task_index, task in enumerate(TASK_FAMILIES):
        x0 = 70 + task_index * 340
        y0 = 90
        draw.text((x0, y0 - 24), task, fill=(20, 20, 20), font=font)
        draw.line((x0, y0 + 220, x0 + 260, y0 + 220), fill=(0, 0, 0))
        draw.line((x0, y0, x0, y0 + 220), fill=(0, 0, 0))
        for tech_index, technique in enumerate(TECHNIQUES):
            points = []
            for tier_index, tier in enumerate(MODEL_TIERS):
                value = means.get((task, tier, technique))
                if value is None:
                    continue
                x = x0 + 40 + tier_index * 80
                y = y0 + 110 - int(value * 45)
                points.append((x, y))
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=colors[tech_index])
            if len(points) >= 2:
                draw.line(points, fill=colors[tech_index], width=2)
        for tier_index, tier in enumerate(MODEL_TIERS):
            draw.text((x0 + 16 + tier_index * 80, y0 + 230), tier.replace("_model", ""), fill=(20, 20, 20), font=font)
    for tech_index, technique in enumerate(TECHNIQUES):
        draw.rectangle((750, 420 + tech_index * 24, 764, 434 + tech_index * 24), fill=colors[tech_index])
        draw.text((772, 418 + tech_index * 24), technique, fill=(20, 20, 20), font=font)
    image.save(path)


def _write_scaling_curves(rows: list[dict[str, Any]], path: Path) -> None:
    means = _mean_by(rows, ("benchmark_strength_score", "evolution_technique"))
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
    for tech_index, technique in enumerate(TECHNIQUES):
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
    run_root: Path,
) -> str:
    lines = [
        "# Model Strength Dominates but Does Not Fully Explain LLM Code Evolution Performance",
        "",
        "## Purpose",
        "",
        "This factorial analysis tests whether evolutionary code search adds performance above base model coding strength across simple games, symmetric TSP, and real-world CVRP.",
        "",
        "## Experimental design",
        "",
        f"Rows analyzed: {len(rows)}. Task families present: {', '.join(sorted({row['task_family'] for row in rows}))}.",
        "",
        "The planned full design is 3 model tiers x 5 techniques with 10 simple-game seeds and 20 TSP/CVRP seeds per cell. Partial or smoke outputs are marked by their row counts.",
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
        "CSV matrices are in `model_x_evolution_matrices/`; heatmaps are in `figures/`.",
        "",
        "## Variance decomposition",
        "",
        _variance_answer(variance_summary),
        "",
        "## Effect sizes relative to single-shot",
        "",
        _effect_answer(effects_single, "single-shot"),
        "",
        "## Effect sizes relative to budget-matched no-replay",
        "",
        _effect_answer(effects_budget, "budget-matched no-replay"),
        "",
        "## Cross-family interpretation",
        "",
        _interpretation(rows, variance_summary, effects_budget),
        "",
        "## Main conclusion",
        "",
        _main_conclusion(variance_summary, effects_budget),
        "",
        "## Limitations",
        "",
        "- Do not overclaim algorithmic discovery; this phase compares model strength and search technique, not novelty of discovered algorithms.",
        "- Replay/failure/compression should be claimed useful only when they beat `budget_matched_no_replay`, not merely when they beat `single_shot`.",
        "- Smoke runs validate schema only; scientific conclusions require the full paid campaign.",
        "- P-values use reduced-model OLS/ANOVA approximations implemented locally to avoid adding heavy statistics dependencies.",
        "",
        "## Required Questions",
        "",
        _required_questions(variance_summary, effects_budget),
        "",
        "## Artifact Paths",
        "",
        f"- `all_runs_long.csv`: `{run_root / 'all_runs_long.csv'}`",
        f"- `variance_partition_summary.csv`: `{run_root / 'variance_decomposition' / 'variance_partition_summary.csv'}`",
    ]
    return "\n".join(lines)


def _markdown_cell_table(rows: list[dict[str, Any]]) -> str:
    lines = ["| task | model | technique | n | mean performance_z | mean raw | mean novelty |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows[:40]:
        lines.append(
            f"| {row['task_family']} | {row['model_tier']} | {row['evolution_technique']} | {row['n_runs']} | "
            f"{_fmt(row.get('mean_performance_z'))} | {_fmt(row.get('mean_performance_raw'))} | {_fmt(row.get('mean_novelty'))} |"
        )
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    parsed = safe_float(value)
    return "" if parsed is None else f"{parsed:.4g}"


def _variance_answer(summary: list[dict[str, Any]]) -> str:
    pooled = [row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"]
    if not pooled:
        return "Insufficient data for pooled variance decomposition."
    row = pooled[0]
    if int(row.get("n") or 0) < 10:
        return "Insufficient data for a scientific pooled variance conclusion; this output validates the schema only."
    return (
        f"Pooled continuous model: model-strength R2={_fmt(row.get('model_strength_r2'))}, "
        f"evolution-technique R2={_fmt(row.get('evolution_technique_r2'))}, "
        f"interaction R2={_fmt(row.get('interaction_r2'))}, residual variance={_fmt(row.get('residual_variance'))}."
    )


def _effect_answer(effects: list[dict[str, Any]], label: str) -> str:
    beating = [row for row in effects if str(row.get("beats_reference")).lower() == "true"]
    return f"{len(beating)} comparisons have bootstrap CIs above zero relative to {label}."


def _interpretation(rows: list[dict[str, Any]], summary: list[dict[str, Any]], effects_budget: list[dict[str, Any]]) -> str:
    del rows
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    return (
        "The interpretation should focus on the budget control. "
        f"Replay/failure/compression techniques beat budget-matched no-replay in {len(positive_budget)} tested task/model comparisons with positive bootstrap support. "
        + _variance_answer(summary)
    )


def _main_conclusion(summary: list[dict[str, Any]], effects_budget: list[dict[str, Any]]) -> str:
    pooled = next((row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"), None)
    if pooled is None:
        return "Smoke data validate the schema, but the full paid campaign is required for the empirical conclusion."
    if int(pooled.get("n") or 0) < 10:
        return "Smoke or partial data validate the schema, but the full paid campaign is required for the empirical conclusion."
    model_r2 = float(pooled.get("model_strength_r2") or 0.0)
    evo_r2 = float(pooled.get("evolution_technique_r2") or 0.0)
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    if model_r2 > evo_r2 and positive_budget:
        return "Model strength explains the largest share of variance, while evolutionary technique adds task/model-dependent value beyond budget-matched search."
    if model_r2 > evo_r2:
        return "Model strength dominates, and replay/failure/compression do not yet show reliable value beyond budget-matched search."
    return "Evolutionary technique explains variance comparable to or larger than model strength in the current data; inspect task-specific interactions before making a broad claim."


def _required_questions(summary: list[dict[str, Any]], effects_budget: list[dict[str, Any]]) -> str:
    pooled = next((row for row in summary if str(row["analysis_scope"]) == "pooled:continuous"), {})
    model_r2 = _fmt(pooled.get("model_strength_r2"))
    evo_r2 = _fmt(pooled.get("evolution_technique_r2"))
    interaction_r2 = _fmt(pooled.get("interaction_r2"))
    positive_budget = [row for row in effects_budget if str(row.get("beats_reference")).lower() == "true"]
    by_tier: dict[str, int] = {}
    for row in positive_budget:
        by_tier[str(row["model_tier"])] = by_tier.get(str(row["model_tier"]), 0) + 1
    return "\n".join(
        [
            f"1. Model strength variance explained: {model_r2 or 'insufficient data'}.",
            f"2. Evolutionary technique variance explained: {evo_r2 or 'insufficient data'}.",
            f"3. Model strength x technique interaction: {interaction_r2 or 'insufficient data'}.",
            f"4. Budget-control wins: {len(positive_budget)} replay/failure/compression comparisons beat budget-matched no-replay with positive bootstrap support.",
            f"5. Weak-vs-strong gain pattern: {by_tier if by_tier else 'insufficient or no positive budget-control gains'}.",
            f"6. Strongest conclusion: {_main_conclusion(summary, effects_budget)}",
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
            "mean_acceptance_rate",
        ],
    )
    _write_matrices(rows, run_root)
    task_anova, pooled_anova, variance_summary = _variance_decomposition(rows, run_root)
    effects_single, effects_budget = _effect_sizes(rows, run_root)
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
    report = _final_report(rows, cell_means, variance_summary, effects_single, effects_budget, run_root)
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
        },
    )
    print(f"final_report.md: {run_root / 'final_report.md'}")
    print(f"all_runs_long.csv: {run_root / 'all_runs_long.csv'}")
    print(f"variance_partition_summary.csv: {run_root / 'variance_decomposition' / 'variance_partition_summary.csv'}")
    print(_main_conclusion(variance_summary, effects_budget))


if __name__ == "__main__":
    main()
