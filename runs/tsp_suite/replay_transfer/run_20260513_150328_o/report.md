# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay`.
- Best TSPLIB holdout gap: `tsplib_failure_replay`.
- Best synthetic holdout gap: `tsplib_failure_replay`.

## Run Metadata
- run_name: run_20260513_150328_o
- started_at_local: 2026-05-13 15:03:28
- finished_at_local: 2026-05-13 15:13:57
- duration_hhmm: 00:10
- duration_seconds: 629.322
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.116589 | 0.010343 | 0.077954 | 0.664145 | 0.76 | 0.034776 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.793498 | 0.56 | -0.031386 |
| tsplib_failure_replay | failure | score_only | False | 0.096403 | 0.0 | 0.061347 | 0.679064 | 0.76 | 0.028617 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.203768 | 0.0 | 0.129671 | 0.683973 | 0.76 | 0.020722 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.116589`, synthetic `0.010343`, combined `0.077954`.
- Accepted-epoch count `3`, mean accepted code novelty `0.664145`, and final complexity `0.76`.
- Adaptation efficiency `0.034776` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.116589` across 7 instances; family means: ch=0.126198, kroD=0.125059, pcb=0.201603, pr=0.041208, rd=0.065487, st=0.13037.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18952, "family": "lin", "name": "lin105", "optimality_gap": 0.318033}, {"best_known_cost": 2579, "cost": 3385, "family": "a", "name": "a280", "optimality_gap": 0.312524}, {"best_known_cost": 7542, "cost": 9203, "family": "berlin", "name": "berlin52", "optimality_gap": 0.220233}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.793498`, and final complexity `0.56`.
- Adaptation efficiency `-0.031386` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.096403`, synthetic `0.0`, combined `0.061347`.
- Accepted-epoch count `3`, mean accepted code novelty `0.679064`, and final complexity `0.76`.
- Adaptation efficiency `0.028617` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.096403` across 7 instances; family means: ch=0.086971, kroD=0.084014, pcb=0.25448, pr=0.119805, rd=0.020354, st=0.022222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3371, "family": "a", "name": "a280", "optimality_gap": 0.307096}, {"best_known_cost": 14379, "cost": 18335, "family": "lin", "name": "lin105", "optimality_gap": 0.275123}, {"best_known_cost": 629, "cost": 763, "family": "eil", "name": "eil101", "optimality_gap": 0.213037}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.203768`, synthetic `0.0`, combined `0.129671`.
- Accepted-epoch count `3`, mean accepted code novelty `0.683973`, and final complexity `0.76`.
- Adaptation efficiency `0.020722` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.203768` across 7 instances; family means: ch=0.173538, kroD=0.233117, pcb=0.229568, pr=0.316423, rd=0.171302, st=0.128889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3460, "family": "a", "name": "a280", "optimality_gap": 0.341605}, {"best_known_cost": 14379, "cost": 16420, "family": "lin", "name": "lin105", "optimality_gap": 0.141943}, {"best_known_cost": 7542, "cost": 8479, "family": "berlin", "name": "berlin52", "optimality_gap": 0.124238}]

## Judge Appendix
### Summary of Results: Replay-Aware TSP Benchmark Suite

| Condition                      | Synthetic Holdout Gap | TSPLIB Holdout Gap | Transfer Gap | Replay Mode               | Final Complexity | Code Novelty (Mean) | Notes                                                                                     |
|-------------------------------|----------------------|-------------------|--------------|--------------------------|------------------|---------------------|-------------------------------------------------------------------------------------------|
| **tsplib_failure_replay**      | **0.000**            | **0.0964**        | **0.0613**   | Failure replay           | 0.76             | 0.679               | Best performance for synthetic, TSPLIB holdout, and transfer gaps.                        |
| tsplib_no_replay               | 0.0103               | 0.1166            | 0.0780       | None                     | 0.76             | 0.664               | Moderate gaps; no replay baseline.                                                       |
| tsplib_failure_replay_compression | 0.000                 | 0.2038            | 0.1297       | Failure replay + compression | 0.76             | 0.684               | Transfer and TSPLIB gaps worse than failure replay without compression despite similar novelty. |
| tsplib_random_replay           | 0.0649               | 0.2134            | 0.1594       | Random replay            | 0.56             | 0.793               | Worst transfer and TSPLIB gaps despite highest code novelty; lower model complexity.     |

---

### Interpretation

- **Best Transfer and Optimality Performance**  
  The **tsplib_failure_replay** condition yields the lowest holdout gaps on both TSPLIB (0.0964) and synthetic benchmarks (0.0), as well as the lowest transfer gap (0.0613). This indicates superior transfer capability and optimization quality under failure replay.

- **No Replay vs Failure Replay**  
  Compared to the **no replay** baseline, failure replay improves holdout gaps (TSPLIB gap reduced from 0.1166 to 0.0964; transfer gap from 0.0780 to 0.0613), supporting that failure replay is beneficial for generalization and transfer.

- **Random Replay**  
  Random replay leads to substantially worse transfer and holdout gaps (TSPLIB: 0.2134; transfer: 0.1594). Despite having the highest code novelty (0.793 mean) and lower complexity (0.56), random replay harms optimality and transfer, showing that lexical/code novelty alone is not indicative of better algorithms.

- **Failure Replay with Compression Pressure**  
  Although compression pressure is applied here, the **tsplib_failure_replay_compression** condition performs worse than failure replay alone, doubling the TSPLIB gap to 0.204 and transfer gap to 0.130. Code novelty remains similar to failure replay without compression, indicating compression reduces transfer efficacy without adding algorithmic innovation.

---

### Conclusion

- **Failure Replay (tsplib_failure_replay) is the most effective replay mode**, yielding the best transfer and optimality-gap metrics, outperforming both no replay and random replay.
- **Code novelty does not correlate positively with transfer performance:** random replay shows higher novelty but worse gaps.
- **Compression-aware replay reduces transfer quality** compared to failure replay without compression, despite similar novelty and complexity.
  
The evidence stresses prioritizing **optimality-gap and transfer metrics over code novelty or speculative narrative**. Failure replay yields improved transfer and should be favored in replay-aware TSP optimization benchmarks.
