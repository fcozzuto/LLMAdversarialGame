# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_diversity_residual_replay`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_034934_k
- started_at_local: 2026-05-20 03:49:34
- finished_at_local: 2026-05-20 04:23:26
- duration_hhmm: 00:34
- duration_seconds: 2031.168
- seed_offset: 10000
- replicate_label: k
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.903377 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235667 | 0.054968 | 0.121542 | 0.836758 | 0.4475 | False | 0.004357 | 0.330053 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.802005 | 0.4425 | False | 0.006979 | 0.336717 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.049643 | 0.117954 | 0.7365 | 0.4425 | False | 0.00524 | 1.51959 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.250653 | 0.068862 | 0.135838 | 0.0 | 0.4425 | False | 0.037997 | 0.682188 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.854962 | 0.4375 | False | 0.003506 | 0.003318 |

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
- Accepted novelty `0.903377`, complexity `0.56`, and adaptation efficiency `-0.027569`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.836758`, complexity `0.4475`, and adaptation efficiency `0.009715`.
- Last-epoch runtime `42.410475` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.004357`, positive scaffolds `1`, Pareto runtime inflation `0.330053`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.235437, "gap_delta": 0.000224, "runtime_inflation": 0.330053, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.802005`, complexity `0.4425`, and adaptation efficiency `0.007279`.
- Last-epoch runtime `73.323625` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.006979`, positive scaffolds `1`, Pareto runtime inflation `0.336717`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.265747, "gap_delta": 0.000224, "runtime_inflation": 0.336717, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.049643`, combined `0.117954`.
- Accepted novelty `0.7365`, complexity `0.4425`, and adaptation efficiency `0.010363`.
- Last-epoch runtime `50.252975` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00524`, positive scaffolds `2`, Pareto runtime inflation `1.51959`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 1.664774, "gap_delta": -0.005462, "runtime_inflation": 1.51959, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.250653`, family holdout `0.068862`, combined `0.135838`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `83.168375` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.037997`, positive scaffolds `1`, Pareto runtime inflation `0.682188`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 1.485397, "gap_delta": 0.017888, "runtime_inflation": 0.682188, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.854962`, complexity `0.4375`, and adaptation efficiency `0.01392`.
- Last-epoch runtime `44.54995` ms and distance evaluations `4507.25`.
- Validation: surviving `False`, transplant delta `0.003506`, positive scaffolds `0`, Pareto runtime inflation `0.003318`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.003318, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite: Conservative Interpretation

## Summary
No discovered modular operators survive the critical transplant and ablation validations necessary to claim reusable operator structure or true transfer improvement.

---

## Key Transfer and Hold-Out Gaps (Primary Transfer Evidence)

| Condition                                 | Final Family Gap | Final Transfer Gap | Final TSPLIB Gap | Transplant Mean Gap Delta | Surviving Candidate? |
|-------------------------------------------|------------------|--------------------|------------------|---------------------------|---------------------|
| phase7_baseline_heuristic_only            | 0.05497          | 0.12132            | 0.23506          | 0.0                       | No                  |
| phase7_full_solver_evolution               | 0.06492          | 0.15940            | 0.21339          | 0.0                       | No                  |
| phase7_modular_operator_evolution          | 0.05497          | 0.12154            | 0.23567          | 0.00436                   | No                  |
| phase7_modular_operator_random_replay      | 0.05497          | 0.12154            | 0.23567          | 0.00698                   | No                  |
| **phase7_modular_operator_diversity_residual_replay** (best transfer condition) | **0.04964**      | **0.11795**        | **0.23506**      | 0.00524                   | No                  |
| phase7_modular_operator_compression_pressure | 0.06886          | 0.13584            | 0.25065          | 0.03800                   | No                  |
| phase7_modular_operator_pareto_selection    | 0.05497          | 0.12132            | 0.23506          | 0.00351                   | No                  |

---

## Surviving Candidates
- **None** of the conditions report surviving candidates.

---

## Modular Operators with Validation and Ablation Insights

### 1. Candidate Pruner Operators ("phase7_modular_operator_evolution" and "random_replay")
- **Core Idea**: Adaptive candidate pruning tuned for mixed Euclidean 2-opt neighborhoods.
- **Held-Out TSPLIB and Transfer Gaps**: No improvement vs. baseline heuristic.
- **Transplant**: Minor positive gap delta (>0.004), but no clear improvement.
- **Ablation**: Disabling operator causes no gap degradation, ablation does not support real operator effect.
- **Runtime Inflation**: High (~33% increase).
- **Conclusion**: Validation fails transplant and ablation checks; no reusable operator confirmed.

### 2. Restart Controller Operator ("phase7_modular_operator_diversity_residual_replay")
- **Core Idea**: Deterministic restart control adapting to stagnation with perturbation restarts.
- **Held-Out Gaps**: Slightly better family gap (0.0496 vs 0.05497 baseline), but no TSPLIB improvement.
- **Family Holdout Signal**: Improvement on "clustered_tsp" and "two_cluster_bottleneck_tsp" with -0.0046 mean gap delta.
- **Transplant**: Positive gap delta (~0.0052), no improvement over baseline, fails clean transplant into some scaffolds.
- **Ablation**: Disabling operator worsens gap (+0.0055 gap delta) indicating some operator effect but no survival.
- **Runtime Inflation**: Very high (~152% increase).
- **Conclusion**: Shows some structured, reusable control idea, but does not survive transplant ablation fully or TSPLIB improvement; not a surviving modular operator.

### 3. Scaffold Selector Operator ("phase7_modular_operator_compression_pressure")
- **Core Idea**: Instance descriptor-based selection among baseline scaffolds.
- **Held-Out Gaps**: Worsens heldout TSPLIB gap substantially (gap delta +0.0198).
- **Transplant**: Large positive gap delta (~0.038), severe regressions in multiple families.
- **Ablation**: Disabling improves gap by ~0.0182, so operator likely harmful.
- **Runtime Inflation**: High (~68% increase).
- **Conclusion**: Fails all transfer and validation checks; not interesting.

### 4. Perturbation Operator ("phase7_modular_operator_pareto_selection")
- **Core Idea**: Deterministic stagnation escape with structured perturbations.
- **Held-Out Gaps**: No improvement over baseline.
- **Transplant**: Slight positive gap delta (~0.0035), no family improvement.
- **Ablation**: No effect when disabled (no gap delta).
- **Runtime Inflation**: Negligible (0.3%).
- **Conclusion**: No validated operator effect; fails survivor criteria.

---

## Pareto Tradeoffs Analysis
- None of the modular operators show better gap at same or lower runtime than baseline.
- Most have substantial runtime inflation (especially restart controller and candidate pruner).
- No Pareto improvements justify operator deployment.

---

## Conservative Conclusions

- **Held-Out TSPLIB Gap and Family Holdout Gap**: No modular operator improves these metrics conclusively.
- **Transplant and Ablation**: Operators fail to survive these critical checks; disabling operators often yields no degradation or even improvements.
- **Reusable Structure Evidence**: Weak or negative; no reusable operator structure established.
- **Full-Solver Performance**: The best full solver (phase7_full_solver_evolution) does not produce surviving modular operators.
- **Discovery Claim**: No modular operator survives scaffold/family transplant and ablation tests sufficiently to claim operator discovery or reusable module.
- **Recommendation**: Current operators may inspire future designs but are not ready for impact or claim as discovered building blocks.

---

# Summary Table: Operator Validation Status

| Operator Name                                      | Operator Type          | Final Transfer Gap | Transplant Mean Gap Delta | Ablation Supported? | Runtime Inflation | Surviving Candidate? | Comments                              |
|---------------------------------------------------|-----------------------|--------------------|---------------------------|---------------------|-------------------|---------------------|-------------------------------------|
| candidate_pruner_transfer_focus_mixed_euc_grid_bottleneck    | candidate_pruner      | 0.12154           | 0.00436                   | No                  | High (33%)        | No                  | No clear benefit, fails ablation    |
| instance_aware_candidate_pruner_transfer_stability_v1        | candidate_pruner      | 0.12154           | 0.00698                   | No                  | High (34%)        | No                  | Same as above                       |
| restart_controller_two_phase_bottleneck_v1                    | restart_controller    | 0.11795           | 0.00524                   | Partial (+0.00546 gap when disabled) | Very High (152%)  | No                  | Some operator effect but costly     |
| scaffold_selector_transfer_focus                              | scaffold_selector     | 0.13584           | 0.03800                   | No (disabling improves gap) | High (68%)        | No                  | Harmful, fails transplant & ablation|
| transfer_bottleneck_escape_perturbation                       | perturbation          | 0.12132           | 0.00351                   | No                  | Negligible (0.3%)  | No                  | No operator effect                  |

---

# Final Assessment

- The best transfer condition ("phase7_modular_operator_diversity_residual_replay") shows some operator effect but fails survival criteria for transplant and ablation and has too high runtime inflation.
- No operator qualifies as a robust, reusable discovered module.
- Full solver evolution yields best TSPLIB gap but no modular operator discovery.
- Operators are thus **not yet validated for reuse or transfer claims**.
```
