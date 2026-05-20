# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_075148_r
- started_at_local: 2026-05-20 07:51:48
- finished_at_local: 2026-05-20 08:22:42
- duration_hhmm: 00:31
- duration_seconds: 1853.542
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.100187 | 0.0 | 0.063755 | 0.692044 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.843989 | 0.4375 | False | 0.008128 | 0.938393 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.046321 | 0.115856 | 0.896926 | 0.4425 | False | 0.00879 | 0.909128 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235667 | 0.054968 | 0.121542 | 0.783221 | 0.44 | False | 0.004996 | 0.384599 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235667 | 0.054968 | 0.121542 | 0.0 | 0.4375 | False | 0.006824 | 0.398175 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235667 | 0.054968 | 0.121542 | 0.0 | 0.4425 | False | 0.005954 | 0.227707 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.100187`, family holdout `0.0`, combined `0.063755`.
- Accepted novelty `0.692044`, complexity `0.76`, and adaptation efficiency `0.027395`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.843989`, complexity `0.4375`, and adaptation efficiency `0.006857`.
- Last-epoch runtime `99.643275` ms and distance evaluations `5266.75`.
- Validation: surviving `False`, transplant delta `0.008128`, positive scaffolds `1`, Pareto runtime inflation `0.938393`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.881272, "gap_delta": -0.002615, "runtime_inflation": 0.938393, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.896926`, complexity `0.4425`, and adaptation efficiency `0.006452`.
- Last-epoch runtime `60.1969` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00879`, positive scaffolds `1`, Pareto runtime inflation `0.909128`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.88592, "gap_delta": -0.005462, "runtime_inflation": 0.909128, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.783221`, complexity `0.44`, and adaptation efficiency `0.007454`.
- Last-epoch runtime `39.656` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.004996`, positive scaffolds `1`, Pareto runtime inflation `0.384599`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.289173, "gap_delta": 0.000224, "runtime_inflation": 0.384599, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.0`, complexity `0.4375`, and adaptation efficiency `0.0`.
- Last-epoch runtime `126.971425` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.006824`, positive scaffolds `1`, Pareto runtime inflation `0.398175`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.308765, "gap_delta": 0.000224, "runtime_inflation": 0.398175, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `104.245025` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.005954`, positive scaffolds `1`, Pareto runtime inflation `0.227707`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.186363, "gap_delta": 0.000224, "runtime_inflation": 0.227707, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Overview
- **Main transfer evidence:** held-out TSPLIB gap & family holdout gap.
- **Key criteria for interesting modular operators:** validation surviving transplant and ablation checks.
- **Prefer reusable operator structure claims over full-solver performance unless modular validation is strong.
- **No algorithm discovery claim:** no operator survives scaffold and family tests.

---

## Summary of Conditions

| Condition                            | Operator Type       | Family Holdout Gap | TSPLIB Gap     | Transplant Mean Gap Delta | Ablation Signal       | Surviving Candidate | Comments Summary                                                                                       |
|------------------------------------|---------------------|--------------------|----------------|---------------------------|-----------------------|---------------------|-----------------------------------------------------------------------------------------------------|
| phase7_baseline_heuristic_only     | n/a                 | 0.054968           | 0.235058       | 0.0                       | n/a                   | No                  | Baseline only; no novel operator.                                                                  |
| phase7_full_solver_evolution       | n/a                 | 0.0                | 0.100187       | 0.0                       | n/a                   | No                  | Full-solver mode, no modular operator candidate surviving.                                          |
| phase7_modular_operator_evolution  | restart_controller  | 0.046321           | 0.235058       | +0.008128 (worse)          | Very weak (gap delta ~0.0026 w.r.t disabled) | No                  | Operator shows modest family gains on clustered instances but **fails transplant**, ablation weak; runtime inflated (~0.94). |
| phase7_modular_operator_random_replay | restart_controller  | 0.046321           | 0.235058       | +0.00879 (worse)           | Weak (gap delta ~0.0055 disabled)             | No                  | Similar restart controller variant, same transplant/ablation failures and high runtime inflation (~0.91). |
| phase7_modular_operator_diversity_residual_replay | candidate_pruner    | 0.054968           | 0.235667       | +0.004996 (worse)          | Negative/Ablation shows no harm when disabled | No                  | Candidate pruner transfers poorly, no family improvements, ablation signal absent, runtime inflation moderate (~0.38).     |
| phase7_modular_operator_compression_pressure | candidate_pruner    | 0.054968           | 0.235667       | +0.006824 (worse)          | Negative/Ablation shows no harm when disabled | No                  | Same limitations as above with compression pressure enforcement.                                    |
| phase7_modular_operator_pareto_selection | candidate_pruner    | 0.054968           | 0.235667       | +0.005954 (worse)          | Negative/Ablation shows no harm when disabled | No                  | No family transfer benefit; runtime inflated (~0.23); no clean transplant.                          |

---

## Detailed Interpretation

### Transfer & Held-out Gaps

- The baseline TSPLIB gap is high (~0.235).
- Modular operators (restart controllers) reduce family gap slightly on clustered families (approx. 0.0463 vs baseline 0.05497).
- Transfer gap improvements on held-out TSPLIB families are zero; no improvement in final TSPLIB gap across any modular operator.
- Candidate pruners do not improve family holdout or TSPLIB gaps.

### Transplant Results

- Restart controllers **do not transplant cleanly** into other scaffolds (`sparse_three_opt`, `clustered_local_search`) and generally worsen mean gaps slightly (+0.008) on transplant.
- Candidate pruners never show meaningful positive transplant effects; gap deltas are slightly positive (worse) or near zero with no clear improvement.

### Ablation Results

- Restart controllers have very weak ablation signals; disabling them results in only minor gap differences (~0.0026 to 0.0055), indicating limited operator impact.
- Candidate pruners show **no evidence of operator effect** since disabling does not harm performance, meaning their adaptive pruning likely does not contribute meaningfully.

### Pareto & Runtime Tradeoffs

- Restart controller operators have **high runtime inflation** (~0.9) and distance evaluation inflation (~0.88) with only tiny gap improvements (less than 0.003).
- Candidate pruners have moderate runtime inflation (~0.23 to 0.38) with no gap improvement.
- No operator achieves better gap at same or faster runtime.

### Survival & Selection

- No modular operator survives all tests (scaffold, transplant, family gap improvement, and ablation).
- All recovery signals negative or inconclusive.
- No positive scaffold count beyond 1; survival candidate flag is false for all.
- No operator qualifies as a robust reusable component based on provided data.

---

## Conclusions

1. **No modular operator passes conservative acceptance criteria**:
   - None improves held-out TSPLIB gap.
   - None survives transplant tests with positive or neutral gap impact.
   - Ablation tests suggest weak or no effective operator contribution.
   - Runtime costs negate minor gap gains.

2. **Restart controllers show some family-specific benefit but fail transplant and ablation checks and have high runtime inflation**; they are **not reusable modular operators** in current form.

3. **Candidate pruner operators fail to improve family or TSPLIB gaps, show no ablation importance, and do not transplant cleanly**, making their core ideas unvalidated as modular operators.

4. **No claims for discovered algorithm or reusable operator structure are supported by this data**.

---

## Recommendations

- Focus future exploration on improving operator transplant fidelity and ablation validation before claiming reusable operator structure.
- Investigate runtime inflation reduction for restart controllers to enable practical gains.
- Candidate pruner ideas may need reengineering or alternative adaptive criteria to demonstrate meaningful operator effect and transfer.

---

# Final Statement

**No modular operator candidate in this suite survives rigorous held-out TSPLIB gap, family holdout, transplant, and ablation validation criteria needed for reusable operator claims or algorithm discovery.** The discovered restart controllers and candidate pruners require further development and validation before being considered reusable modular components for TSP solvers.
```
