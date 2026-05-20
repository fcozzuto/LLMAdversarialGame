# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_full_solver_evolution`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_082243_s
- started_at_local: 2026-05-20 08:22:43
- finished_at_local: 2026-05-20 08:53:48
- duration_hhmm: 00:31
- duration_seconds: 1865.176
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.081984 | 0.0 | 0.052172 | 0.821136 | 0.76 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235667 | 0.054968 | 0.121542 | 0.792608 | 0.445 | False | 0.001735 | 0.344792 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.8657 | 0.44 | False | 0.003056 | 0.007338 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235871 | 0.054968 | 0.121617 | 0.83759 | 0.44 | False | 0.00543 | -0.035494 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.864706 | 0.445 | False | 0.005437 | 2.055607 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.866546 | 0.4425 | False | 0.003072 | -0.005965 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.081984`, family holdout `0.0`, combined `0.052172`.
- Accepted novelty `0.821136`, complexity `0.76`, and adaptation efficiency `0.047651`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.792608`, complexity `0.445`, and adaptation efficiency `0.00491`.
- Last-epoch runtime `139.384025` ms and distance evaluations `9649.75`.
- Validation: surviving `False`, transplant delta `0.001735`, positive scaffolds `1`, Pareto runtime inflation `0.344792`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.234827, "gap_delta": 0.000224, "runtime_inflation": 0.344792, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.8657`, complexity `0.44`, and adaptation efficiency `0.006874`.
- Last-epoch runtime `38.8161` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003056`, positive scaffolds `0`, Pareto runtime inflation `0.007338`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.007338, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235871`, family holdout `0.054968`, combined `0.121617`.
- Accepted novelty `0.83759`, complexity `0.44`, and adaptation efficiency `0.004617`.
- Last-epoch runtime `42.092525` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00543`, positive scaffolds `1`, Pareto runtime inflation `-0.035494`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.006899, "gap_delta": 0.000299, "runtime_inflation": -0.035494, "same_gap_faster": true}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.864706`, complexity `0.445`, and adaptation efficiency `0.019173`.
- Last-epoch runtime `42.7546` ms and distance evaluations `4333.0`.
- Validation: surviving `False`, transplant delta `0.005437`, positive scaffolds `2`, Pareto runtime inflation `2.055607`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 1.878498, "gap_delta": -0.003363, "runtime_inflation": 2.055607, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.866546`, complexity `0.4425`, and adaptation efficiency `0.019023`.
- Last-epoch runtime `39.878675` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003072`, positive scaffolds `0`, Pareto runtime inflation `-0.005965`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.005965, "same_gap_faster": true}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite Review

## Summary of Main Results

| Condition                              | Final Transfer Gap | Final Family Gap | Final TSPLIB Gap | Surviving Candidate | Transplant Mean Gap Delta | Ablation Support | Notes                                            |
|--------------------------------------|--------------------|------------------|------------------|---------------------|---------------------------|------------------|--------------------------------------------------|
| phase7_baseline_heuristic_only       | 0.121317           | 0.054968         | 0.235058         | No                  | 0.0                       | N/A              | Baseline only, no operator                       |
| phase7_full_solver_evolution         | 0.052172           | 0.0              | 0.081984         | No                  | 0.0                       | No               | Full solver evolution, no modular operators     |
| phase7_modular_operator_evolution    | 0.121542           | 0.054968         | 0.235667         | No                  | 0.001735                  | No               | Candidate pruner; no clear family or heldout gain; disabled variant no worse; runtime inflation high (0.34) |
| phase7_modular_operator_random_replay| 0.121317           | 0.054968         | 0.235058         | No                  | 0.003056                  | No               | Perturbation operator; no family/heldout gap improvement; ablation shows no operator effect |
| phase7_modular_operator_diversity_residual_replay | 0.121617           | 0.054968         | 0.235871         | No                  | 0.00543                   | No               | Candidate pruner variant; no family/heldout improvement; disabled variant no worse |
| phase7_modular_operator_compression_pressure | 0.118702           | 0.050827         | 0.235058         | No                  | 0.005437                  | No               | Restart controller; slight family gain on two_cluster_bottleneck; runtime inflation very high (2.05); ablation disabled hurts (gap +0.0033) |
| phase7_modular_operator_pareto_selection | 0.121317           | 0.054968         | 0.235058         | No                  | 0.003072                  | No               | Perturbation variant; no family/heldout gap improvement; ablation disabled no effect |

---

## Conservative Interpretation

### Transfer Evidence (Held-out TSPLIB and Family Gaps)
- None of the modular operators demonstrated improvements in held-out TSPLIB or family gaps relative to the host baseline or baseline heuristic.
- Slight positive or negative gap deltas on heldout TSPLIB and families are near zero, indicating no meaningful transfer gains.
- Only the compression pressure condition showed a modest family gain (-0.024425 gap delta) on the "two_cluster_bottleneck_tsp" family, but this came with high runtime inflation and no heldout TSPLIB gap improvement.

### Transplant Checks
- Transplant mean gap deltas for modular operators are small positive numbers (~0.0017 to 0.0054), indicating no consistent or clear improvement under transplant.
- Some scaffolds show minor positive delta, but no scaffold or transplant condition demonstrates robust gap improvements.
- Operators generally fail to transplant cleanly to some scaffolds (notably `clustered_local_search`), limiting claims of structural reusability.

### Ablation Checks
- Ablation results show that disabling operators does not worsen solution gaps.
- Best variant gap deltas vs. full operator are zero or slightly negative, indicating no ablation-supported operator effect.
- No operator shows convincing ablation signal confirming the operator’s contribution.

### Pareto & Runtime Tradeoffs
- Runtime inflation for modular operators is often high, e.g., ~0.34 for candidate pruners and 2.05 for restart controller.
- No Pareto improvements observed: better gap at same runtime or same gap at faster runtime.
- Reduced runtime variants exist but without gap improvements.

### Operator Survival & Discovery
- No operator survived modular transplant, ablation, and family transfer checks simultaneously.
- No operator classified as "surviving_candidate."
- No clear operator discovery supported by scaffold and family tests.

---

## Summary of Individual Operator Findings

1. **Candidate Pruner (phase7_modular_operator_evolution & diversity residual replay)**
   - Core idea: Adaptive candidate-list pruning adapting neighborhood size with structural cues.
   - Validation: No family or heldout TSPLIB gap improvement; disabling does not worsen gap; runtime overhead noticeable.
   - Transplant: Minor positive gap deltas but no survival.
   - Conclusion: Not a reusable or impactful operator under modular testing framework.

2. **Perturbation Operators (random replay & pareto selection)**
   - Core idea: Deterministic structured perturbations (double-bridge, segment reversal) for stagnation escape.
   - Validation: No family or heldout TSPLIB gap improvement; no ablation effect; no transplant survival.
   - Runtime inflation negligible or negative but no benefit.
   - Conclusion: Not validated as reusable stagnation escape operators.

3. **Restart Controller (compression pressure)**
   - Core idea: Adaptive restart count to escape bottlenecks, specifically two-cluster.
   - Validation: Small family gap gain on two_cluster_bottleneck_tsp, but no TSPLIB gain; runtime inflation significant.
   - Ablation disables operator leads to worse gap (~+0.0033), suggesting some modest operator effect.
   - Transplant shows minor positive gains on 2 scaffolds.
   - Conclusion: Marginal candidate with some family signal but poor transplant and high runtime cost; not surviving candidate.

---

## Final Conclusion

- None of the tested modular operators qualify as surviving candidates due to lack of consistent transfer gap improvements on held-out TSPLIB and family tests and failure of ablation and transplant validation.
- No operator can be claimed as reusable or structurally novel in the TSP context based on this data.
- No modular-operator "discovery" is supported.
- Full-solver performance gains in the best full_solver condition do not correspond to reusable modular operator effects.
- The suite correctly finds some candidate ideas (adaptive pruning, structured perturbation, adaptive restart), but these do not survive conservative validation to merit claims of effective modular operator discovery or transfer.

---

**Recommendation:**

Focus on improving operator validation pipelines to ensure ablation effects are detectable and transplant checks are more robust before claiming reusable operator structures or algorithm discovery from modular-operator evolution results.
```
