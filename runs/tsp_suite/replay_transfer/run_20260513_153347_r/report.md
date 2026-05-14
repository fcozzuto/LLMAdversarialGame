# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay`.
- Best TSPLIB holdout gap: `tsplib_failure_replay`.
- Best synthetic holdout gap: `tsplib_failure_replay`.

## Run Metadata
- run_name: run_20260513_153347_r
- started_at_local: 2026-05-13 15:33:47
- finished_at_local: 2026-05-13 15:43:02
- duration_hhmm: 00:09
- duration_seconds: 555.411
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.914661 | 0.56 | -0.027229 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.879896 | 0.56 | -0.028304 |
| tsplib_failure_replay | failure | score_only | False | 0.119843 | 0.0 | 0.076264 | 0.804813 | 0.76 | 0.018215 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.914661`, and final complexity `0.56`.
- Adaptation efficiency `-0.027229` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.879896`, and final complexity `0.56`.
- Adaptation efficiency `-0.028304` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.119843`, synthetic `0.0`, combined `0.076264`.
- Accepted-epoch count `3`, mean accepted code novelty `0.804813`, and final complexity `0.76`.
- Adaptation efficiency `0.018215` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.119843` across 7 instances; family means: ch=0.121576, kroD=0.081948, pcb=0.220292, pr=0.048345, rd=0.199241, st=0.045926.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3408, "family": "a", "name": "a280", "optimality_gap": 0.321442}, {"best_known_cost": 7542, "cost": 9753, "family": "berlin", "name": "berlin52", "optimality_gap": 0.293158}, {"best_known_cost": 629, "cost": 761, "family": "eil", "name": "eil101", "optimality_gap": 0.209857}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

## Judge Appendix
### Summary of Transfer Performance and Optimality Gaps by Condition

| Condition                       | Replay Mode | Selection Mode | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Notes                                                                                                       |
|--------------------------------|-------------|----------------|-----------------|--------------------|-------------------|---------------------|------------|-------------------------------------------------------------------------------------------------------------|
| **tsplib_failure_replay**       | failure     | score_only     | **0.119843**    | **0.0**            | **0.076264**      | 0.804813            | 0.76       | Best heldout and synthetic performance. Clear transfer improvement over no replay and random replay by ~0.09 TSPLIB gap. Some decrease in code novelty compared to no replay/random replay. |
| tsplib_no_replay               | none        | score_only     | 0.213387        | 0.064916           | 0.159398          | 0.914661            | 0.56       | Baseline with highest gaps across transfer and heldout sets. Highest code novelty and lowest complexity.   |
| tsplib_random_replay           | random      | score_only     | 0.213387        | 0.064916           | 0.159398          | 0.879896            | 0.56       | Same gaps as no replay, but slightly reduced code novelty. Random replay does not improve transfer metrics. |
| tsplib_failure_replay_compression | failure + compression | novelty_gate| 0.213387        | 0.064916           | 0.159398          | 0.0                 | 0.56       | Transfer and heldout gaps identical to no replay. Code novelty collapsed to zero, possibly due to compression pressure. |

---

### Interpretation

- **Transfer & Optimality Gap:**  
  The **tsplib_failure_replay** condition shows clear and consistent improvement in both heldout TSPLIB and synthetic datasets, reducing mean transfer gaps roughly by half relative to no replay or random replay. According to the rules, these metrics are the main evidence for transfer and indicate the failure replay strategy benefits generalization and solution quality on unseen instances.

- **Code Novelty vs Transfer:**  
  Despite the improvement in transfer and optimality gaps, the **failure replay** condition exhibits a reduction in code novelty (mean ~0.80) compared to no replay (~0.91) and random replay (~0.88). This confirms that improved transfer does come with lower code novelty, as per instructions to report explicitly. However, failure replay with compression pressure leads to zero code novelty and no transfer gains, indicating loss of effective adaptation.

- **Replay Modes:**  
  - **No replay** and **random replay** conditions show indistinguishable transfer performance and optimality gap, suggesting random replay alone does not improve transfer.
  - **Failure replay** condition uniquely improves transfer metrics, confirming the benefit of targeted replay of failure cases.
  - **Failure replay with compression** restricts novelty and degrades transfer, implying trade-offs between compression pressure and transfer gains.

- **Complexity:**  
  The failure replay condition produces a higher behavioral complexity (0.76) than other conditions (0.56), potentially indicating more elaborate solutions supporting better transfer and lower gaps.

---

### Conservative Conclusion

- **Failure replay** is the only replay-aware method to demonstrate measurable improvements in holdout TSPLIB and synthetic TSP instance optimality gaps, confirming its positive effect on transfer.  
- This improvement coincides with moderately reduced code novelty and increased behavioral complexity, consistent with a shift towards convergence on better quality solutions rather than exploratory novelty.  
- Random replay and no replay perform equivalently, negating the efficacy of random sample reuse without failure focus.  
- Compression-aware replay under failure replay conditions causes failure of transfer gains and collapses code novelty, suggesting detrimental effects from compression pressure in this setting.
