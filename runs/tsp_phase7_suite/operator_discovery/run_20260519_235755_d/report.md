# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260519_235755_d
- started_at_local: 2026-05-19 23:57:55
- finished_at_local: 2026-05-20 00:30:07
- duration_hhmm: 00:32
- duration_seconds: 1932.106
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.086786 | 0.0 | 0.055227 | 0.806609 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.811502 | 0.4375 | False | 0.003917 | 0.004207 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.915929 | 0.445 | False | 0.010836 | 0.566615 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.054968 | 0.121317 | 0.803432 | 0.4425 | False | 0.003643 | 0.00337 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235667 | 0.054968 | 0.121542 | 0.901072 | 0.435 | False | 0.004143 | 0.263013 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.840152 | 0.44 | False | 0.001958 | 0.015417 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.086786`, family holdout `0.0`, combined `0.055227`.
- Accepted novelty `0.806609`, complexity `0.76`, and adaptation efficiency `0.040944`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.811502`, complexity `0.4375`, and adaptation efficiency `0.007333`.
- Last-epoch runtime `79.794325` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003917`, positive scaffolds `0`, Pareto runtime inflation `0.004207`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.004207, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.915929`, complexity `0.445`, and adaptation efficiency `0.000476`.
- Last-epoch runtime `65.7419` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.010836`, positive scaffolds `1`, Pareto runtime inflation `0.566615`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.388628, "gap_delta": 0.000224, "runtime_inflation": 0.566615, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.803432`, complexity `0.4425`, and adaptation efficiency `0.007406`.
- Last-epoch runtime `97.795575` ms and distance evaluations `4385.75`.
- Validation: surviving `False`, transplant delta `0.003643`, positive scaffolds `0`, Pareto runtime inflation `0.00337`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.00337, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.901072`, complexity `0.435`, and adaptation efficiency `0.059586`.
- Last-epoch runtime `164.845125` ms and distance evaluations `7380.75`.
- Validation: surviving `False`, transplant delta `0.004143`, positive scaffolds `1`, Pareto runtime inflation `0.263013`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.184271, "gap_delta": 0.000224, "runtime_inflation": 0.263013, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.840152`, complexity `0.44`, and adaptation efficiency `0.014165`.
- Last-epoch runtime `158.145275` ms and distance evaluations `7668.75`.
- Validation: surviving `False`, transplant delta `0.001958`, positive scaffolds `1`, Pareto runtime inflation `0.015417`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.015417, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Summary of Conditions

- **Best condition for TSPLIB and transfer:** `phase7_full_solver_evolution`
- **Total conditions:** 7
- **No surviving candidates** under any condition
- **Key metrics consistently show:**
  - No held-out TSPLIB gap improvement (gap reductions = 0)
  - No family holdout gap improvement (gap deltas = 0)
  - Ablation tests indicate disabling or altering operators causes **no degradation**
  - Transplant checks mostly show **no positive gap delta**, sometimes even minor regressions
  - Pareto tradeoffs show no gap improvement at the same or similar runtimes
  - High runtime inflation for candidate pruner operators without meaningful gains
  - No positive family-specific signals; no operators improve any family consistently

---

## Detailed Interpretation

### 1. Held-Out TSPLIB and Family Holdout Gaps

- All reported operators (perturbation and candidate pruner types) show **zero or no meaningful reduction** in held-out TSPLIB gap (~0.235 baseline).
- Family holdout gaps show no improvement (best family gain = 0), indicating no generalization or transfer benefits.
- Hence, no operator demonstrates effective transfer or family holdout generalization.

### 2. Transplant and Ablation Checks

- Ablation tests for all modular operators show disabling or simplifying operators **does not increase gap**, implying the operators do not contribute positively.
- Transplant mean gap deltas cluster around zero or small positive values (gap degradation), except some are slightly positive but insignificant.
- The failure to transplant cleanly into alternative scaffolds (notably `clustered_local_search`) is consistent across operators.
- Runtime increases significantly with candidate pruner operators, but without gap improvement.
- Therefore, no operator survives the transplant or ablation validation criteria for meaningful modularity and reusability.

### 3. Pareto and Runtime Tradeoffs

- Pareto results show **no better gap at equal or lower runtime** for any modular operator.
- Runtime inflation can be up to ~0.56x (large) for pruning operators without improvement in solution quality.
- No operator shows speedup at equal gap.
- No operators improve the Pareto frontier meaningfully.

### 4. Operator Core Ideas and Reusability

- Operators target stagnation escape via deterministic perturbation schedules or candidate pruning adapting to instance descriptors.
- Despite reasonable conceptual ideas, consistent failure in validation implies **no reusable operator structure identified**.
- No operator can be claimed as discovered or reusable modular operator according to validation rules.

---

## Conclusion

- **No operators survived** transplant, ablation, held-out gap, or family holdout gap validations.
- The **full solver evolution baseline** condition yields the best TSPLIB and transfer gaps, but is non-modular and cannot be claimed as a reusable operator.
- Modular operators, both perturbations and candidate pruners, show no validated effect on held-out generalization or family transfer.
- No claims about reusable operator structure or algorithm discovery are supported.
- Runtime inflation and transplant failures further weaken the practical value of proposed operators.
  
**Recommendation:** Focus future work on stronger validation designs improving candidate operator transfer and ablation signals, especially on held-out TSPLIB and family holdouts.

---

## Key Metrics Summary Table (selected)

| Condition                             | Type             | Final TSPLIB Gap | Final Family Gap | Transplant Mean Gap Delta | Ablation Signal (disabled Δgap) | Surviving Candidate | Runtime Inflation |
|-------------------------------------|------------------|------------------|------------------|---------------------------|----------------------------------|---------------------|-------------------|
| phase7_baseline_heuristic_only      | Baseline         | 0.235058         | 0.054968         | 0.0                       | N/A                              | No                  | 0.0               |
| phase7_full_solver_evolution        | Full solver      | **0.086786**     | 0.0              | 0.0                       | N/A                              | No                  | 0.0               |
| phase7_modular_operator_evolution   | Perturbation     | 0.235058         | 0.054968         | 0.0039                    | 0.0 (no hurt)                    | No                  | ~0.0042           |
| phase7_modular_operator_random_replay | Candidate Pruner | 0.235667         | 0.054968         | 0.0108                    | -0.0002 (disabled slightly better) | No              | 0.57              |
| phase7_modular_operator_diversity_residual_replay | Perturbation | 0.235058  | 0.054968         | 0.0036                    | 0.0 (no hurt)                    | No                  | 0.0034            |
| phase7_modular_operator_compression_pressure | Candidate Pruner | 0.235667       | 0.054968         | 0.0041                    | -0.0002 (disabled slightly better) | No              | 0.26              |
| phase7_modular_operator_pareto_selection | Perturbation | 0.235058         | 0.054968         | 0.0020                    | 0.0 (no hurt)                    | No                  | 0.015             |

---

# Final Verdict

- **No validated modular operator was found.**
- The best transfer and TSPLIB gaps come from a full solver evolution non-modular approach with no positive modular operator transplant.
- Candidate pruning and perturbation modular operators fail ablation and transplant tests and show no transfer improvement.
- **No claims of algorithm discovery or reusable operator structure are supported by the data.**
```
