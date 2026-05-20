# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260519_225244_b
- started_at_local: 2026-05-19 22:52:44
- finished_at_local: 2026-05-19 23:24:55
- duration_hhmm: 00:32
- duration_seconds: 1931.523
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.868026 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.90359 | 0.445 | False | 0.010863 | 0.719721 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.046321 | 0.115856 | 0.84925 | 0.445 | False | 0.00897 | 0.423769 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.049737 | 0.118013 | 0.870615 | 0.445 | False | 0.00837 | 0.677344 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.0 | 0.44 | False | 0.004297 | 1.374482 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.812304 | 0.44 | False | 0.003448 | 0.276204 |

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
- Accepted novelty `0.868026`, complexity `0.56`, and adaptation efficiency `-0.028692`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.90359`, complexity `0.445`, and adaptation efficiency `0.03612`.
- Last-epoch runtime `54.69495` ms and distance evaluations `4648.0`.
- Validation: surviving `False`, transplant delta `0.010863`, positive scaffolds `1`, Pareto runtime inflation `0.719721`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.844848, "gap_delta": -0.002615, "runtime_inflation": 0.719721, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.84925`, complexity `0.445`, and adaptation efficiency `0.008613`.
- Last-epoch runtime `54.953275` ms and distance evaluations `4451.25`.
- Validation: surviving `False`, transplant delta `0.00897`, positive scaffolds `1`, Pareto runtime inflation `0.423769`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.795701, "gap_delta": -0.005462, "runtime_inflation": 0.423769, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.049737`, combined `0.118013`.
- Accepted novelty `0.870615`, complexity `0.445`, and adaptation efficiency `0.006611`.
- Last-epoch runtime `55.457125` ms and distance evaluations `4816.25`.
- Validation: surviving `False`, transplant delta `0.00837`, positive scaffolds `1`, Pareto runtime inflation `0.677344`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.804735, "gap_delta": -0.005462, "runtime_inflation": 0.677344, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.0`, complexity `0.44`, and adaptation efficiency `0.0`.
- Last-epoch runtime `66.69595` ms and distance evaluations `4451.25`.
- Validation: surviving `False`, transplant delta `0.004297`, positive scaffolds `2`, Pareto runtime inflation `1.374482`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 1.609585, "gap_delta": -0.003363, "runtime_inflation": 1.374482, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.812304`, complexity `0.44`, and adaptation efficiency `0.014374`.
- Last-epoch runtime `82.2059` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003448`, positive scaffolds `1`, Pareto runtime inflation `0.276204`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.216542, "gap_delta": 0.000224, "runtime_inflation": 0.276204, "same_gap_faster": false}

## Judge Appendix
# Conservative Interpretation of TSP Modular-Operator Discovery Results

## Main Transfer Evidence (Held-out TSPLIB & Family Holdout Gaps)
- **Held-out TSPLIB Gap:** No improvement over baseline (all have gap delta = 0.0).
- **Family Holdout Gap:**
  - The modular operator conditions related to restart controllers (phase7_modular_operator_*) show modest family gap improvements (~ -0.004 to -0.007).
  - Families with positive signal: *clustered_tsp* and *two_cluster_bottleneck_tsp*.
  - No severe regressions observed in any operators.

## Validation via Transplant and Ablation Checks
- All modular restart controller operators fail clean transplantation into some scaffolds (`sparse_three_opt`, `clustered_local_search`).
- Transplant mean gap deltas for restart controllers are slightly positive (performance worsens) overall (~ +0.008 to +0.011), indicating limited transplant robustness.
- Ablation signals for restart controllers show small gap increases when disabled (~ +0.0026 to +0.0054), indicating some operator effect but weak.
- The candidate pruner operator:
  - Shows no improvement on held-out families or held-out TSPLIB.
  - Ablation indicates disabling does not degrade performance (gap delta slightly negative).
  - Does not transplant cleanly into `clustered_local_search`.

## Operator Complexity and Runtime Tradeoffs (Pareto)
- Restart controller operators have moderate complexity (~12 lines, score 0.44).
- Runtime inflation for restart controllers is high (0.42 to 1.37), with no better gap at same runtime.
- Candidate pruner exhibits low complexity with negligible gap improvement but also runtime inflation (~0.28).
- No operator shows Pareto improvements (better gap at same or less runtime).

## Claims on Reusable Operator Structure
- Restart controllers modify restart pressure using deterministic triggers under stagnation — a compact reusable mechanism.
- Candidate pruner adapts candidate list size based on instance descriptors, offering a potentially reusable neighborhood control.
- However, limited transplant success and weak ablation signals reduce confidence in robust reusable operator structure.

## Summary and Conclusion
| Operator (Condition Name)                         | Transfer Gap Delta | Family Gap Delta | Ablation Support | Transplant Success | Pareto Improvement | Surviving Candidate |
|-------------------------------------------------|-------------------|-----------------|------------------|--------------------|--------------------|---------------------|
| phase7_modular_operator_evolution                | -0.0055 approx.   | -0.0074 approx. | Weak (small gap increase if disabled) | Partial (fails some scaffolds) | None (runtime inflation) | No                  |
| phase7_modular_operator_random_replay            | -0.0055 approx.   | -0.0074 approx. | Weak              | Partial             | None               | No                  |
| phase7_modular_operator_diversity_residual_replay| -0.0045 approx.   | -0.0045 approx. | Weak              | Partial             | None               | No                  |
| phase7_modular_operator_compression_pressure      | -0.0035 approx.   | -0.0035 approx. | Weak              | Partial             | None (high runtime inflation) | No            |
| phase7_modular_operator_pareto_selection          | +0.00009          | Slight regression | No ablation signal | Partial             | None               | No                  |

- None of the modular operators survive all conditions (transplant, ablation, family transfer, held-out TSPLIB).
- The restart controller class shows some promise as a reusable component for clustered and bottleneck TSP families but fails transplant and Pareto criteria.
- No new algorithm discovery supported by the modular-operator approach due to failure in scaffold and family holdout tests.
- Full solver evolution (phase7_full_solver_evolution) achieves accepted epochs but no modular validated reusable operator extracted.

---

# Final Conservative Conclusion

- **No modular operator qualifies as a surviving reusable operator given transplant and ablation validation.**
- Restart controllers exhibit modest family transfer gains and weak ablation support but fail clean transplant and Pareto tradeoffs.
- Candidate pruner does not show meaningful transfer or ablation signal.
- Held-out TSPLIB gaps remain equal or worse than baseline for all operators, indicating no generalization to new problem sets.
- No modular operator discovery claim or reusable operator extraction can be made currently.
- The best evidence points to limited reusable restart pressure control potential within clustered TSP families, but this requires further development and stronger validation for practical use.
