# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay`.
- Best TSPLIB holdout gap: `tsplib_failure_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_145329_n
- started_at_local: 2026-05-13 14:53:29
- finished_at_local: 2026-05-13 15:03:27
- duration_hhmm: 00:10
- duration_seconds: 597.297
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.096215 | 0.0 | 0.061228 | 0.900415 | 0.76 | -0.001811 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.853264 | 0.56 | -0.029188 |
| tsplib_failure_replay | failure | score_only | False | 0.077078 | 0.0 | 0.04905 | 0.853725 | 0.76 | 0.084983 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.096215`, synthetic `0.0`, combined `0.061228`.
- Accepted-epoch count `2`, mean accepted code novelty `0.900415`, and final complexity `0.76`.
- Adaptation efficiency `-0.001811` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.096215` across 7 instances; family means: ch=0.077801, kroD=0.069597, pcb=0.113396, pr=0.188926, rd=0.097092, st=0.048889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19928, "family": "lin", "name": "lin105", "optimality_gap": 0.38591}, {"best_known_cost": 629, "cost": 809, "family": "eil", "name": "eil101", "optimality_gap": 0.286169}, {"best_known_cost": 2579, "cost": 3296, "family": "a", "name": "a280", "optimality_gap": 0.278015}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.853264`, and final complexity `0.56`.
- Adaptation efficiency `-0.029188` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.077078`, synthetic `0.0`, combined `0.04905`.
- Accepted-epoch count `2`, mean accepted code novelty `0.853725`, and final complexity `0.76`.
- Adaptation efficiency `0.084983` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.077078` across 7 instances; family means: ch=0.036917, kroD=0.03602, pcb=0.201505, pr=0.105132, rd=0.093426, st=0.02963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3413, "family": "a", "name": "a280", "optimality_gap": 0.323381}, {"best_known_cost": 14379, "cost": 18619, "family": "lin", "name": "lin105", "optimality_gap": 0.294874}, {"best_known_cost": 7542, "cost": 8754, "family": "berlin", "name": "berlin52", "optimality_gap": 0.1607}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Results

| Condition                     | Replay Mode          | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (Mean) | Complexity | Notes on Transfer and Novelty                                 |
|-------------------------------|---------------------|-----------------|--------------------|-------------------|---------------------|------------|--------------------------------------------------------------|
| **tsplib_failure_replay**      | Failure Replay      | **0.0771**      | 0.0                | **0.0491**        | 0.854               | 0.76       | Best transfer and TSPLIB gaps; zero synthetic gap; moderate code novelty|
| **tsplib_no_replay**           | No Replay           | 0.0962          | **0.0**            | 0.0612            | **0.900**           | 0.76       | Best synthetic gap (zero), slightly worse transfer and TSPLIB gaps; highest code novelty|
| **tsplib_random_replay**       | Random Replay       | 0.2134          | 0.0649             | 0.1594            | 0.853               | 0.56       | Poorer transfer and TSPLIB gaps; some synthetic gap; moderate code novelty|
| **tsplib_failure_replay_compression** | Failure Replay + Compression | 0.2134          | 0.0649             | 0.1594            | 0.0                 | 0.56       | Matches random replay in gaps; zero code novelty; compression pressure evident |

---

### Interpretation

1. **Key Transfer Metrics (Held-out TSPLIB and Synthetic Holdout):**  
   - The **tsplib_failure_replay** condition achieves the best transfer performance, evidenced by the lowest held-out TSPLIB gap (0.077) and transfer gap (0.049), with zero synthetic holdout gap.  
   - **tsplib_no_replay** also achieves zero synthetic holdout gap but slightly higher transfer (0.061) and TSPLIB gap (0.096), indicating good but less strong transfer than failure replay.  
   - Both **tsplib_random_replay** and **tsplib_failure_replay_compression** show substantially poorer transfer performance (TSPLIB gap ~0.213, transfer gap ~0.159), indicating worse generalization.

2. **Code Novelty vs. Transfer:**  
   - Despite the **tsplib_failure_replay** condition having lower code novelty (mean 0.854) than no replay (mean 0.900), transfer performance improves significantly. This indicates that **improved transfer is not due to increased code novelty but better replay strategy (failure replay).**  
   - The **failure replay compression** condition has zero code novelty and poorer transfer, indicating that compression pressure and novelty gating limit algorithmic innovation and degrade transfer.  
   - Random replay has moderate code novelty (~0.853) but performs worse on transfer gaps, suggesting that random replay is less effective despite some novelty.

3. **Effect of Replay Mode:**  
   - **Failure replay** (no compression) clearly outperforms no replay and random replay in transfer and holds zero synthetic gap.  
   - **No replay** yields excellent synthetic generalization but inferior TSPLIB transfer.  
   - **Random replay** results in poorer transfer and synthetic generalization.  
   - **Failure replay with compression** degrades both transfer and novelty, negating the benefits of failure replay.

4. **Complexity and Behavior:**  
   - Higher complexity (0.76) was observed in no replay and failure replay conditions, associated with better transfer.  
   - Lower complexity (0.56) in random replay and failure replay compression correlates with worse transfer.

---

### Conclusions

- **Failure replay without compression yields the best transfer performance on held-out TSPLIB instances and synthetic benchmarks, outperforming no replay and other replay methods.**  
- **Improved transfer occurs despite a slight reduction in code novelty compared to no replay, showing that replay strategy, not lexical novelty alone, drives this improvement.**  
- **Compression-aware failure replay severely limits code novelty and transfer performance, indicating a detrimental trade-off.**  
- **Random replay is less effective for transfer despite moderate code novelty.**  

These results highlight the importance of carefully distinguishing replay types: **failure replay optimizes for transfer**, while compression pressure unduly restricts learned solutions and harms performance. Optimality gaps and transfer metrics provide the primary evidence; narrative speculation should refrain from equating code novelty with algorithmic novelty without this support.
