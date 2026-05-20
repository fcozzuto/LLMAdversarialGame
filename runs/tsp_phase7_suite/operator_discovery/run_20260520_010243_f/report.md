# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_010243_f
- started_at_local: 2026-05-20 01:02:43
- finished_at_local: 2026-05-20 01:38:21
- duration_hhmm: 00:36
- duration_seconds: 2137.641
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.083222 | 0.003941 | 0.054393 | 0.840904 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.826805 | 0.4425 | False | 0.005319 | 1.835159 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.046321 | 0.115856 | 0.745094 | 0.445 | False | 0.00921 | 0.881022 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.241011 | 0.143086 | 0.179164 | 0.0 | 0.445 | False | 0.027675 | 24.116978 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.898566 | 0.4975 | False | 0.007362 | 0.928358 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.238386 | 0.064041 | 0.128273 | 0.0 | 0.4425 | False | 0.001658 | 0.014599 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.083222`, family holdout `0.003941`, combined `0.054393`.
- Accepted novelty `0.840904`, complexity `0.76`, and adaptation efficiency `0.038881`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.826805`, complexity `0.4425`, and adaptation efficiency `0.007`.
- Last-epoch runtime `43.07635` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.005319`, positive scaffolds `2`, Pareto runtime inflation `1.835159`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 1.785695, "gap_delta": -0.002615, "runtime_inflation": 1.835159, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.745094`, complexity `0.445`, and adaptation efficiency `0.014726`.
- Last-epoch runtime `72.336825` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00921`, positive scaffolds `1`, Pareto runtime inflation `0.881022`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.91212, "gap_delta": -0.005462, "runtime_inflation": 0.881022, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.241011`, family holdout `0.143086`, combined `0.179164`.
- Accepted novelty `0.0`, complexity `0.445`, and adaptation efficiency `0.0`.
- Last-epoch runtime `44.770675` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.027675`, positive scaffolds `1`, Pareto runtime inflation `24.116978`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 628.593581, "gap_delta": 0.057846, "runtime_inflation": 24.116978, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.898566`, complexity `0.4975`, and adaptation efficiency `0.010627`.
- Last-epoch runtime `83.88895` ms and distance evaluations `4281.5`.
- Validation: surviving `False`, transplant delta `0.007362`, positive scaffolds `1`, Pareto runtime inflation `0.928358`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.911481, "gap_delta": -0.003304, "runtime_inflation": 0.928358, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.238386`, family holdout `0.064041`, combined `0.128273`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `101.97515` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.001658`, positive scaffolds `1`, Pareto runtime inflation `0.014599`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006956, "runtime_inflation": 0.014599, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Overview
- **Main transfer evidence**: Held-out TSPLIB gap and family holdout gap.
- **Modular operator interest criterion**: Validation survival after transplant or ablation.
- **Priority**: Reusable operator structure claims over full-solver performance.
- **Algorithm discovery**: Only if operator survives scaffold and family tests.

---

## Summary of Conditions

| Condition Name                        | Final Family Gap | Final Transfer Gap | Final TSPLIB Gap | Ablation Support | Transplant Support | Surviving Candidate | Operator Type          | Key Notes                          |
|-------------------------------------|-----------------|--------------------|------------------|------------------|--------------------|---------------------|------------------------|-----------------------------------|
| phase7_baseline_heuristic_only      | 0.054968        | 0.121317           | 0.235058         | N/A              | None               | No                  | n/a                    | Baseline only                     |
| phase7_full_solver_evolution        | 0.003941        | 0.054393           | 0.083222         | No               | No                 | No                  | n/a                    | Full solver; no modular operator |
| phase7_modular_operator_evolution   | 0.046321        | 0.115856           | 0.235058         | Marginal (0.0026) | Weak positive (0.0053) | No                  | restart_controller      | Ablation shows slight gap increase if disabled; partial transplant gains in some scaffolds; high runtime inflation (~1.8x); failed transplant into sparse_three_opt |
| phase7_modular_operator_random_replay | 0.046321     | 0.115856           | 0.235058         | Marginal (0.0055) | Weak positive (0.0092) | No                  | restart_controller      | Similar to above; slight ablation gap increase if disabled; only 1 positive scaffold; high runtime inflation (0.88x) |
| phase7_modular_operator_diversity_residual_replay | 0.143086 | 0.179164          | 0.241011         | Negative effect (disabling improves gap by ~0.0578) | Negative (gap worsens with operator transplant, +0.0277) | No                  | scaffold_selector       | Operator consistently underperforms baseline (esp. heldout TSPLIB and many families); ablation does not support effect; numerous transplant failures; very high runtime inflation (24x) |
| phase7_modular_operator_compression_pressure | 0.050827 | 0.118702          | 0.235058         | Marginal (0.0033) | Weak positive (0.0074) | No                  | restart_controller      | Similar pattern to restart controllers above; no significant ablation impact; failed transplant to sparse_three_opt; runtime inflation ~0.93 |
| phase7_modular_operator_pareto_selection | 0.064041  | 0.128273          | 0.238386         | No (disabling improved gap by 0.0069) | Negative (gap delta +0.0017) | No                  | candidate_ranker        | No clear validation; underperformed in grid-like family; multiple transplant failures; minimal positive signals |

---

## Conservative Interpretation

### 1. **Full Solver and Baseline Conditions**
- Full solver evolution condition shows good family and transfer gaps (0.0039 fam gap, 0.054 transfer gap), but no modular operator component.
- Baseline is significantly worse on all fronts.

### 2. **Modular Operators of type "restart_controller"**
- Appear in multiple related conditions (modular_operator_evolution, random_replay, compression_pressure).
- Ablation results:
  - Slight (but small) performance degradation when disabled, supporting some operator effect.
  - Variants with fixed or wider restart budgets show no gap changes vs. full.
- Transfer:
  - Moderate to weak positive transplant mean gap deltas (~0.005-0.009), only 1-2 positive scaffolds out of 5.
- Family holdout gap improvements are modest and concentrated in "clustered_tsp" and "two_cluster_bottleneck_tsp" families.
- Failure to transplant cleanly into some scaffolds (especially sparse_three_opt) limits reuse claim.
- Runtime inflation notable (around 0.88 to 1.83 times), reducing practicality.
- Final TSPLIB gaps remain high (~0.235), same as baseline for heldout TSPLIB instances.

**Conclusion:**  
The restart_controller modular operators show some limited reusable structure signal for bottleneck and clustered TSP families but fail strong transplant and ablation checks to claim discovery or robust reuse. They are not surviving candidates under strict criteria.

### 3. **Scaffold Selector Operator**
- Shows consistent underperformance vs. baseline on held-out TSPLIB and most families.
- Ablation indicates disabling improves performance notably (gap delta -0.058).
- Transplant attempts failed in multiple scaffolds.
- Extremely high runtime inflation (~24x) further disqualifies.
- No survival evidence to claim operator efficacy.

**Conclusion:**  
Not interesting under all criteria; no validation support.

### 4. **Candidate Ranker Operator**
- No consistent family or transfer improvement.
- Ablation shows disabling operator improves performance.
- Transplant results are slightly negative.
- Underperforms on grid-like family and no families show clear gain.
- Not validated under transplant or ablation.

**Conclusion:**  
No reusable or transferable operator discovered here.

---

## Final Evaluation and Recommendations

| Criterion                 | Result Summary                                       | Interpretation                          |
|---------------------------|----------------------------------------------------|---------------------------------------|
| Held-out TSPLIB Gap       | Modular ops show no improvement over baseline      | No transfer improvement on hard set   |
| Family Holdout Gap        | Restart controllers show small gains in 2 families| Limited, non-robust effect             |
| Transplant Results        | Weak positive gap deltas in restart controllers    | Partial transfer; not consistent       |
| Ablation Tests            | Marginal or negative impact on operator removal    | Weak modular operator effect           |
| Pareto Tradeoffs          | Runtime inflation high; Pareto improvements absent | Unfavorable cost-benefit balance       |
| Survival as Candidate     | None survived; all flagged as non-surviving         | No confirmed reusable modular ops      |

---

### **Summary:**

- No modular operator satisfies transplant and ablation validation criteria robustly enough to claim discovery or reusable operator structure.
- Restart controllers provide weak evidence of reusable restart pressure control aiding bottlenecked TSP instances, but fail transplant into key scaffolds and exhibit high runtime cost.
- Other modular types (scaffold selector, candidate ranker) demonstrate negative or no transfer signals, ablation failures, and worse runtime profiles.
- Full-solver evolution yields best overall gaps but lacks modular operator confirmation.
- Conservative interpretation: No modular operator discovered that reliably transfers across families and scaffolds with validated improvement.
- Recommend revisiting modular designs focused on restart strategies with improved runtime efficiency and stronger transplant validation.

---
```
