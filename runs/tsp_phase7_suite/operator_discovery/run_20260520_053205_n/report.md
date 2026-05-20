# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_evolution`.
- Best held-out TSPLIB gap: `phase7_modular_operator_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_053205_n
- started_at_local: 2026-05-20 05:32:05
- finished_at_local: 2026-05-20 06:08:48
- duration_hhmm: 00:37
- duration_seconds: 2203.553
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.873692 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.166295 | 0.086074 | 0.115629 | 0.861447 | 0.445 | False | -0.047281 | 25.028343 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.870033 | 0.4475 | False | 0.008878 | 0.373594 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235667 | 0.054968 | 0.121542 | 0.866478 | 0.4425 | False | 0.002993 | 0.308456 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.866909 | 0.4425 | False | 0.005576 | 0.707399 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.238386 | 0.064041 | 0.128273 | 0.891554 | 0.44 | False | 0.002971 | 0.057948 |

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
- Accepted novelty `0.873692`, complexity `0.56`, and adaptation efficiency `-0.028505`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.166295`, family holdout `0.086074`, combined `0.115629`.
- Accepted novelty `0.861447`, complexity `0.445`, and adaptation efficiency `0.010209`.
- Last-epoch runtime `39.4934` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.047281`, positive scaffolds `4`, Pareto runtime inflation `25.028343`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 638.855145, "gap_delta": -0.003539, "runtime_inflation": 25.028343, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.870033`, complexity `0.4475`, and adaptation efficiency `0.007896`.
- Last-epoch runtime `198.866` ms and distance evaluations `6674.75`.
- Validation: surviving `False`, transplant delta `0.008878`, positive scaffolds `1`, Pareto runtime inflation `0.373594`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.260257, "gap_delta": 0.000224, "runtime_inflation": 0.373594, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.866478`, complexity `0.4425`, and adaptation efficiency `0.009382`.
- Last-epoch runtime `47.371` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.002993`, positive scaffolds `1`, Pareto runtime inflation `0.308456`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.231646, "gap_delta": 0.000224, "runtime_inflation": 0.308456, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.866909`, complexity `0.4425`, and adaptation efficiency `0.032378`.
- Last-epoch runtime `111.136625` ms and distance evaluations `5310.75`.
- Validation: surviving `False`, transplant delta `0.005576`, positive scaffolds `2`, Pareto runtime inflation `0.707399`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.770256, "gap_delta": -0.003304, "runtime_inflation": 0.707399, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.238386`, family holdout `0.064041`, combined `0.128273`.
- Accepted novelty `0.891554`, complexity `0.44`, and adaptation efficiency `0.005546`.
- Last-epoch runtime `49.0911` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.002971`, positive scaffolds `0`, Pareto runtime inflation `0.057948`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006956, "runtime_inflation": 0.057948, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Summary
- **Main transfer evidence** (held-out TSPLIB gap & family holdout gap) shows **no operator survived scaffold transplant or ablation validation**.
- No condition generated a **surviving candidate operator**.
- Baseline and full-solver conditions do not involve modular operators; modular operator conditions are critical for reusable operator claims.
- Pareto and transfer gaps favor the modular operator condition "phase7_modular_operator_evolution" but **survival criteria fail**.

---

## Held-Out TSPLIB & Family Holdout Gap Analysis

| Condition                         | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Surviving Candidate | Transplant Mean Gap Delta |
|----------------------------------|-----------------|------------------|--------------------|----------------------|---------------------------|
| Baseline heuristic only           | 0.235058        | 0.054968         | 0.121317           | No                   | 0.0                       |
| Full solver evolution             | 0.213387        | 0.064916         | 0.159398           | No                   | 0.0                       |
| Modular operator evolution        | **0.166295**    | 0.086074         | **0.115629**       | No                   | -0.047281                 |
| Modular operator random replay    | 0.235667        | 0.054968         | 0.121542           | No                   | 0.008878                  |
| Modular operator diversity replay | 0.235667        | 0.054968         | 0.121542           | No                   | 0.002993                  |
| Modular operator compression      | 0.235058        | 0.050827         | 0.118702           | No                   | 0.005576                  |
| Modular operator pareto selection | 0.238386        | 0.064041         | 0.128273           | No                   | 0.002971                  |

- The best modular operator condition ("phase7_modular_operator_evolution") reduces TSPLIB gap relative to baseline (0.166295 vs 0.235058), supporting some transfer.
- However, **final family gap and ablation indicate performance regressions on certain families**, notably:
  - Severe regressions on `nearest_neighbor_trap_tsp` (+0.3987 gap delta)
  - Regressions on `uniform_euclidean` (+0.013605 gap delta)
- Transplant results positive on 4 scaffolds but **fail on key scaffolds** (no clean transplant into `cheapest_insertion_2opt`).
- Runtime inflation is very high (25x), risking practicality.

---

## Ablation and Transplant Validation (Modular Operator Evolution)

- Full operator gap: 0.117778 average (family+transfer evaluation)
- Disabling or flattening selector variants increased gap by +0.0035, suggesting some operator signal.
- But shuffled selector variant slightly improves gap (-0.001): inconsistent ablation evidence.
- Transplant mean gap delta: -0.047281 (improvement), yet **some scaffold hosts show severe failure/not clean transplant**.

### Other operators (candidate pruners, restart controllers, rankers):
- All fail ablation (disabling does not hurt or improves)
- No validation family shows consistent improvement over host baseline.
- Transplant results show mostly neutral/slightly negative transplant gap deltas.
- No operator survives ablation/transplant tests or family diversity robustness.

---

## Pareto Tradeoffs and Complexity

- The only condition improving Pareto gap marginally (-0.0035) is "phase7_modular_operator_evolution".
- Runtime inflation is high for this operator (~25x), which is impractical despite gap gains.
- Other operators have tiny or negative Pareto gap effects with modest runtime inflation.
- Complexity scores are modest (~0.44-0.46), code length approx 12-13 lines - operators are simple, but improvements do not survive validation.
  
---

## Conservative Interpretation & Recommendations

1. **No modular operator meets survival criteria** across scaffold and family transplant tests.
2. Operators show limited or negative transfer robustness: severe regressions on known families and poor ablation signals.
3. The "phase7_modular_operator_evolution" scaffold selector is the closest to interesting due to some transfer gap improvements and positive transplant mean gap delta.
4. However, this operator fails:
   - Transplant into key scaffolds
   - Shows severe performance regressions in certain families
   - Exhibits high runtime inflation
5. Candidate pruners, restart controllers, and rankers fail both ablation and transplant validations; no reusable operator evidence.
6. Full-solver evolution yields worse TSPLIB gaps and no modular interpretability.

---

## Final Conclusion

- **No discovered modular operator is validated for transfer or demonstrated to be reusable under ablation and transplant conditions.**
- Claims about operator discovery or reusable operator structure are **not supported**.
- The baseline and full-solver conditions are inferior to modular operator evolution in TSPLIB gap, but the modular operator fails survival criteria.
- Further work should focus on:
  - Improving transplant robustness and reducing runtime inflation of promising scaffold selectors.
  - Strengthening ablation signals indicating operator necessity.
  - Expanding validation on hold-out families to avoid severe regressions.
  
---

# Summary Table for Operators (Modular Conditions)

| Operator Name                             | Transfer Gap Delta* | Ablation Supported? | Transplant Supported? | Survives Scaffold & Family Tests? | Runtime Inflation | Comments                                                                                  |
|------------------------------------------|--------------------|---------------------|----------------------|-----------------------------------|-------------------|-------------------------------------------------------------------------------------------|
| transfer_scaffold_mix_bottleneck_cluster_grid_safe (scaffold_selector) | -0.0473 (mean gap improved) | Weak (ablation inconsistent) | Partial (fails some scaffolds)    | No                                | High (25x)          | Best candidate but severe runtime cost, inconsistent ablation, and family regressions.    |
| tsp_pruner_transfer_biased_to_bottlenecks (candidate_pruner)           | +0.0089 (worsened)           | No                  | No                   | No                                | Moderate (0.37x)       | No improvement or survival signals, fails transplant and ablation, no positive families.  |
| candidate_pruner_instance_grid_cluster_adaptive_medium (candidate_pruner) | +0.0030 (worsened)           | No                  | No                   | No                                | Moderate (0.31x)       | Similar to above, no survival signal.                                                    |
| restart_controller_stagnation_escape_balanced (restart_controller)     | +0.0056 (worsened)           | No                  | Partial              | No                                | Moderate (0.7x)        | Some positive family transfer but no survival through ablation/transplant.                |
| rank_2opt_moves_bottleneck_escape_bias (candidate_ranker)              | +0.0030 (worsened)           | No                  | No                   | No                                | Low (~0.06x)           | No survival support, underperforms on key families, fails transplant.                     |

*Negative gap delta indicates improvement over baseline.

---

# Recommendation

- No operator is currently "interesting" by survival criteria.
- The "phase7_modular_operator_evolution" scaffold selector is a promising structure-to-scaffold mapping with limited transfer evidence but must be improved to survive validation and reduce runtime inflation before any claim of reusable operator structure.
- Do **not claim algorithm discovery or reusable modular operators** in this suite based on current data.
```
