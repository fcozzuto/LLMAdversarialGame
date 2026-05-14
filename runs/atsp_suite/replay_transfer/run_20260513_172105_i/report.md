# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay_compression`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay_compression`.
- Best synthetic holdout gap: `atsp_no_replay`.

## Run Metadata
- run_name: run_20260513_172105_i
- started_at_local: 2026-05-13 17:21:05
- finished_at_local: 2026-05-13 17:29:28
- duration_hhmm: 00:08
- duration_seconds: 503.469
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.192839 | 0.009004 | 0.100922 | 0.713857 | 0.58 | 0.044079 |
| atsp_random_replay | random | score_only | False | 0.196068 | 0.041579 | 0.118823 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.19016 | 0.009004 | 0.099582 | 0.869385 | 0.58 | 0.007555 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.162165 | 0.020176 | 0.091171 | 0.786717 | 0.78 | 0.026743 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192839`, synthetic `0.009004`, combined `0.100922`.
- Accepted-epoch count `2`, mean accepted code novelty `0.713857`, and final complexity `0.58`.
- Adaptation efficiency `0.044079` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192839` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.003915, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.196068`, synthetic `0.041579`, combined `0.118823`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.196068` across 4 instances; family means: ft=0.280377, ftv=0.309361, p=0.019039, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1925, "family": "ftv", "name": "ftv35", "optimality_gap": 0.306857}, {"best_known_cost": 1530, "cost": 1968, "family": "ftv", "name": "ftv38", "optimality_gap": 0.286275}, {"best_known_cost": 1286, "cost": 1492, "family": "ftv", "name": "ftv33", "optimality_gap": 0.160187}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.19016`, synthetic `0.009004`, combined `0.099582`.
- Accepted-epoch count `6`, mean accepted code novelty `0.869385`, and final complexity `0.58`.
- Adaptation efficiency `0.007555` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.19016` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004093, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.162165`, synthetic `0.020176`, combined `0.091171`.
- Accepted-epoch count `3`, mean accepted code novelty `0.786717`, and final complexity `0.78`.
- Adaptation efficiency `0.026743` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.162165` across 4 instances; family means: ft=0.27748, ftv=0.318041, p=0.002313, ry=0.050825.
- Panel `synthetic_holdout` mean gap `0.020176` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1797, "family": "ftv", "name": "ftv35", "optimality_gap": 0.219959}, {"best_known_cost": 1530, "cost": 1842, "family": "ftv", "name": "ftv38", "optimality_gap": 0.203922}, {"best_known_cost": 1286, "cost": 1527, "family": "ftv", "name": "ftv33", "optimality_gap": 0.187403}]

## Judge Appendix
### Summary of Benchmark Comparison

| Condition                     | Replay Mode              | Code Novelty (mean) | Synthetic Holdout Gap | Held-Out TSPLIB Gap | Transfer Gap     | Compression Pressure | Notes on Transfer vs. Novelty                          |
|-------------------------------|-------------------------|---------------------|----------------------|---------------------|------------------|----------------------|--------------------------------------------------------|
| **atsp_no_replay**             | None                    | 0.714               | **0.009004 (best synthetic)** | 0.192839              | 0.100922         | No                   | Highest code novelty but worse transfer gaps than best transfer condition |
| **atsp_random_replay**         | Random                  | 0.0                 | 0.041579              | 0.196068              | 0.118823         | No                   | Zero code novelty; worse transfer and synthetic gaps than failure replay |
| **atsp_failure_replay**        | Failure                 | 0.869               | 0.009004              | 0.19016               | 0.099582         | No                   | Highest code novelty, slightly better transfer gaps than no replay |
| **atsp_failure_replay_compression** | Failure + Compression-aware | 0.787               | 0.020176              | **0.162165 (best TSPLIB)** | **0.091171 (best transfer)** | Yes                  | Transfer metrics improved despite slight code novelty decrease compared to failure_replay |

---

### Interpretation

- **Transfer Evidence (Primary Focus):**
  - The **best transfer** and **best held-out TSPLIB performance** occur under **atsp_failure_replay_compression** condition, with transfer gap 0.091 and TSPLIB gap 0.162, respectively.
  - **No replay (atsp_no_replay)** has the **lowest synthetic gap (0.009)** but significantly worse transfer gaps (TSPLIB 0.193, transfer 0.101).
  - **Random replay** performed worst in transfer metrics; also zero code novelty.

- **Code Novelty vs. Transfer:**
  - Code novelty is highest in **atsp_failure_replay** (0.869 mean), but transfer gaps are marginally worse than those in compression-aware failure replay.
  - Despite some code novelty reduction from failure_replay (0.869) to failure_replay_compression (0.787), transfer metrics improve. This indicates that **transfer gains happen even with reduced code novelty**, emphasizing that code novelty alone does not guarantee better transfer.
  - Random replay with zero code novelty yields the poorest transfer, confirming novelty is necessary but not sufficient.

- **Replay Mode Impact:**
  - **No replay** and **failure replay** conditions yield low synthetic holdout gaps (~0.009).
  - **Random replay** yields poor synthetic and transfer performance, likely due to non-informative samples.
  - **Failure replay with compression** leverages replay selectively under compression pressure, achieving best transfer performance.

- **Complexity and Selection Mode:**
  - Replay compression conditions yield higher complexity (0.78) versus no replay/failure replay (0.58).
  - Selection mode "novelty_gate" in failure replay compression correlates with better transfer despite lower accepted epoch count (3 vs 6 in failure replay).

---

### Conclusion

- **Replay-aware methods, especially failure replay combined with compression-aware selection, provide superior transfer to held-out TSPLIB ATSP instances.**
- This transfer improvement comes **despite a moderate reduction in code novelty**, implying that architectural/selection refinements aid transfer beyond mere novelty.
- **Random replay is ineffective** in this context.
- Synthetic holdout optimality gaps favor no replay and failure replay equally, suggesting synthetic benchmarks alone are insufficient proxy for transfer performance.
- Optimality-gap metrics emphasize the **value of failure replay with compression** as the best overall transfer condition.
