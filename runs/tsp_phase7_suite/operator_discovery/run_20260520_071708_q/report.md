# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_diversity_residual_replay`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_071708_q
- started_at_local: 2026-05-20 07:17:08
- finished_at_local: 2026-05-20 07:51:47
- duration_hhmm: 00:35
- duration_seconds: 2079.291
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.802078 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.236585 | 0.064041 | 0.12761 | 0.887686 | 0.4475 | False | 0.003318 | 0.00507 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.828977 | 0.435 | False | 0.004105 | 0.00874 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.049737 | 0.118013 | 0.819295 | 0.4425 | False | 0.00861 | 0.892423 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.889017 | 0.44 | False | 0.00784 | 0.911918 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.0 | 0.5175 | False | 0.006779 | 0.272308 |

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
- Accepted novelty `0.802078`, complexity `0.56`, and adaptation efficiency `-0.031051`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.236585`, family holdout `0.064041`, combined `0.12761`.
- Accepted novelty `0.887686`, complexity `0.4475`, and adaptation efficiency `0.002106`.
- Last-epoch runtime `76.976775` ms and distance evaluations `5024.25`.
- Validation: surviving `False`, transplant delta `0.003318`, positive scaffolds `0`, Pareto runtime inflation `0.00507`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006293, "runtime_inflation": 0.00507, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.828977`, complexity `0.435`, and adaptation efficiency `0.004785`.
- Last-epoch runtime `79.784925` ms and distance evaluations `5142.25`.
- Validation: surviving `False`, transplant delta `0.004105`, positive scaffolds `0`, Pareto runtime inflation `0.00874`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.00874, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.049737`, combined `0.118013`.
- Accepted novelty `0.819295`, complexity `0.4425`, and adaptation efficiency `0.009279`.
- Last-epoch runtime `74.78395` ms and distance evaluations `4683.0`.
- Validation: surviving `False`, transplant delta `0.00861`, positive scaffolds `1`, Pareto runtime inflation `0.892423`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.884148, "gap_delta": -0.005462, "runtime_inflation": 0.892423, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.889017`, complexity `0.44`, and adaptation efficiency `0.031794`.
- Last-epoch runtime `89.91765` ms and distance evaluations `4278.75`.
- Validation: surviving `False`, transplant delta `0.00784`, positive scaffolds `1`, Pareto runtime inflation `0.911918`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.929896, "gap_delta": -0.003304, "runtime_inflation": 0.911918, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.0`, complexity `0.5175`, and adaptation efficiency `0.0`.
- Last-epoch runtime `150.94045` ms and distance evaluations `7315.75`.
- Validation: surviving `False`, transplant delta `0.006779`, positive scaffolds `1`, Pareto runtime inflation `0.272308`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 16, "complexity_score": 0.52, "distance_eval_inflation": 0.19862, "gap_delta": 0.000224, "runtime_inflation": 0.272308, "same_gap_faster": false}

## Judge Appendix
### Summary of TSP Modular-Operator Discovery Results

---

#### Main Transfer Evidence (Held-Out TSPLIB & Family Gaps)

| Condition                                | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Transplant Mean Gap Delta | Family Signal (Mean Gap Delta) | Surviving Candidate? |
|----------------------------------------|-----------------|-----------------|--------------------|---------------------------|-------------------------------|---------------------|
| **Best TSPLIB:** phase7_full_solver_evolution | 0.213387        | 0.064916        | 0.159398           | 0.0                       | N/A                           | No                  |
| **Best Transfer:** phase7_modular_operator_diversity_residual_replay | 0.235058        | 0.049737        | 0.118013           | 0.00861                   | -0.004484 (improvement in some families) | No                  |
| phase7_modular_operator_evolution      | 0.236585        | 0.064041        | 0.12761            | 0.003318                  | +0.007995 (positive but no improvement families) | No                  |
| phase7_modular_operator_random_replay  | 0.235058        | 0.054968        | 0.121317           | 0.004105                  | 0.0                          | No                  |
| phase7_modular_operator_compression_pressure | 0.235058        | 0.050827        | 0.118702           | 0.00784                   | -0.00355 (small improvement in 1 family) | No                  |
| phase7_modular_operator_pareto_selection | 0.235667        | 0.054968        | 0.121542           | 0.006779                  | +8.7e-05 (negligible)         | No                  |
| phase7_baseline_heuristic_only          | 0.235058        | 0.054968        | 0.121317           | 0.0                       | N/A                           | No                  |

---

#### Operator Validation, Transplant, Ablation, and Pareto Tradeoffs Highlights

- **No operator survived transplant or ablation checks:**  
  - All modular operators fail to show a significant, consistent positive impact when disabled (ablation results show no significant degradation; disabling operators often unchanged or better gap).  
  - No operators are surviving candidates.

- **Transplant results:**  
  - None of the operators improve significantly when transplanted into other scaffolds (no positive scaffold counts except rare cases with negligible or negative family signals).  
  - Several operators fail to transplant cleanly into alternative solvers (notably `clustered_local_search`, `sparse_three_opt`).

- **Family Holdout Performance:**  
  - No operator shows consistent improvement over host baselines across validation families. Some show regressions on `grid_like_tsp` and no positive family gains in heldout TSPLIB.  
  - The restart controllers show some positive gains on "clustered_tsp" and "two_cluster_bottleneck_tsp" families but at high runtime inflation (near 90% increase).

- **Pareto tradeoffs:**  
  - Runtime inflation is generally non-negligible (up to ~0.9) often without corresponding gap improvements.  
  - No operator demonstrates a clear better-gap-at-same-runtime scenario.

- **Core Ideas and Novelty:**  
  - Operators implement interesting ideas: deterministic local ranking for move selection, stagnation escape via perturbations, adaptive restart control, and candidate pruning.  
  - However, these do not materialize into reusable, validated operators due to failure in ablation and transplant checks.

---

### Conservative Interpretation and Conclusions

- **Main Known Result:** The "phase7_full_solver_evolution" condition (non-modular) achieves the best TSPLIB gaps but offers no evidence of reusable modular operator structure.

- **Modular Operators:**  
  - None survive ablation or transplant validations meaning no modular operators have demonstrated generalizable, reusable impact on held-out or family holdout test sets.

- **Transfer Evidence:**  
  - Although some modular operator variants show small improvements in certain families (e.g., restart controllers on clustered/bottleneck instances), these improvements come at a significant runtime cost and fail ablation tests, undermining claims of operator effect.

- **Pareto Tradeoffs:**  
  - No operator distinctly improves Pareto frontier (better gap without runtime cost or faster runtime at same gap).

- **No Algorithm Discovery:**  
  - Since none survive scaffold or family transfer tests, no claim can be made about discovered modular algorithms or reusable operators.

---

### Recommendation

- **No modular operator can currently be deemed interesting or reusable** based on the given evidence.

- Future work should focus on improving operator validation rigor, considering operator impact on transfer families, ensuring positive ablation signals, successful transplants, and better runtime-gap tradeoffs before claiming discovery of reusable modular operators.

---

### Summary Table of Modular Operators (Key Validation Metrics)

| Operator Name                              | Type               | Final TSPLIB Gap | Family Gap | Transfer Gap | Ablation Effect | Transplant Effect | Runtime Inflation | Surviving Candidate? |
|-------------------------------------------|--------------------|------------------|------------|--------------|-----------------|-------------------|-------------------|---------------------|
| candidate_ranker_bottleneck_aware_2opt_moves | candidate_ranker   | 0.236585         | 0.064041   | 0.12761      | Disabling helps  | No positive scaffolds | ~0.5%             | No                  |
| perturb_escape_double_bridge_progressive  | perturbation        | 0.235058         | 0.054968   | 0.121317     | No effect       | No positive scaffolds | ~0.87%            | No                  |
| restart_controller_deterministic_perturb_restart_pool | restart_controller | 0.235058         | 0.049737   | 0.118013     | Disabling helps  | 1 positive scaffold (marginal) | ~89%              | No                  |
| descriptor_driven_restart_controller_stagnation_escape | restart_controller | 0.235058         | 0.050827   | 0.118702     | Disabling helps  | 1 positive scaffold (marginal) | ~91%              | No                  |
| structure_aware_pruner_midlimit            | candidate_pruner    | 0.235667         | 0.054968   | 0.121542     | Disabling helps  | 1 positive scaffold (marginal) | ~27%              | No                  |

---

# Final conservative conclusion:

**No modular operator in the suite can be claimed as reusable or algorithmically discovered under the current criteria focusing on held-out transfer gap, transplant, ablation validation, and Pareto tradeoffs.**
