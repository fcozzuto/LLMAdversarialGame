# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_diversity_residual_replay`.
- Best held-out TSPLIB gap: `phase7_modular_operator_diversity_residual_replay`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_085349_t
- started_at_local: 2026-05-20 08:53:49
- finished_at_local: 2026-05-20 09:24:56
- duration_hhmm: 00:31
- duration_seconds: 1866.809
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.880805 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235667 | 0.054968 | 0.121542 | 0.893186 | 0.4425 | False | 0.003387 | 0.316569 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.824053 | 0.4475 | False | 0.009583 | 0.318133 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.210324 | 0.041246 | 0.103538 | 0.0 | 0.445 | False | -0.003034 | 2.246598 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.887949 | 0.445 | False | 0.006407 | 1.083761 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.0 | 0.4475 | False | 0.009895 | 0.386275 |

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
- Accepted novelty `0.880805`, complexity `0.56`, and adaptation efficiency `-0.028275`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.893186`, complexity `0.4425`, and adaptation efficiency `0.137352`.
- Last-epoch runtime `40.167125` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003387`, positive scaffolds `1`, Pareto runtime inflation `0.316569`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.22697, "gap_delta": 0.000224, "runtime_inflation": 0.316569, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.824053`, complexity `0.4475`, and adaptation efficiency `0.009865`.
- Last-epoch runtime `93.11585` ms and distance evaluations `6364.75`.
- Validation: surviving `False`, transplant delta `0.009583`, positive scaffolds `1`, Pareto runtime inflation `0.318133`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.269436, "gap_delta": 0.000224, "runtime_inflation": 0.318133, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.210324`, family holdout `0.041246`, combined `0.103538`.
- Accepted novelty `0.0`, complexity `0.445`, and adaptation efficiency `0.0`.
- Last-epoch runtime `138.293125` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.003034`, positive scaffolds `4`, Pareto runtime inflation `2.246598`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 26.784097, "gap_delta": -0.01625, "runtime_inflation": 2.246598, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.887949`, complexity `0.445`, and adaptation efficiency `0.016348`.
- Last-epoch runtime `67.91075` ms and distance evaluations `4691.5`.
- Validation: surviving `False`, transplant delta `0.006407`, positive scaffolds `2`, Pareto runtime inflation `1.083761`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.954353, "gap_delta": -0.003304, "runtime_inflation": 1.083761, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.0`, complexity `0.4475`, and adaptation efficiency `0.0`.
- Last-epoch runtime `39.334` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.009895`, positive scaffolds `1`, Pareto runtime inflation `0.386275`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.275361, "gap_delta": 0.000224, "runtime_inflation": 0.386275, "same_gap_faster": false}

## Judge Appendix
# Review of TSP Modular-Operator Discovery Suite Results

## Summary of Evaluation Criteria and Priority
- **Main transfer evidence**: Held-out TSPLIB gap & family holdout gap.
- **Modular operator interest**: Must survive transplant and ablation validation.
- **Claims**: Focus on reusable operator structure rather than full solver unless modular conditions strongly support discovery.
- **Algorithm discovery**: Requires operator survival in scaffold and family tests.

---

## Conditions Overview

| Condition Name                          | Operator Type        | Final Family Gap | Final Transfer Gap | Final TSPLIB Gap | Ablation Support | Transplant Mean Gap Delta | Surviving Candidate |
|---------------------------------------|---------------------|------------------|--------------------|------------------|------------------|---------------------------|---------------------|
| phase7_baseline_heuristic_only        | n/a                 | 0.054968         | 0.121317           | 0.235058         | N/A              | 0.0                       | No                  |
| phase7_full_solver_evolution          | n/a                 | 0.064916         | 0.159398           | 0.213387         | N/A              | 0.0                       | No                  |
| phase7_modular_operator_evolution     | candidate_pruner    | 0.054968         | 0.121542           | 0.235667         | No               | 0.003387                  | No                  |
| phase7_modular_operator_random_replay | candidate_pruner    | 0.054968         | 0.121542           | 0.235667         | No               | 0.009583                  | No                  |
| phase7_modular_operator_diversity_residual_replay | scaffold_selector | 0.041246         | 0.103538           | 0.210324         | Partial (ablation shows disabling increases gap) | -0.003034                 | No                  |
| phase7_modular_operator_compression_pressure | restart_controller | 0.050827         | 0.118702           | 0.235058         | No               | 0.006407                  | No                  |
| phase7_modular_operator_pareto_selection | candidate_pruner    | 0.054968         | 0.121542           | 0.235667         | No               | 0.009895                  | No                  |

---

## Detailed Interpretation

### 1. Held-Out Transfer Gap and Family Holdout Gap

- The lowest held-out TSPLIB gap (0.210324) and transfer gap (0.103538) are reported by **phase7_modular_operator_diversity_residual_replay (scaffold_selector)**.
- This condition also shows **best family-level transfer improvements** with:
  - Mean family gap delta ≈ -0.0153 (improvement)
  - Positive scaffolds count = 4 (best positive scaffold transplant count)
  - Helpful families: heldout_tsplib, clustered_tsp, grid_like_tsp
- However, transplant results show:
  - Does *not* transplant cleanly into `cheapest_insertion_2opt`.
  - Runtime inflation is very high (2.2466×).
- Ablation:
  - Disabling operator **increases gap by +0.016** → moderate ablation signal supporting an operator effect.
  - However, a variant ("flattened_selector") performs even worse (+0.048 gap), while "shuffled_selector" slightly improves (-0.009).
- Despite good transfer & family gap results, the operator **did not survive as candidate**.

### 2. Modular Candidate Pruners (3 variant conditions: evolution, random_replay, pareto_selection)

- Final TSPLIB gaps ~0.2356, transfer gaps ~0.1215 — close to baseline.
- Ablation shows **no significant penalty when disabling** operator (disabling gap delta slightly negative ~ -0.0002), i.e., no ablation support.
- No family shows clear improvement; positive family count = 0.
- Runtime inflation ~0.3× (significant overhead).
- Transplant results:
  - Mean transplant gap delta slightly **worse** than baseline (0.0034 to 0.0099).
  - Only one or zero positive scaffolds.
- Not surviving candidate status.
- Conclusion: No evidence of reusable operator structure validated by ablation or transplant.

### 3. Restart Controller (phase7_modular_operator_compression_pressure)

- Moderate final transfer gap (0.1187) slightly better than baseline (0.1213).
- Ablation: disabling operator slightly worsens gap (+0.0033), which is weak ablation signal.
- Family-level signals weakly positive but only for one family (`two_cluster_bottleneck_tsp`).
- Runtime inflation ~1.08× and does not transplant cleanly into some scaffolds.
- Transplant mean gap delta positive (worsening) 0.0064 with only 2 positive scaffolds.
- Not surviving candidate status.

---

## Pareto Tradeoffs

- Scaffold selector (best transfer gap) has the highest runtime inflation (2.25×), but reduces gap more than others (~-0.01625 gap delta vs baseline).
- Candidate pruners offer minor or no gap improvements with ~0.3× runtime inflation.
- Restart controller has small gap improvement (-0.0033) with ~1.08× runtime inflation.
- No operator achieves better gap without runtime inflation or better runtime without losing gap.

---

## Transplant Validation

- No operator cleanly transplants across all tested scaffolds.
- Scaffold selector has positive scaffold counts but introduces large runtime overhead and inconsistent transplant success (negative transplant gap delta for some scaffolds).
- Candidate pruners and restart controllers show modest or negative transplant results with no ablation validation.

---

## Ablation Summary

- Scaffold selector is the only operator with a moderate ablation signal indicating it contributes positively to solution quality.
- Candidate pruners and restart controllers fail ablation tests (disabling does not degrade performance), so their effect is not validated.

---

## Conclusion and Recommendations

| Operator                       | Considered Interesting? | Reasoning |
|-------------------------------|------------------------|-----------|
| Scaffold Selector (phase7_modular_operator_diversity_residual_replay) | Marginally interesting but not surviving | Shows best transfer family gap improvements and some ablation support; however, large runtime inflation and failure to survive transplant and family validations prohibit claim of algorithm discovery. |
| Candidate Pruners (modular operator conditions) | Not interesting | No ablation validation, no family or transplant improvement, runtime inflation ~30%. |
| Restart Controller             | Not interesting         | Weak ablation, limited family help, runtime inflation >1×, no transplant survival. |

**No modular operator survived the full validation pipeline to support claims of reusable operator structure or algorithm discovery.**

---

# Final Summary

- **No modular operator qualifies as a surviving candidate.**
- The **scaffold selector operator** (phase7_modular_operator_diversity_residual_replay) shows the strongest evidence of reusable structure via transfer gap and family improvements with some ablation signal but suffers from large runtime inflation and transplant issues. It remains a **potentially reusable operator** but not confirmed.
- Candidate pruners and restart controllers fail ablation and transplant validation; their minor gap differences are indistinguishable from noise.
- Pareto tradeoffs disfavor these operators because improvements come at high runtime cost without robust validation.
- Full-solver evolution and baseline produce higher transfer gaps, indicating modular approaches capture some structural signal but fall short of validated improvement.
- **No claims of algorithm discovery or reliably reusable operator structure can be made.**

---

# Recommendations

- Focus future modular operator discovery on improving ablation and transplant robustness.
- Reduce runtime inflation to increase Pareto competitiveness.
- Scaffold selector variants merit further enhancement due to best transfer/family signals but require runtime and transplantation fixes.
- Candidate pruners and restart controllers need redesign or stronger validation signals before acceptance.

---

*This interpretation is conservative and prioritizes held-out gap, ablation, family transfer, transplant, and Pareto metrics in accordance with specified rules.*
