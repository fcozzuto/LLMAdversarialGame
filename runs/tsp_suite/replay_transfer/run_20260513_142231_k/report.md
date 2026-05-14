# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_142231_k
- started_at_local: 2026-05-13 14:22:31
- finished_at_local: 2026-05-13 14:32:09
- duration_hhmm: 00:10
- duration_seconds: 578.242
- seed_offset: 10000
- replicate_label: k
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.767125 | 0.56 | -0.032465 |
| tsplib_random_replay | random | score_only | False | 0.182623 | 0.0 | 0.116215 | 0.781271 | 0.76 | 0.010072 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.861375 | 0.56 | -0.028913 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.767125`, and final complexity `0.56`.
- Adaptation efficiency `-0.032465` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.182623`, synthetic `0.0`, combined `0.116215`.
- Accepted-epoch count `2`, mean accepted code novelty `0.781271`, and final complexity `0.76`.
- Adaptation efficiency `0.010072` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.182623` across 7 instances; family means: ch=0.130649, kroD=0.25162, pcb=0.229765, pr=0.223199, rd=0.205815, st=0.106667.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10118, "family": "berlin", "name": "berlin52", "optimality_gap": 0.341554}, {"best_known_cost": 2579, "cost": 3293, "family": "a", "name": "a280", "optimality_gap": 0.276851}, {"best_known_cost": 629, "cost": 773, "family": "eil", "name": "eil101", "optimality_gap": 0.228935}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.861375`, and final complexity `0.56`.
- Adaptation efficiency `-0.028913` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Suite Results

| Condition                          | Replay Mode           | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer vs Novelty                           |
|----------------------------------|----------------------|------------------|---------------------|--------------------|---------------------|------------|-------------------------------------------------------|
| **tsplib_random_replay** (best)   | Random Replay        | **0.1826**       | **0.0**             | **0.1162**         | 0.7813              | 0.76       | Best transfer performance despite lower code novelty than failure replay conditions. Synthetic gap zero indicates strong generalization on synthetic holdout. |
| tsplib_no_replay                 | None                 | 0.2134           | 0.0649              | 0.1594             | 0.7671              | 0.56       | Higher transfer gap than random replay, with slightly lower novelty but better than failure replay compression on transfer. |
| tsplib_failure_replay            | Failure Replay       | 0.2134           | 0.0649              | 0.1594             | 0.8614              | 0.56       | High code novelty but transfer and TSPLIB gaps equal to no replay; no transfer gain despite novelty increase. |
| tsplib_failure_replay_compression | Failure Replay + Compression | 0.2134           | 0.0649              | 0.1594             | 0.0                 | 0.56       | No code novelty with compression pressure; transfer performance matches no replay and failure replay, indicating no benefit from compression or novelty gating in transfer. |

---

### Conservative Interpretation

- **Transfer Evidence:**
  - The **tsplib_random_replay** condition yields the best **held-out TSPLIB gap (0.1826)** and **synthetic holdout gap (0.0)**, outperforming no replay and failure replay modes.
  - The **mean transfer gap (0.1162)** is the lowest under random replay, indicating improved generalization to new problem instances.
  - No replay and failure replay variants show identical TSPLIB and transfer gaps (~0.2134 and ~0.1594 respectively), suggesting no transfer improvement in these conditions.

- **Code Novelty vs Transfer:**
  - Failure replay conditions increase code novelty (~0.86 for failure replay, 0.0 with compression), but **do not improve transfer metrics** relative to no replay.
  - Random replay shows **lower code novelty (0.78)** compared to failure replay but achieves **better transfer performance**.
  - Compression-aware failure replay results in *zero* code novelty and no transfer improvement, indicating compression or novelty gating suppresses novelty without transfer gain.

- **Replay Modes:**
  - **Random Replay** positively affects transfer despite somewhat reduced novelty compared to failure replay.
  - **Failure Replay**, with or without compression, fails to yield transfer improvement, though failure replay shows the highest code novelty.
  - **No Replay** shows intermediate novelty and transfer performance.

- **Complexity:**
  - Random replay condition uses more complex solutions (0.76) than others (0.56), possibly contributing to transfer gains.

---

### Conclusion

- **Random replay of TSPLIB instances is the best strategy for improving transfer performance** on both held-out real and synthetic benchmarks.
- This improvement occurs **despite reduced code novelty** compared to failure replay; hence, **lexical novelty does not equate to improved algorithmic transfer** here.
- Failure replay modes increase novelty significantly but do **not translate to better transfer gaps**, indicating novelty increase alone is insufficient for transfer.
- Compression-aware replay suppresses novelty without effect on transfer or held-out gaps, suggesting no advantage here.
- Therefore, prioritizing **optimality gap and transfer measures supports random replay** as the optimal replay mode in this suite.
