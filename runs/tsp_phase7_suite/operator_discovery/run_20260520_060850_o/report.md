# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_060850_o
- started_at_local: 2026-05-20 06:08:50
- finished_at_local: 2026-05-20 06:42:59
- duration_hhmm: 00:34
- duration_seconds: 2049.033
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.091021 | 0.0 | 0.057922 | 0.859479 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235667 | 0.054968 | 0.121542 | 0.81601 | 0.445 | False | 0.00304 | 0.208165 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.046321 | 0.115856 | 0.857489 | 0.445 | False | 0.009939 | 0.707203 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.054968 | 0.121317 | 0.832569 | 0.4425 | False | 0.001236 | -0.013835 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.86711 | 0.4375 | False | 0.007161 | 1.104421 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.0 | 0.4375 | False | 0.009806 | 0.48603 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.091021`, family holdout `0.0`, combined `0.057922`.
- Accepted novelty `0.859479`, complexity `0.76`, and adaptation efficiency `0.053925`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.81601`, complexity `0.445`, and adaptation efficiency `0.009963`.
- Last-epoch runtime `45.883375` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00304`, positive scaffolds `1`, Pareto runtime inflation `0.208165`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.173945, "gap_delta": 0.000224, "runtime_inflation": 0.208165, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.857489`, complexity `0.445`, and adaptation efficiency `0.008531`.
- Last-epoch runtime `59.863475` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.009939`, positive scaffolds `1`, Pareto runtime inflation `0.707203`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.784605, "gap_delta": -0.005462, "runtime_inflation": 0.707203, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.832569`, complexity `0.4425`, and adaptation efficiency `0.004765`.
- Last-epoch runtime `67.611125` ms and distance evaluations `5165.75`.
- Validation: surviving `False`, transplant delta `0.001236`, positive scaffolds `0`, Pareto runtime inflation `-0.013835`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 11, "complexity_score": 0.42, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.013835, "same_gap_faster": true}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.86711`, complexity `0.4375`, and adaptation efficiency `0.016741`.
- Last-epoch runtime `43.6948` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.007161`, positive scaffolds `1`, Pareto runtime inflation `1.104421`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.865064, "gap_delta": -0.003304, "runtime_inflation": 1.104421, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.0`, complexity `0.4375`, and adaptation efficiency `0.0`.
- Last-epoch runtime `65.07795` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.009806`, positive scaffolds `1`, Pareto runtime inflation `0.48603`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.357171, "gap_delta": 0.000224, "runtime_inflation": 0.48603, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Key Evaluation Criteria Summary

| Criterion                   | Priority      | Evidence Source(s)                           |
|-----------------------------|---------------|---------------------------------------------|
| Held-out TSPLIB gap          | High          | `final_tsplib_gap` from modular conditions  |
| Family holdout gap           | High          | `final_family_gap` and `family_signal`       |
| Transplant validation        | High          | `transplant_mean_gap_delta`, `positive_scaffold_count`, `transplant_results` |
| Ablation validation          | High          | `ablation_results`, effect of disabling operator |
| Pareto tradeoffs             | Medium-High   | `pareto_gap_delta`, `pareto_runtime_inflation` |
| Surviving candidates status  | Critical      | `surviving_candidate` flag                   |
| Reusable operator structure | Preferred     | Operator reproducibility and validation across scaffolds/families |

---

## Overall Findings

### Baselines and Full Solver
- **Baseline heuristic (phase7_baseline_heuristic_only)**: Final TSPLIB gap is large (0.235058), family gap 0.054968.
- **Full solver evolution (phase7_full_solver_evolution)** improves transfer (0.0579) and TSPLIB gap (0.0910) strictly better than baseline.
- However, full solver conditions do not involve modular operators, yielding no reusable operator candidates.

---

### Modular Operators Overview

| Operator Name                           | Type              | Final TSPLIB Gap | Family Gap | Transfer Gap | Transplant Mean Gap Delta | Ablation Signal | Surviving Candidate | Comments                                   |
|---------------------------------------|-------------------|------------------|------------|--------------|---------------------------|-----------------|--------------------|--------------------------------------------|
| xfer_candidate_prune_by_trap_cluster_v1 | candidate_pruner  | 0.235667         | 0.054968   | 0.121542     | 0.00304                   | **No effect**   | False              | No improvement over host; disables harmless; high runtime inflation (~0.21) |
| det_restart_ctrl_twocluster_bottleneck_boost | restart_controller | 0.235058         | 0.046321   | 0.115856     | 0.009939                  | **No effect**   | False              | Gains on clustered/two-cluster families; no TSPLIB improvement; high runtime (~0.71) |
| restart_controller_two_cluster_safe   | restart_controller | 0.235058         | 0.050827   | 0.118702     | 0.007161                  | **No effect**   | False              | Helps "two_cluster_bottleneck_tsp" family slightly; no TSPLIB impact; highest runtime inflation (~1.1) |
| acceptance_bounded_worse_with_stagnation_safeguard | acceptance       | 0.235058         | 0.054968   | 0.121317     | 0.001236                  | **No effect**   | False              | No family or TSPLIB improvements; disables harmless; runtime slightly lower (-0.013) |
| pruner_cluster_bottleneck_adaptive    | candidate_pruner  | 0.235667         | 0.054968   | 0.121542     | 0.009806                  | **No effect**   | False              | Similar to other pruners; no family/TSPLIB gains; disables harmless; moderate runtime inflation (~0.49) |

---

### Key Observations

1. **Held-out TSPLIB Gap & Family Transfer**
   - None of the modular operators improve TSPLIB gaps relative to the baseline (about 0.235).
   - Family holdout gaps remain similar or worse; no clear family benefit except small gains on two-cluster and clustered family subsets by restart controllers.
  
2. **Transplant Validation**
   - All operators show small positive average transplant gap deltas (~0.001 to 0.01), indicating no consistent transferable improvement.
   - Positive scaffold counts are low (max 1), and some scaffolds show regressions.
   - Operators fail to transplant cleanly into some scaffolds (especially `clustered_local_search` and `sparse_three_opt`).

3. **Ablation Validation**
   - Disabling operators generally does **not degrade** performance.
   - Variant and disabled ablation gaps are nearly identical or even slightly better without the operator.
   - This indicates the discovered operators do not produce independent, measurable positive effect.

4. **Pareto Tradeoffs**
   - No operator moves clearly on the Pareto frontier improving gap at same runtime.
   - Runtime inflation is significant (up to 1.1x) with minimal or no gap improvement.
   - Some operators show slight negative gap deltas but at large runtime cost.

5. **Validation of Reusability and Survival**
   - None of the operators survive the transplant, ablation, scaffold, or family transfer tests.
   - No operators flagged as `surviving_candidate`.
   - Operators do not show reusable modular structure validated by ablation or transplant.

---

## Conservative Conclusions

- **No discovered modular operator passed key validations to be considered reusable or independently beneficial.**  
- The slight transfer or family gains on two-cluster or clustered TSP instances by restart-controller operators exist but do not generalize or improve held-out TSPLIB or survive ablation/transplant checks.
- Candidate pruners similarly fail ablation and transplant tests, indicating lack of real effect.
- High runtime inflation undermines practical utility of these operators.
- Full solver condition improves performance but does not yield modular reusable operators.
- **Hence, no modular-operator discovery or reusable operator structure can be credibly claimed from these results.**
- Narrative speculation unsupported; focus should remain on improving transfer and ablation validation criteria.

---

## Recommendation

- Continue refining modular discovery methods focusing on:
  - Ensuring ablation disables operator cause detectable performance drop.
  - Improving transfer to held-out families and TSPLIB datasets.
  - Achieving operator survival after transplant and family holdout.
  - Reducing runtime inflation to Pareto-beneficial levels.
- Given current results, do not promote any operator as reusable or as a discovered algorithm component.

---

# Summary

| Status                    | Result                         |
|---------------------------|--------------------------------|
| Modular operators found    | Yes, several candidates         |
| Survive transplant test   | No                             |
| Survive ablation test     | No                             |
| Improve held-out TSPLIB   | No                             |
| Improve family holdout    | Marginal/sparse, not robust    |
| Pareto runtime/gap trade  | Poor (runtime inflation high)  |
| Survive family holdout    | No clear survivors             |
| Declared discovered algos | None                          |
| Recommended action        | Further refinement needed      |
```
