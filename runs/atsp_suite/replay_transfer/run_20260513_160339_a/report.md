# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_no_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_no_replay`.

## Run Metadata
- run_name: run_20260513_160339_a
- started_at_local: 2026-05-13 16:03:39
- finished_at_local: 2026-05-13 16:15:48
- duration_hhmm: 00:12
- duration_seconds: 729.074
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.190767 | 0.009004 | 0.099886 | 0.0 | 0.5775 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.207155 | 0.030781 | 0.118968 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.207396 | 0.014741 | 0.111069 | 0.809219 | 0.78 | 0.044372 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193143 | 0.009004 | 0.101074 | 0.830791 | 0.58 | 0.012299 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190767`, synthetic `0.009004`, combined `0.099886`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190767` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.003915, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.207155`, synthetic `0.030781`, combined `0.118968`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.207155` across 4 instances; family means: ft=0.307748, ftv=0.292622, p=0.002135, ry=0.226113.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1980, "family": "ftv", "name": "ftv38", "optimality_gap": 0.294118}, {"best_known_cost": 1286, "cost": 1619, "family": "ftv", "name": "ftv33", "optimality_gap": 0.258942}, {"best_known_cost": 1473, "cost": 1756, "family": "ftv", "name": "ftv35", "optimality_gap": 0.192125}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.207396`, synthetic `0.014741`, combined `0.111069`.
- Accepted-epoch count `2`, mean accepted code novelty `0.809219`, and final complexity `0.78`.
- Adaptation efficiency `0.044372` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.207396` across 4 instances; family means: ft=0.321796, ftv=0.358958, p=0.001068, ry=0.14776.
- Panel `synthetic_holdout` mean gap `0.014741` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.040637, wind_clusters=0.018328.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1981, "family": "ftv", "name": "ftv35", "optimality_gap": 0.344874}, {"best_known_cost": 1530, "cost": 2039, "family": "ftv", "name": "ftv38", "optimality_gap": 0.33268}, {"best_known_cost": 1286, "cost": 1629, "family": "ftv", "name": "ftv33", "optimality_gap": 0.266719}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193143`, synthetic `0.009004`, combined `0.101074`.
- Accepted-epoch count `4`, mean accepted code novelty `0.830791`, and final complexity `0.58`.
- Adaptation efficiency `0.012299` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193143` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.110456.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
# Replay-aware ATSP Benchmark Suite Analysis

| Condition                      | Replay Mode             | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer & Novelty                              |
|-------------------------------|------------------------|------------------|---------------------|--------------------|---------------------|------------|----------------------------------------------------------|
| **atsp_no_replay**              | none                   | 0.1908           | 0.0090              | 0.0999             | 0.0                 | 0.58       | Best gaps overall on TSPLIB, synthetic, and transfer; no replay, zero code novelty. |
| **atsp_random_replay**          | random                 | 0.2072           | 0.0308              | 0.1190             | 0.0                 | 0.78       | Transfer and synthetic gaps worse than no-replay; no code novelty improvement despite higher complexity. |
| **atsp_failure_replay**         | failure                | 0.2074           | 0.0147              | 0.1111             | 0.81                | 0.78       | Code novelty increased substantially but transfer (TSPLIB) performance degraded vs. no replay; synthetic gap improved over random replay but not no replay. |
| **atsp_failure_replay_compression** | failure + compression | 0.1931           | 0.0090              | 0.1011             | 0.83                | 0.58       | High code novelty with compression; transfer metrics close to no replay but slight degradation; complexity reduced via compression. |

---

## Interpretation

- **Transfer Performance**:  
  The **no replay** condition shows superior transfer performance as measured by held-out TSPLIB gap (0.1908) and synthetic holdout gap (0.0090), outperforming all replay conditions.

- **Code Novelty vs Transfer**:  
  Conditions employing **failure replay** (with and without compression) yield substantially higher code novelty (mean ~0.81–0.83), but this does **not** translate to improved transfer metrics, which are slightly worse than no replay.

- **Complexity and Compression Effects**:  
  Failure replay with compression maintains high code novelty but reduces complexity (0.58 vs. 0.78), showing that compression pressure can restore complexity levels closer to no replay while preserving novelty. This condition nearly matches no replay in transfer gaps but does not surpass it.

- **Random Replay**:  
  Random replay results in the worst transfer gaps among the conditions, despite zero code novelty and highest complexity (0.78). This suggests random replay may impair transferability.

- **Replay Mode Effects**:  
  - **No replay** (atsp_no_replay) is best for transfer metrics with zero code novelty.  
  - **Failure replay** induces novel code but leads to transfer degradation.  
  - **Random replay** degrades transfer without increasing novelty.  
  - **Compression-aware failure replay** improves complexity but does not fully recover no replay transfer performance.

---

## Summary

- The **no replay** condition achieves the best transfer and synthetic holdout optimality gaps with no increase in code novelty.
- Replay mechanisms (random or failure) increase complexity and/or code novelty but do not improve transfer; often transfer gaps worsen.
- Compression-aware failure replay mitigates complexity growth and closes the transfer gap somewhat but does not surpass no replay.
- Therefore, **higher code novelty through replay does not equate to improved algorithmic transferability** in this benchmark.
- The evidence favors **conservative interpretation** that replay and associated code novelty provide no clear transfer advantage over no replay.
