# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260519_222129_a
- started_at_local: 2026-05-19 22:21:29
- finished_at_local: 2026-05-19 22:52:43
- duration_hhmm: 00:31
- duration_seconds: 1873.514
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.130772 | 0.003941 | 0.084652 | 0.862117 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.804218 | 0.445 | False | 0.008417 | 0.849429 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.881696 | 0.48 | False | 0.003487 | 0.010929 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.176662 | 0.056269 | 0.100624 | 0.0 | 0.4425 | False | -0.037302 | 1.442123 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.691789 | 0.44 | False | 0.007173 | 0.702383 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235871 | 0.069893 | 0.131043 | 0.811695 | 0.435 | False | 0.005155 | -0.126442 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.130772`, family holdout `0.003941`, combined `0.084652`.
- Accepted novelty `0.862117`, complexity `0.76`, and adaptation efficiency `0.009542`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.804218`, complexity `0.445`, and adaptation efficiency `0.009096`.
- Last-epoch runtime `50.5346` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.008417`, positive scaffolds `1`, Pareto runtime inflation `0.849429`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.766132, "gap_delta": -0.002615, "runtime_inflation": 0.849429, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.881696`, complexity `0.48`, and adaptation efficiency `0.006232`.
- Last-epoch runtime `56.145825` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003487`, positive scaffolds `0`, Pareto runtime inflation `0.010929`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.010929, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.176662`, family holdout `0.056269`, combined `0.100624`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `55.66275` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.037302`, positive scaffolds `4`, Pareto runtime inflation `1.442123`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 11.648842, "gap_delta": -0.019489, "runtime_inflation": 1.442123, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.691789`, complexity `0.44`, and adaptation efficiency `0.020983`.
- Last-epoch runtime `117.395575` ms and distance evaluations `7522.75`.
- Validation: surviving `False`, transplant delta `0.007173`, positive scaffolds `1`, Pareto runtime inflation `0.702383`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.788207, "gap_delta": -0.003304, "runtime_inflation": 0.702383, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235871`, family holdout `0.069893`, combined `0.131043`.
- Accepted novelty `0.811695`, complexity `0.435`, and adaptation efficiency `0.00268`.
- Last-epoch runtime `198.651025` ms and distance evaluations `7714.75`.
- Validation: surviving `False`, transplant delta `0.005155`, positive scaffolds `1`, Pareto runtime inflation `-0.126442`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": -0.01997, "gap_delta": 0.009726, "runtime_inflation": -0.126442, "same_gap_faster": false}

## Judge Appendix
# TSP Modular-Operator Discovery Suite Review

## Summary of Evaluation Criteria
- **Primary transfer evidence:** held-out TSPLIB gap and family holdout gap
- **Modular operator interest requires:** validation surviving transplant and ablation tests
- **Claims limited to:** reusable operator structure if modular conditions are met
- **Algorithm discovery claims require:** operator survival on scaffold and family holdouts

---

## Key Findings

### 1. Baseline Heuristic Only (phase7_baseline_heuristic_only)
- Heldout TSPLIB gap: 23.51%
- Family gap: 5.5%
- No modular operator, no novelty or survival expected.
- Not a candidate for modular operator claims.

### 2. Full Solver Evolution (phase7_full_solver_evolution)
- Final TSPLIB gap: 13.07%
- Family gap: 0.39%
- No modular operators extracted or validated.
- Does not provide reusable modular operator structure.

---

### 3. Modular Operator: `restart_escape_control_2opt_transfer`
- Operator type: *restart_controller*
- Validation:
  - Ablation shows mild gap differences (~0.0026), but disabling operator slightly increases gap → marginal ablation support.
  - Transplant yields **mean gap delta +0.0084**, indicating slight degradation on different scaffolds.
  - Only 1 scaffold shows positive transplant effect.
- Transfer and family gaps:
  - Family gap reduced by 2.7% on helpful families (clustered_tsp, two_cluster_bottleneck_tsp).
  - TSPLIB gap unchanged at 23.5%, no improvement on heldout TSPLIB family.
- Runtime inflation high (~0.85x)
- Complexity low (12 lines), compact restart controller mechanism.
- Failure to transplant cleanly to some scaffolds.
- Outcome: **Does not survive transplant and family holdouts sufficiently**, no surviving candidate.

### 4. Modular Operator: `det_escape_schedule_double_bridge_then_segment_reversal`
- Operator type: *perturbation*
- Validation:
  - Ablation shows no difference; disabling operator does not hurt performance.
  - No positive family gain; no improvement over baseline.
  - Transplant mean gap delta +0.0035 (slight degradation).
  - No scaffolds with positive transplant gain.
- TSPLIB and family gaps not improved.
- Runtime inflation negligible.
- Outcome: **No ablation or transplant validation**, not an interesting reusable operator.

### 5. Modular Operator: `scaffold_selector_structure_aware`
- Operator type: *scaffold_selector*
- Validation:
  - Ablation indicates disabling operator worsens gap by ~0.02, but best variant also shows regression.
  - Some positive family gains (heldout_tsplib, clustered_tsp, two_cluster_bottleneck_tsp).
  - Severe regressions in grid_like_tsp and uniform_euclidean families.
  - Transplant mean gap delta is negative (-0.037) indicating some positive transfer but with high runtime inflation (~1.44x).
  - Positive transplant gains in 4 scaffolds, but large runtime costs and inconsistent performance.
- Outcome: Although partially reusable, inconsistent family and transplant results mean **does not survive conservative criteria**.

### 6. Modular Operator: `transfer_restart_controller_bottleneck_escape_dense`
- Operator type: *restart_controller*
- Validation:
  - Ablation shows small gap increase (~0.0033) when disabled, indicating a mild effect.
  - Family gains limited to one family (two_cluster_bottleneck_tsp).
  - Transplant mean gap delta +0.0072 (degradation), only 1 positive scaffold.
  - Runtime inflation moderate (0.7x).
  - Does not transplant well to some scaffolds.
- Outcome: Moderate effect but **fails robust transfer and transplant survival**.

### 7. Modular Operator: `candidate_pruner_scale_by_structure_escape_bias`
- Operator type: *candidate_pruner*
- Validation:
  - Ablation results show disabling reduces gap (~0.01), indicating operator may hurt rather than help.
  - No family shows improvement; one family shows severe regression.
  - Transplant mean gap delta +0.005 (degradation), only one scaffold positive.
  - Runtime slightly reduced but performance worsens overall.
- Outcome: No ablation or transplant validation, **not reusable or beneficial**.

---

## Overall Conclusion

- **No modular operator survives transplant and ablation validation robustly enough to be considered reusable.**
- All modular operators fail to reduce held-out TSPLIB gap or family holdout gap in a consistent manner.
- Runtime overhead is significant for some operators with no gap improvements.
- Ablations frequently show operator disabling does not hurt or even improves results.
- Transplant results show mostly neutral or negative gap delta; only isolated positive scaffolds but with tradeoffs.
- Therefore, **no modular operator supports claims of reusable operator structure or algorithm discovery.**

---

## Recommendations

- Future work should focus on operators that:
  - Show significant improvement on heldout TSPLIB and family gaps.
  - Pass ablation checks with disabled variants increasing gap substantially.
  - Survive transplant tests on multiple scaffolds with neutral or positive gap deltas.
  - Maintain manageable runtime overhead and complexity.

---

## Summary Table for Quick Reference

| Operator                                  | Operator Type       | Heldout Family Gap Δ | Heldout TSPLIB Gap Δ | Ablation Support | Transplant Mean Gap Δ | Runtime Inflation | Survives Modular Validation? |
|-------------------------------------------|---------------------|---------------------|---------------------|------------------|----------------------|-------------------|-----------------------------|
| restart_escape_control_2opt_transfer       | restart_controller  | -0.0275             | 0.0                 | Marginal         | +0.0084              | 0.85x             | No                          |
| det_escape_schedule_double_bridge_then_segment_reversal | perturbation       | 0.0                 | 0.0                 | None             | +0.0035              | 0.01x             | No                          |
| scaffold_selector_structure_aware          | scaffold_selector    | -0.0072             | -0.0583             | Weak             | -0.0373              | 1.44x             | No                          |
| transfer_restart_controller_bottleneck_escape_dense | restart_controller  | -0.0035             | 0.0                 | Marginal         | +0.0072              | 0.7x              | No                          |
| candidate_pruner_scale_by_structure_escape_bias | candidate_pruner    | +0.0129             | +0.0008             | None (harmful)   | +0.0052              | 0.87x             | No                          |

---

# Final Summary

- **No evidence of reusable modular operator discovery.**
- **No modular operator survives scaffold and family transplant tests.**
- **No algorithm discovery supported.**
- Operators with mild positive family effects do not improve generalization or heldout TSPLIB gap.
- Operators fail ablation or transplant tests critical for claiming reusable modular structure.

---

*Review conducted with conservative interpretation and prioritization of transfer, transplant, ablation, and Pareto tradeoffs per instructions.*
