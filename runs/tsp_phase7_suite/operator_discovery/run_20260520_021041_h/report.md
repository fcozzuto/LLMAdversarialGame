# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_compression_pressure`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_021041_h
- started_at_local: 2026-05-20 02:10:41
- finished_at_local: 2026-05-20 02:41:58
- duration_hhmm: 00:31
- duration_seconds: 1876.298
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.845032 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.238552 | 0.065041 | 0.128966 | 0.0 | 0.445 | False | 0.024412 | 0.894435 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.785756 | 0.44 | False | 0.004184 | -4.3e-05 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.054968 | 0.121317 | 0.908703 | 0.44 | False | 0.003509 | 0.005081 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.796782 | 0.44 | False | 0.008919 | 0.977422 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.855895 | 0.4375 | False | 0.001654 | -0.001558 |

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
- Accepted novelty `0.845032`, complexity `0.56`, and adaptation efficiency `-0.029472`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.238552`, family holdout `0.065041`, combined `0.128966`.
- Accepted novelty `0.0`, complexity `0.445`, and adaptation efficiency `0.0`.
- Last-epoch runtime `157.06945` ms and distance evaluations `6899.75`.
- Validation: surviving `False`, transplant delta `0.024412`, positive scaffolds `1`, Pareto runtime inflation `0.894435`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 1.541079, "gap_delta": 0.004671, "runtime_inflation": 0.894435, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.785756`, complexity `0.44`, and adaptation efficiency `0.007573`.
- Last-epoch runtime `77.9611` ms and distance evaluations `4863.0`.
- Validation: surviving `False`, transplant delta `0.004184`, positive scaffolds `0`, Pareto runtime inflation `-4.3e-05`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -4.3e-05, "same_gap_faster": true}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.908703`, complexity `0.44`, and adaptation efficiency `0.006548`.
- Last-epoch runtime `296.338925` ms and distance evaluations `10000.75`.
- Validation: surviving `False`, transplant delta `0.003509`, positive scaffolds `0`, Pareto runtime inflation `0.005081`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.005081, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.796782`, complexity `0.44`, and adaptation efficiency `0.018218`.
- Last-epoch runtime `72.066475` ms and distance evaluations `4475.5`.
- Validation: surviving `False`, transplant delta `0.008919`, positive scaffolds `1`, Pareto runtime inflation `0.977422`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.97364, "gap_delta": -0.003304, "runtime_inflation": 0.977422, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.855895`, complexity `0.4375`, and adaptation efficiency `0.013905`.
- Last-epoch runtime `187.374425` ms and distance evaluations `7429.75`.
- Validation: surviving `False`, transplant delta `0.001654`, positive scaffolds `0`, Pareto runtime inflation `-0.001558`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 11, "complexity_score": 0.42, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.001558, "same_gap_faster": true}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Key Evaluation Metrics (prioritized)
- **Held-out TSPLIB Gap** (transfer test)
- **Family Holdout Gap**
- **Operator Survival through Transplant & Ablation**
- **Evidence of Reusable Operator Structure**
- **Pareto Tradeoffs (gap vs runtime)**

---

## Overview of Conditions

| Condition Name                            | Transfer Gap | TSPLIB Gap | Family Gap | Transplant Mean Gap Delta | Ablation Support | Surviving Candidate | Operator Type          | Comments Summary                          |
|-----------------------------------------|--------------|------------|------------|--------------------------|-----------------|---------------------|-----------------------|-------------------------------------------|
| phase7_baseline_heuristic_only           | 0.1213       | 0.2351     | 0.0550     | 0.0000                   | N/A             | No                  | n/a                   | Baseline heuristic                       |
| phase7_full_solver_evolution              | 0.1594       | 0.2134     | 0.0649     | 0.0000                   | N/A             | No                  | n/a                   | Full solver evolution, no operator survival |
| phase7_modular_operator_evolution         | 0.1290       | 0.2386     | 0.0650     | 0.0244                   | No              | No                  | scaffold_selector      | Some family gain but negative ablation; no transplant survival |
| phase7_modular_operator_random_replay     | 0.1213       | 0.2351     | 0.0550     | 0.0042                   | No              | No                  | perturbation           | No family gain, no ablation effect, no transplant survival |
| phase7_modular_operator_diversity_residual_replay | 0.1213   | 0.2351     | 0.0550     | 0.0035                   | No              | No                  | perturbation           | Same as random_replay                     |
| **phase7_modular_operator_compression_pressure** | 0.1187 | 0.2351     | 0.0508     | 0.0089                   | No              | No                  | restart_controller     | Some family help but no transplant survival; ablation does not confirm effect |
| phase7_modular_operator_pareto_selection  | 0.1213       | 0.2351     | 0.0550     | 0.0017                   | No              | No                  | acceptance             | No family gain, no ablation effect, no transplant survival |

---

## Interpretation and Priority Analysis

### 1. **Held-Out TSPLIB Gap & Family Holdout Gap**
- None of the modular operators outperform baseline on held-out TSPLIB gap (transfer gap ≥ baseline 0.1213).
- Family holdout gap improvements are negligible or negative except for slight gain by "phase7_modular_operator_evolution" (+0.0650 vs baseline 0.0550) but this is not validated by transplant.

### 2. **Transplant Results**
- All modular operators fail clear transplant advantage:
  - Mean transplant gap deltas are positive or near zero (worsening or no improvement).
  - Most report "Does not transplant cleanly" failures.
  - The best transplant positive scaffold counts are 0 or 1 with associated gap increases.

### 3. **Ablation Checks**
- For all modular operators, disabling the operator does **not hurt** performance (ablation gap delta ≤ 0).
- No ablation variant shows a meaningful improvement or operator necessity.
- This suggests no real, robust operator effect in modular components.

### 4. **Pareto Analysis**
- No operator improves gap without severe runtime inflation.
- The best compression_pressure operator has runtime inflation ~0.98 and minimal gap reduction.
- Others show zero or negative gap deltas with no runtime advantage.

### 5. **Operator Survival**
- None of the modular operators survive as candidates under transplant and ablation criteria.
- No evidence supports reusable operator structure surviving scaffold and family tests.
- Therefore, no claim for operator discovery or general reusable structure is warranted.

---

## Conclusions

- **No modular operator passes the transplant and ablation robustness criteria.**
- **Held-out TSPLIB and family holdout gaps do not show consistent improvement from any operator.**
- **No operator demonstrates robust reusable structure; perturbation, acceptance, or restart operators do not survive validation.**
- **Given runtime inflation and lack of ablation support, operators fail to justify claim beyond baseline heuristics or full solver.**
- **Hence, no algorithm discovery or reusable operator claim is supported by data.**

---

## Notable Observations

- The **"phase7_modular_operator_compression_pressure"** condition shows marginal family holdout gain in "two_cluster_bottleneck_tsp" (-0.024425 gap delta), but this does not transfer or survive transplant.
- Scaffold selector operator ("phase7_modular_operator_evolution") shows some family gain on "grid_like_tsp" but suffers from worse performance on held-out families and no ablation benefit.
- The baseline heuristic and full solver evolution conditions have higher training gaps but do not produce reusable operators.

---

# Summary

No modular operator candidate demonstrates robust evidence of reusable operator structure or transfer performance improvements. The held-out TSPLIB and family results, combined with transplant and ablation checks, indicate failure to discover effective modular operators in this suite. Full-solver evolution maintains better gaps but does not yield reusable modular components. Focus should remain on improving operator validation and transplant success before asserting discovery claims.
