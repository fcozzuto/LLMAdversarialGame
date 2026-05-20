# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_031517_j
- started_at_local: 2026-05-20 03:15:17
- finished_at_local: 2026-05-20 03:49:33
- duration_hhmm: 00:34
- duration_seconds: 2056.59
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.103264 | 0.0 | 0.065713 | 0.716491 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.844713 | 0.4375 | False | 0.007439 | 2.139159 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.046321 | 0.115856 | 0.852418 | 0.435 | False | 0.009238 | 1.097128 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235667 | 0.054968 | 0.121542 | 0.82186 | 0.4425 | False | 0.006684 | 0.278041 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.0 | 0.4425 | False | 0.006074 | 0.992123 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.901027 | 0.4425 | False | 0.003694 | 0.010622 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.103264`, family holdout `0.0`, combined `0.065713`.
- Accepted novelty `0.716491`, complexity `0.76`, and adaptation efficiency `0.040923`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.844713`, complexity `0.4375`, and adaptation efficiency `0.006851`.
- Last-epoch runtime `104.224075` ms and distance evaluations `4766.75`.
- Validation: surviving `False`, transplant delta `0.007439`, positive scaffolds `1`, Pareto runtime inflation `2.139159`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 1.934645, "gap_delta": -0.002615, "runtime_inflation": 2.139159, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.852418`, complexity `0.435`, and adaptation efficiency `0.006789`.
- Last-epoch runtime `69.88625` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.009238`, positive scaffolds `1`, Pareto runtime inflation `1.097128`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.9834, "gap_delta": -0.005462, "runtime_inflation": 1.097128, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.82186`, complexity `0.4425`, and adaptation efficiency `0.009892`.
- Last-epoch runtime `45.361425` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.006684`, positive scaffolds `1`, Pareto runtime inflation `0.278041`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.237223, "gap_delta": 0.000224, "runtime_inflation": 0.278041, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `58.050125` ms and distance evaluations `3995.75`.
- Validation: surviving `False`, transplant delta `0.006074`, positive scaffolds `2`, Pareto runtime inflation `0.992123`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.928037, "gap_delta": -0.003304, "runtime_inflation": 0.992123, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.901027`, complexity `0.4425`, and adaptation efficiency `0.018295`.
- Last-epoch runtime `55.70865` ms and distance evaluations `4678.75`.
- Validation: surviving `False`, transplant delta `0.003694`, positive scaffolds `0`, Pareto runtime inflation `0.010622`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.010622, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Overview
- Main transfer evidence (held-out TSPLIB and family holdout gaps) show no improvement over baseline.
- No modular operator survives transplant or ablation validation to qualify as reusable.
- No operator meets scaffold and family holdout tests to claim algorithm discovery.
- Operators generally increase runtime inflation significantly.

---

## Key Conditions and Findings

### Baseline (phase7_baseline_heuristic_only)
- Held-out family gap: 5.50%
- Transfer gap: 12.13%
- TSPLIB gap: 23.51%
- No novel operators; serves as baseline.

---

### Full Solver Evolution (phase7_full_solver_evolution)
- Best condition for lowest held-out family gap (0%) and transfer gap (6.57%).
- No modular operator identified (no operator validation).
- No surviving candidates.

---

### Modular Operators Summary

| Operator Name                               | Type              | Family Gap  | Transfer Gap | TSPLIB Gap | Ablation Survival | Transplant Survival | Runtime Inflation | Comments                                                   |
|---------------------------------------------|-------------------|-------------|--------------|------------|-------------------|---------------------|-------------------|------------------------------------------------------------|
| det_restart_controller_two_cluster_aware_fast_growth | Restart Controller | 4.63%       | 11.59%       | 23.51%     | Pass (small gap delta on ablation: 0.0026) | Partial (1 positive scaffold, but no overall survival) | High (2.14x)        | Helps clustered and two-cluster bottleneck TSP families; fails clean transplant on some scaffolds; no survival overall. |
| restart_controller_adaptive_2opt_escape_v1 | Restart Controller | 4.63%       | 11.59%       | 23.51%     | Pass (small gap delta on ablation: 0.0055) | Partial (1 positive scaffold)                      | Moderate (1.10x)   | Similar to above, with slightly better runtime; no surviving candidate. |
| adaptive_candidate_pruner_transfer_robust  | Candidate Pruner   | 5.50%       | 12.15%       | 23.57%     | Negative ablation signal (disabling does not hurt) | Partial (1 positive scaffold)                      | Low (0.28x)        | No validation family improvement; ablation does not support effect.   |
| restart_controller_bounded_escape_escalate | Restart Controller | 5.08%       | 11.87%       | 23.51%     | Pass but small ablation gap (0.0033)          | Partial (2 positive scaffolds)                   | ~1.0x             | Transfer gap not improved; runtime roughly baseline; no survival.     |
| det_escape_double_bridge_then_segment_reversal_v2 | Perturbation       | 5.50%       | 12.13%       | 23.51%     | Ablation no effect (disabled gap delta 0.0)  | No positive transplant scaffolds                   | Near zero inflation  | No family or transfer improvement; not surviving or reusable.         |

---

## General Patterns
- Operators target restart control or perturbation for stagnation escape.
- Some operators improve on specific families (clustered, two-cluster bottleneck) by up to ~2.7% gap reduction but fail overall transfer gap improvement.
- Ablation tests mostly show no or minimal gap difference when operators are disabled or altered, indicating weak to no validated operator effect.
- Transplant tests reveal some positive scaffolds but also failures (no clean transplant) and mild to moderate runtime inflation.
- No candidates survive phase7 tests to be considered robust, reusable operators.
- Pareto tradeoffs generally unfavorable (runtime inflation >1 with marginal or no gap improvement).

---

## Conservative Interpretation and Recommendations

- **No modular operator exhibits validated reusable structure** under transplant and ablation conditions—no surviving candidate.
- **Held-out TSPLIB and family holdout gaps remain high (~23.5% and ~5%) with operators**, showing no confirmed transfer benefit.
- Operators improving some family cases do not generalize or survive transplant failures.
- Runtime inflation often exceeds acceptable limits, further undermining practical reuse.
- **No evidence supports claiming algorithm discovery.**
- Focus should remain on refining operator validation to improve transplant robustness and detect ablation signals before claiming reusable operators.
- Current operators provide insight into potential restart and perturbation mechanisms but lack demonstrated generality or performance transfer.

---

## Summary

| Metric                         | Best Baseline | Best Operator Candidate             | Conclusion                        |
|-------------------------------|---------------|-----------------------------------|---------------------------------|
| Held-out Family Gap            | 5.5%          | min 4.63% (restart controllers)   | Marginal local improvement      |
| Held-out Transfer Gap          | 12.1%         | min 11.59%                        | No meaningful transfer gain     |
| Held-out TSPLIB Gap            | 23.5%         | 23.5%                            | No TSPLIB improvement            |
| Ablation Effectiveness         | N/A           | Negligible or absent              | No validated operator effect    |
| Transplant Survival            | N/A           | Partial positive on few scaffolds | No consistent transplant success|
| Runtime Inflation (Pareto)     | 1.0x baseline | 1.1x - 2.1x                      | Unfavorable runtime tradeoffs   |
| Surviving Candidate            | No            | No                               | No modular algorithm discovery  |

**No operators meet the modular conditions required for claiming reusable structure or algorithm discovery.**

---

# Final Recommendation

Prioritize improving ablation and transplant robustness in future modular operator searches. Current candidates remain experimental with no validated transfer or generalization. Full-solver evolution condition yields best held-out gap but lacks modular structure definition. Focus on operators that can survive disabling and transplant tests before further claims.
```
