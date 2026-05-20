# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_042327_l
- started_at_local: 2026-05-20 04:23:27
- finished_at_local: 2026-05-20 04:57:42
- duration_hhmm: 00:34
- duration_seconds: 2055.357
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.819776 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.895543 | 0.44 | False | 0.008978 | 0.669401 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.888046 | 0.44 | False | -0.000133 | 0.013898 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.236585 | 0.064041 | 0.12761 | 0.899613 | 0.445 | False | 0.002398 | 0.006216 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.892386 | 0.44 | False | 0.008043 | 0.684063 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.887354 | 0.4375 | False | 0.009335 | 0.355837 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.213387`, family holdout `0.064916`, combined `0.159398`.
- Accepted novelty `0.819776`, complexity `0.56`, and adaptation efficiency `-0.03038`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.895543`, complexity `0.44`, and adaptation efficiency `0.009694`.
- Last-epoch runtime `57.114525` ms and distance evaluations `4782.75`.
- Validation: surviving `False`, transplant delta `0.008978`, positive scaffolds `1`, Pareto runtime inflation `0.669401`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.767933, "gap_delta": -0.002615, "runtime_inflation": 0.669401, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.888046`, complexity `0.44`, and adaptation efficiency `0.006187`.
- Last-epoch runtime `67.78975` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.000133`, positive scaffolds `1`, Pareto runtime inflation `0.013898`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 11, "complexity_score": 0.42, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.013898, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.236585`, family holdout `0.064041`, combined `0.12761`.
- Accepted novelty `0.899613`, complexity `0.445`, and adaptation efficiency `0.003117`.
- Last-epoch runtime `96.743475` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.002398`, positive scaffolds `0`, Pareto runtime inflation `0.006216`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006293, "runtime_inflation": 0.006216, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.892386`, complexity `0.44`, and adaptation efficiency `0.016267`.
- Last-epoch runtime `245.747425` ms and distance evaluations `7156.75`.
- Validation: surviving `False`, transplant delta `0.008043`, positive scaffolds `1`, Pareto runtime inflation `0.684063`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.803776, "gap_delta": -0.003304, "runtime_inflation": 0.684063, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.887354`, complexity `0.4375`, and adaptation efficiency `0.013158`.
- Last-epoch runtime `75.819425` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.009335`, positive scaffolds `1`, Pareto runtime inflation `0.355837`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.278237, "gap_delta": 0.000224, "runtime_inflation": 0.355837, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Summary of Key Metrics and Focus

| Condition                                | Held-out TSPLIB Gap | Family Holdout Gap | Transplant Mean Gap Delta | Ablation Validation | Surviving Candidate | Operator Type        | Comments on Transfer / Reuse                  |
|-----------------------------------------|---------------------|-------------------|--------------------------|---------------------|---------------------|----------------------|-----------------------------------------------|
| phase7_baseline_heuristic_only          | 0.235058            | 0.054968          | 0.0                      | N/A                 | No                  | N/A                  | Baseline non-modular heuristic.               |
| phase7_full_solver_evolution             | **0.213387**        | 0.064916          | 0.0                      | N/A                 | No                  | N/A                  | Best TSPLIB gap overall but no modular operator identified or validated. |
| phase7_modular_operator_evolution        | 0.235058            | **0.046321**      | 0.008978                 | Yes (~0.0026 gap diff)    | No                  | Restart Controller   | Small family gap improvement. Transplant failed on key scaffolds (`sparse_three_opt`, `clustered_local_search`). Ablation shows minimal effect but confirms operator effect. Runtime inflation high (0.67x). |
| phase7_modular_operator_random_replay    | 0.235058            | 0.054968          | -0.000133                | No (ablation shows no effect)  | No                  | Acceptance           | No family improvement or transfer benefit. Ablation disables operator with zero effect. Non-robust operator. |
| phase7_modular_operator_diversity_residual_replay | 0.236585            | 0.064041          | 0.002398                 | No (ablation disables operator improves gap) | No                  | Candidate Ranker     | Family gap worsens significantly on `grid_like_tsp`. No positive family signals. Transplant failed in multiple scaffolds. Ablation does not confirm operator efficacy. |
| phase7_modular_operator_compression_pressure | 0.235058            | 0.050827          | 0.008043                 | Yes (~0.0033 gap diff)    | No                  | Restart Controller   | Similar operator to modular_operator_evolution condition. Provides small family gap improvement on `two_cluster_bottleneck_tsp`. Transplant issues and high runtime inflation (~0.68x). Operator validated by ablation but not surviving transplant. |
| phase7_modular_operator_pareto_selection | 0.235667            | 0.054968          | 0.009335                 | No (ablation no effect)   | No                  | Candidate Pruner     | No family-level improvement. Ablation indicates operator effect negligible or harmful. Runtime inflation moderately high (0.36x). Transplant mostly negative or neutral. |

---

## Conservative Interpretation & Prioritization

### Transfer Evidence (Held-out TSPLIB and Family Gaps)
- No modular operators improve held-out TSPLIB gap beyond baseline (best TSPLIB gap of 0.213387 comes from full solver evolution but no modular operator identified).
- Family holdout gap gains are marginal (~0.046–0.050 vs baseline ~0.054), only seen in two restart-controller operators (modular_operator_evolution, compression_pressure).

### Transplant & Ablation Validation
- Only restart-controller operators (phase7_modular_operator_evolution and compression_pressure) show positive ablation signals validating operator effect.
  - Ablation gap delta vs full operator ~0.0026 to 0.0033 (small but consistent).
- Neither restart-controller operator survives clean transplant tests cleanly:
  - Both fail in `sparse_three_opt` and `clustered_local_search`.
  - Transplant gap deltas positive (performance worsens or no improvement).
  - High runtime inflation (~0.67–0.68) severely limits practical reusability.
- Other operators (acceptance, candidate ranker, candidate pruner):
  - Fail ablation tests (disabling operator causes no harm or slight improvement).
  - Show no family-level or TSPLIB improvement.
  - Fail transplant validation or show neutral-to-negative transfer effects.
  - No surviving candidates.

### Pareto Tradeoffs
- Restart-controller operators cause notable runtime inflation (~66%–68%), suggesting poor efficiency tradeoff.
- Candidate pruner operator has moderate runtime inflation (~36%) but no robust benefit and failed ablation.
- No operator achieves better gap at same or faster runtime.

### Operator Reusability and Structure Claims
- Restart-controller operators embody a deterministic restart mechanism tuned for EUC2D TSP stagnation scenarios, enabling escapes from traps.
- However, these operators are insufficiently robust in diverse scaffolds and fail transplant conditions.
- Other operators do not convincingly surpass baseline or validate as modular reusable components.
- No operators meet surviving candidate threshold.

### Algorithm Discovery Claims
- No operator passes both the scaffold and family holdout tests to justify claiming algorithm discovery.
- Best modular candidates (restart controllers) show marginal benefits but poor transfer robustness and high runtime costs.

---

## Final Assessment

| Operator Name                                | Meets Key Criteria?                     | Comments                                                                                  |
|----------------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------|
| det_restart_controller_stagnation_balanced_euc2d (restart_controller) | **No** (fails transplant and family tests) | Validated by ablation; marginal family gains; fails transplant on multiple scaffolds; high runtime. |
| deterministic_restart_with_perturbation_escape (restart_controller)   | **No** (same as above)                 | Same profile as above; slight family improvement; runtime inflation; no survival.         |
| bounded_worse_threshold_acceptance_stagnation_bias (acceptance)       | **No** (fails ablation and transfer) | No ablation effect; no family gain; no transplant improvement.                           |
| candidate_ranker_bottleneck_grid_aware_reorder (candidate_ranker)     | **No** (negative family and no ablation) | Fails ablation; negative gap delta on grid_like family; no transplant success.            |
| candidate_pruning_bottleneck_cluster_safe (candidate_pruner)          | **No** (no ablation effect, no family gain) | Runtime inflation; no positive family or transplant signals.                              |

---

# Key Recommendations

- **No modular operator currently qualifies as a reusable, transportable component under transplant and family holdout tests.**
- The restart controller operators show some promise for modular restart mechanisms tuned for EUC2D stagnation but require improved transplant robustness and runtime efficiency.
- Future work should focus on reducing runtime inflation and validating operators across more scaffolds for reusable designs.
- Full solver evolution outperforms all modular operators in TSPLIB benchmarks but does not isolate reusable operator structures.
- Avoid claims of algorithm discovery until surviving candidate conditions are met (scaffold and family holdout validated).

---

# Summary

The suite's main transfer evidence lies in phase7_modular_operator_evolution (restart controller) and compression_pressure (restart controller) operators, both validated by ablation but failing robust transplant and family holdout tests, limiting claims to reusable modular operator structure. No modular operator improves held-out TSPLIB gap significantly nor survives transplant sufficiently to justify claiming algorithm discovery. The full-solver evolution condition performs best on TSPLIB but without modular operator discovery.

```
