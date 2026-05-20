# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_045743_m
- started_at_local: 2026-05-20 04:57:43
- finished_at_local: 2026-05-20 05:32:04
- duration_hhmm: 00:34
- duration_seconds: 2060.508
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.180847 | 0.0 | 0.115084 | 0.78157 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.865478 | 0.445 | False | 0.003002 | -0.000838 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.875576 | 0.4425 | False | 0.010654 | 0.610699 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.049737 | 0.118013 | 0.874239 | 0.4425 | False | 0.007732 | 0.623816 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.0 | 0.4425 | False | 0.00714 | 0.616565 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.795501 | 0.44 | False | 0.003293 | 0.197399 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.180847`, family holdout `0.0`, combined `0.115084`.
- Accepted novelty `0.78157`, complexity `0.76`, and adaptation efficiency `0.014874`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.865478`, complexity `0.445`, and adaptation efficiency `0.004584`.
- Last-epoch runtime `2071.520475` ms and distance evaluations `2755497.0`.
- Validation: surviving `False`, transplant delta `0.003002`, positive scaffolds `0`, Pareto runtime inflation `-0.000838`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.000838, "same_gap_faster": true}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.875576`, complexity `0.4425`, and adaptation efficiency `0.007846`.
- Last-epoch runtime `257.032825` ms and distance evaluations `10482.75`.
- Validation: surviving `False`, transplant delta `0.010654`, positive scaffolds `1`, Pareto runtime inflation `0.610699`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.433839, "gap_delta": 0.000224, "runtime_inflation": 0.610699, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.049737`, combined `0.118013`.
- Accepted novelty `0.874239`, complexity `0.4425`, and adaptation efficiency `0.017392`.
- Last-epoch runtime `59.9857` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.007732`, positive scaffolds `1`, Pareto runtime inflation `0.623816`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.763082, "gap_delta": -0.005462, "runtime_inflation": 0.623816, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `56.66135` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00714`, positive scaffolds `1`, Pareto runtime inflation `0.616565`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.763692, "gap_delta": -0.003304, "runtime_inflation": 0.616565, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.795501`, complexity `0.44`, and adaptation efficiency `0.014678`.
- Last-epoch runtime `91.2285` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003293`, positive scaffolds `1`, Pareto runtime inflation `0.197399`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.154905, "gap_delta": 0.000224, "runtime_inflation": 0.197399, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite - Conservative Interpretation

## Summary of Key Metrics to Prioritize
- **Held-out TSPLIB gap** and **family holdout gap** are main indicators of successful transfer.
- Modular operators must pass **transplant** and **ablation** checks to be considered reusable.
- No operator here survives scaffold transplant or family holdout validation clearly.
- No operator is marked as a surviving candidate, so **no algorithm discovery claimed**.

---

## Condition Analysis

### 1. Baseline (phase7_baseline_heuristic_only)
- Held-out TSPLIB gap: 0.235058
- Family gap: 0.054968
- Transfer gap: 0.121317
- No modular operator.
- Used as baseline reference.

### 2. Full Solver Evolution (phase7_full_solver_evolution)
- Held-out TSPLIB gap improved to 0.180847 (better than baseline)
- Family gap reduced to 0.0
- Transfer gap: 0.115084 (improvement)
- No modular operator components isolated (operator_type = "n/a").
- No surviving candidate.

### 3. Modular Operator: det_escape_doublebridge_escalation_perturbation
- Held-out TSPLIB gap: 0.235058 (no improvement over baseline)
- Family gaps: no gains; 0 positive families.
- Ablation: disabling the operator does **not** degrade performance (gap delta = 0).
- Transplant test showed no consistent improvement; fails on `clustered_local_search`.
- Runtime slightly improved or neutral.
- Not a surviving candidate.
- Conclusion: No evidence of reusable operator effect; operator fails transplant and ablation checks.

### 4. Modular Operator: candidate_prune_transfer_adaptive_local_trap_guard and candidate_prune_transfer_prone_to_clusters_and_grids (similar candidate pruner variants)
- Held-out TSPLIB gap unchanged or slightly worse (0.235667 vs baseline 0.235058).
- Family gap shows no positive families.
- Ablation: disabling operator does **not** hurt performance (negative or zero gap delta).
- Transplant: slight positive scaffold count but mean transplant gap delta positive (worse).
- Runtime inflation notable (~0.61 in worst cases).
- Conclusion: No confirmed reuse or positive operator effect; ablation and transplant checks fail.

### 5. Modular Operator: restart_controller_adaptive_2x_pool and det_restart_controller_two_cluster_bottleneck
- Family holdout gap shows some small improvements on bottleneck/clustered TSP families.
- Ablation: disabling operator **hurts** performance by about 0.005gap, indicating a modest operator effect.
- Transplant results: weak positive scaffold counts, but mean transplant gap delta positive (slightly worse).
- Runtime inflation high (~0.62).
- Does not transplant cleanly to some scaffolds.
- No surviving candidate status.
- Conclusion: borderline operator effect but fails robust transplant checks and shows runtime cost; no reliable reusable operator identified.

---

## Pareto Tradeoffs
- Pareto results for all modular operators show:
  - No major gap improvements over baseline.
  - Some operators slightly faster without gap improvements (e.g., det_escape_doublebridge_escalation_perturbation).
  - Others have significant runtime inflation without gap gains.
- No operator dominates on the Pareto front in gap/runtime tradeoff.

---

## Overall Conclusion

- **No modular operator passes transplant and ablation validation to confirm reusable operator effect.**
- Held-out TSPLIB and family gaps do not improve with modular operators relative to baseline or full solver condition.
- Ablation tests consistently show disabling the operators does not hurt or yields negligible impact.
- Transplant tests fail or show insignificant/negative improvement.
- No surviving candidates identified.
- **No modular operator discovery or reusable operator structure adoption is supported by the current results.**
- The full solver evolution shows performance gains but lacks modular operator isolation; no modular discovery claim can be made.

---

# Final recommendation:
- Continue refining modular operator designs to produce consistent family holdout gains and robust transplant survival.
- Prioritize operators that demonstrate genuine ablation sensitivity and transfer benefits before claiming reusable operator structures.
```
