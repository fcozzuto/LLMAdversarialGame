# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_133240_f
- started_at_local: 2026-05-13 13:32:40
- finished_at_local: 2026-05-13 13:42:21
- duration_hhmm: 00:10
- duration_seconds: 581.273
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.907174 | 0.56 | -0.027453 |
| tsplib_random_replay | random | score_only | False | 0.122993 | 0.0 | 0.078268 | 0.751012 | 0.76 | 0.070532 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.878769 | 0.56 | -0.028341 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.907174`, and final complexity `0.56`.
- Adaptation efficiency `-0.027453` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.122993`, synthetic `0.0`, combined `0.078268`.
- Accepted-epoch count `3`, mean accepted code novelty `0.751012`, and final complexity `0.76`.
- Adaptation efficiency `0.070532` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.122993` across 7 instances; family means: ch=0.090517, kroD=0.126843, pcb=0.202982, pr=0.163389, rd=0.1067, st=0.08.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3418, "family": "a", "name": "a280", "optimality_gap": 0.32532}, {"best_known_cost": 629, "cost": 790, "family": "eil", "name": "eil101", "optimality_gap": 0.255962}, {"best_known_cost": 7542, "cost": 9209, "family": "berlin", "name": "berlin52", "optimality_gap": 0.221029}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.878769`, and final complexity `0.56`.
- Adaptation efficiency `-0.028341` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
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
### Benchmark Suite Summary

| Condition                      | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Replay Mode | Code Novelty (mean/last) | Final Complexity | Adaptation Efficiency |
|-------------------------------|------------------|--------------------|--------------------|-------------|--------------------------|------------------|-----------------------|
| tsplib_no_replay               | 0.2134           | 0.0649             | 0.1594             | none        | 0.9072 / 0.8997          | 0.56             | -0.0275               |
| **tsplib_random_replay**       | **0.1230**       | **0.0000**         | **0.0783**         | random      | 0.7510 / 0.7432          | 0.76             | 0.0705                |
| tsplib_failure_replay          | 0.2134           | 0.0649             | 0.1594             | failure     | 0.8788 / 0.8665          | 0.56             | -0.0283               |
| tsplib_failure_replay_compression | 0.2134         | 0.0649             | 0.1594             | failure & compression | 0.0 / 0.0                 | 0.56             | 0.0                   |

---

### Conservative Interpretation

1. **Transfer Performance (TSPLIB and Synthetic Gaps):**  
   - The **tsplib_random_replay** condition achieves the **lowest held-out TSPLIB gap (0.1230)** and **lowest synthetic holdout gap (0.0000)**, indicating superior transfer ability relative to others.
   - No-replay and failure-replay conditions have identical and substantially higher TSPLIB gaps (~0.2134) and synthetic gaps (~0.0649).
   - Compression-aware failure replay does not improve transfer gap compared to failure replay; its metrics are identical.

2. **Optimality Gaps Details:**  
   - Family-level TSPLIB gaps under tsplib_random_replay are consistently lower than no replay and failure replay, supporting better optimality.
   - Worst heldout TSPLIB instances show tsplib_random_replay reduces the largest gaps (max ~0.203) compared to no/failure replay (~0.350).
   - Synthetic holdout worst cases have zero gap under random replay, contrasting with higher gaps (e.g., 0.260 for grid_outliers) under no and failure replay.

3. **Code Novelty vs Transfer:**  
   - Code novelty (mean and last) is **lower in tsplib_random_replay (~0.75) compared to no replay (~0.91) and failure replay (~0.88)**.
   - Despite the drop in code novelty, the transfer performance improves substantially under random replay.
   - Compression-aware failure replay shows zero code novelty and no transfer improvement, suggesting no novelty does not guarantee transfer gains.
   - This supports the conclusion that **increased novelty is not required for improved transfer here**.

4. **Replay Modes:**  
   - **No replay and failure replay have identical results, implying failing replay does not improve transfer relative to no replay.**
   - **Random replay uniquely provides the best transfer and synthetic results with moderate complexity increase (0.76 vs 0.56).**
   - Compression pressure with failure replay neither lowers gaps nor increases novelty or efficiency, suggesting compression-aware failure replay is ineffective here.

5. **Adaptation Efficiency and Complexity:**  
   - Only random replay shows positive adaptation efficiency (0.0705), consistent with improved transfer.
   - Random replay increases final complexity (0.76), reflecting more complex solutions, possibly aiding optimization.
   - No replay and failure replay have negative or zero efficiency.

---

### Key Takeaways

- **Random replay outperforms no replay and failure replay in terms of TSPLIB holdout optimality gap and synthetic holdout gap, indicating superior transfer ability.**
- **This transfer gain occurs despite decreased code novelty, indicating code novelty alone is not indicative of algorithmic innovation.**
- **Failure replay and compression-aware failure replay do not improve transfer relative to no replay, despite higher code novelty in failure replay (except zero in compression).**
- **Random replay is associated with positive adaptation efficiency and increased complexity, supporting its effectiveness.**

---

### Summary Statement

The tsplib_random_replay condition provides the best overall transfer performance, evidenced by the lowest TSPLIB and synthetic holdout gaps and positive adaptation efficiency, despite reduced code novelty compared to other conditions. Failure replay and compression-aware failure replay fail to improve transfer beyond no replay, even with higher or zero code novelty, respectively. Thus, random replay uniquely enhances productive generalization in this benchmark suite without requiring heightened code novelty.
