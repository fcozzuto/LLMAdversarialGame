# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_no_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_182303_p
- started_at_local: 2026-05-13 18:23:03
- finished_at_local: 2026-05-13 18:31:46
- duration_hhmm: 00:09
- duration_seconds: 522.918
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.148196 | 0.046162 | 0.097179 | 0.794255 | 0.78 | 0.026665 |
| atsp_random_replay | random | score_only | False | 0.190037 | 0.008454 | 0.099246 | 0.878183 | 0.58 | 0.037982 |
| atsp_failure_replay | failure | score_only | False | 0.197676 | 0.030781 | 0.114228 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.191565 | 0.029928 | 0.110747 | 0.0 | 0.78 | 0.0 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.148196`, synthetic `0.046162`, combined `0.097179`.
- Accepted-epoch count `3`, mean accepted code novelty `0.794255`, and final complexity `0.78`.
- Adaptation efficiency `0.026665` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.148196` across 4 instances; family means: ft=0.245764, ftv=0.278983, p=0.003203, ry=0.064832.
- Panel `synthetic_holdout` mean gap `0.046162` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.018328.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1774, "family": "ftv", "name": "ftv35", "optimality_gap": 0.204345}, {"best_known_cost": 1286, "cost": 1546, "family": "ftv", "name": "ftv33", "optimality_gap": 0.202177}, {"best_known_cost": 1530, "cost": 1819, "family": "ftv", "name": "ftv38", "optimality_gap": 0.188889}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190037`, synthetic `0.008454`, combined `0.099246`.
- Accepted-epoch count `2`, mean accepted code novelty `0.878183`, and final complexity `0.58`.
- Adaptation efficiency `0.037982` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190037` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.197676`, synthetic `0.030781`, combined `0.114228`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.197676` across 4 instances; family means: ft=0.307748, ftv=0.3292, p=0.008007, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 2082, "family": "ftv", "name": "ftv38", "optimality_gap": 0.360784}, {"best_known_cost": 1286, "cost": 1662, "family": "ftv", "name": "ftv33", "optimality_gap": 0.292379}, {"best_known_cost": 1473, "cost": 1774, "family": "ftv", "name": "ftv35", "optimality_gap": 0.204345}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.191565`, synthetic `0.029928`, combined `0.110747`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.191565` across 4 instances; family means: ft=0.307748, ftv=0.252945, p=0.030071, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.029928` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.034101, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1593, "family": "ftv", "name": "ftv33", "optimality_gap": 0.238725}, {"best_known_cost": 1473, "cost": 1646, "family": "ftv", "name": "ftv35", "optimality_gap": 0.117447}]

## Judge Appendix
### Summary of ATSP Replay-Aware Benchmark Results

| Condition                    | Replay Mode    | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer & Novelty                   |
|------------------------------|---------------|-----------------|--------------------|-------------------|---------------------|------------|----------------------------------------------|
| **atsp_no_replay**            | none          | **0.148**       | 0.046              | **0.097**         | 0.79                | 0.78       | Best transfer performance despite moderate code novelty; no replay. |
| **atsp_random_replay**        | random        | 0.190           | **0.008**          | 0.099             | **0.88**            | 0.58       | Best synthetic gap and highest code novelty but worse TSPLIB transfer than no replay. |
| **atsp_failure_replay**       | failure       | 0.198           | 0.031              | 0.114             | 0.0                 | 0.78       | Worst transfer gaps and zero code novelty. Failure replay without compression reduces performance. |
| **atsp_failure_replay_compression** | failure + compression | 0.192           | 0.030              | 0.111             | 0.0                 | 0.78       | Similar to failure replay in gaps and novelty; added compression pressure does not improve transfer. |

---

### Interpretation

- **Transfer Metrics (TSPLIB & Holdout Gaps):**  
  The **no replay condition achieves the best transfer to held-out TSPLIB ATSP problems** (mean gap 0.148), as well as superior transfer holdout gap (0.097). Even with no replay, transfer generalization is better than all replay conditions.  
  Synthetic holdout results favor the **random replay condition** with an exceptionally low synthetic gap (0.00845) but its TSPLIB transfer gap is worse (0.190), indicating that synthetic holdout gains do not reliably translate to transfer on more realistic TSPLIB instances.

- **Replay Impact:**  
  Using **random replay improves synthetic holdout gaps substantially but worsens TSPLIB transfer**.  
  Failure replay (with or without compression) results in the worst transfer performance and zero code novelty, indicating failure replay degrades generalization and code diversity here.

- **Code Novelty vs Transfer:**  
  The random replay condition shows **highest code novelty (0.88) with reduced transfer performance** compared to no replay. Conversely, no replay achieves **better transfer with slightly lower code novelty (0.79)**.  
  Failure replay conditions have **zero code novelty**, suggesting possibly conservative or degenerate behavior with lowest transfer performance.  
  This indicates that **code novelty increases with replay but does not correlate with improved transfer**.

- **Replay Modes:**  
  - **No replay**: best transfer on held-out TSPLIB and holds stable synthetic gaps.  
  - **Random replay**: best synthetic gaps and highest novelty but transfer on realistic problems degrades.  
  - **Failure replay (with and without compression)**: poor transfer, zero novelty, compression pressure does not improve results significantly.

---

### Conservative Conclusions

- **Best transfer to held-out TSPLIB ATSP problems is achieved under the no replay condition**, which also shows moderate code novelty and complexity.  
- **Random replay yields improved synthetic holdout gaps and increases code novelty but sacrifices transfer gap on TSPLIB problems, indicating that code novelty increase does not guarantee better real-world transfer.**  
- Failure replay conditions, regardless of compression, perform worst on transfer metrics and exhibit zero code novelty, thus are not beneficial in this context.  
- **Replay strategies influence code novelty and holdout synthetic gaps differently**, but optimal transfer to TSPLIB instances aligns with no replay, not with replay-induced novelty or compression pressure.

---

### Key Recommendation

Prioritize **no replay** mode when transfer to realistic ATSP benchmarks (like TSPLIB) is the main goal, despite potentially higher synthetic holdout gaps or lower code novelty. Replay mechanisms, especially failure replay, may hurt real-world transfer performance.
