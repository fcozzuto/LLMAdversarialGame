# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260519_232457_c
- started_at_local: 2026-05-19 23:24:57
- finished_at_local: 2026-05-19 23:57:54
- duration_hhmm: 00:33
- duration_seconds: 1976.961
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.08803 | 0.0 | 0.056019 | 0.737297 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235667 | 0.054968 | 0.121542 | 0.903863 | 0.44 | False | 0.004908 | 0.172081 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.901066 | 0.44 | False | 0.006066 | 0.244254 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.054968 | 0.121317 | 0.820961 | 0.4425 | False | 0.003143 | -0.002078 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.888325 | 0.44 | False | 0.007131 | 0.718077 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.238386 | 0.064041 | 0.128273 | 0.893773 | 0.4425 | False | 0.001469 | 0.095546 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.08803`, family holdout `0.0`, combined `0.056019`.
- Accepted novelty `0.737297`, complexity `0.76`, and adaptation efficiency `0.052001`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.903863`, complexity `0.44`, and adaptation efficiency `0.059402`.
- Last-epoch runtime `60.9314` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.004908`, positive scaffolds `1`, Pareto runtime inflation `0.172081`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.149822, "gap_delta": 0.000224, "runtime_inflation": 0.172081, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.901066`, complexity `0.44`, and adaptation efficiency `0.007624`.
- Last-epoch runtime `160.58695` ms and distance evaluations `7185.75`.
- Validation: surviving `False`, transplant delta `0.006066`, positive scaffolds `1`, Pareto runtime inflation `0.244254`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.182993, "gap_delta": 0.000224, "runtime_inflation": 0.244254, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.820961`, complexity `0.4425`, and adaptation efficiency `0.006693`.
- Last-epoch runtime `74.8824` ms and distance evaluations `5058.75`.
- Validation: surviving `False`, transplant delta `0.003143`, positive scaffolds `0`, Pareto runtime inflation `-0.002078`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.002078, "same_gap_faster": true}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.888325`, complexity `0.44`, and adaptation efficiency `0.016341`.
- Last-epoch runtime `75.207525` ms and distance evaluations `4823.25`.
- Validation: surviving `False`, transplant delta `0.007131`, positive scaffolds `1`, Pareto runtime inflation `0.718077`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.866865, "gap_delta": -0.003304, "runtime_inflation": 0.718077, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.238386`, family holdout `0.064041`, combined `0.128273`.
- Accepted novelty `0.893773`, complexity `0.4425`, and adaptation efficiency `0.005533`.
- Last-epoch runtime `67.89985` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.001469`, positive scaffolds `1`, Pareto runtime inflation `0.095546`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006956, "runtime_inflation": 0.095546, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular Operator Discovery Suite - Conservative Interpretation

## Summary of Main Transfer Evidence (Held-out TSPLIB & Family Gap)
- Held-out TSPLIB gaps remain high (baseline ~0.235, operators ≥0.235, except slight variations).
- Family holdout gaps (~0.05 - 0.06) show no clear improvement beyond baseline.
- Transfer gaps in modular operators range from approx. 0.118 to 0.128, not clearly better than baseline (baseline transfer gap ~0.121).

## Operator Validation & Robustness
- No operator passes strict transplant or ablation checks convincingly:
  - Ablation: Disabling the operator often does not hurt performance, indicating weak or no real effect.
  - Transplant: Operators fail to transplant cleanly into critical scaffolds, e.g., `clustered_local_search`.
  - Family tests: No operator demonstrates consistent benefit on held-out families; no positive family gains notable except one restart controller family, but with tradeoffs.

## Detailed Notes on Key Operators

### Candidate Pruner (e.g., "candidate_pruner_transfer_balanced", "descriptor_adaptive_pruner_for_cluster_grid_trap")
- Core idea: Adaptive pruning of candidate moves based on instance descriptors.
- Held-out TSPLIB gaps ~0.235 (no improvement over baseline).
- Transplant mean gap delta positive (worsened gaps) ~0.0049-0.006.
- Ablation shows disabled variant slightly better (negative gap delta vs full), so no ablation support for operator usefulness.
- Runtime inflation high (~17% to 24% on Pareto).
- Conclusion: Fails transplant and ablation criteria; no surviving candidate.

### Perturbation Operator ("perturbation_double_bridge_escalating_2opt_escape_transfer")
- Core idea: Deterministic stagnation escape via structured perturbations.
- Family gap and held-out TSPLIB gap unchanged from baseline.
- Ablation variants equal to full operator; disabling does not hurt.
- Transplant shows no positive scaffold.
- Runtime slightly reduced but no benefit on transfer gap.
- Conclusion: No validation support; not a surviving candidate.

### Restart Controller ("instance_adaptive_restart_controller_two_cluster_escape")
- Core idea: Adaptive restarts triggered by instance features to escape traps.
- Shows some family benefit on "two_cluster_bottleneck_tsp" (gap -0.024).
- However, held-out TSPLIB gap unchanged (0.235).
- Ablation suggests disabling operator worsens gap by +0.0033, some weak ablation support.
- Runtime inflation is high (~0.72).
- Transplant mean gap delta +0.007, runtime increase notable.
- Conclusion: Limited family transfer gain but fails held-out TSPLIB improvement and transplant; fails surviving candidate criteria.

### Candidate Ranker ("rank_2opt_candidates_cluster_span_balanced")
- Core idea: Prioritizes local moves by score incorporating crossing and trap awareness.
- Family gap worsens (+0.064 gap), with severe regression on grid-like TSP.
- Ablation disabling operator reduces gap by -0.007, indicating operator hurts performance.
- Poor transplant results; no family-level improvement.
- Runtime inflation modest (~9.5%).
- Conclusion: Underperforms consistently; not surviving candidate.

### Full-Solver Evolution (baseline reference)
- Best transfer and TSPLIB gaps: 0.056 (transfer) and 0.088 (TSPLIB) in 'phase7_full_solver_evolution', but no modular operator candidate survives.
- No modular operator achieved better gaps than full-solver baseline.

## Pareto Tradeoff Assessment
- No operator yields Pareto improvements:
  - None achieves better gap at equal or lower runtime.
  - Most modular operators inflate runtime notably with no gap improvements.
  
## Overall Conclusion
- **No modular operator survives the strict transplant, ablation, family holdout, and held-out TSPLIB gap criteria to be considered interesting or reusable.**
- Weak or no operator effect indicated by ablation (disabling often does not harm or slightly improves).
- No operator demonstrates consistent improvements on held-out instance families, nor on TSPLIB benchmark.
- Some operators show minor family-level benefits at the cost of high runtime inflation and fail to transfer across scaffolds.
- Therefore, **no claims about reusable modular operator structure or algorithm discovery are justified.**
- The full-solver evolution baseline remains the best performing condition but is not modularized.

---

## Recommendations
- Focus further exploration on operators that:
  - Show consistent positive gap reductions on held-out TSPLIB and family holdouts.
  - Pass ablation checks with disabling clearly reducing performance.
  - Successfully transplant into multiple scaffolds without severe runtime or gap regressions.
- Investigate runtime inflation drivers to improve Pareto efficiency.
- Avoid claims of algorithm discovery until modular operator validation passes scaffold and family tests.

```
