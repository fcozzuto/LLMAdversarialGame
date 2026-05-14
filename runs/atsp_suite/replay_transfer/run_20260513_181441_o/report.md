# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay_compression`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_181441_o
- started_at_local: 2026-05-13 18:14:41
- finished_at_local: 2026-05-13 18:23:02
- duration_hhmm: 00:08
- duration_seconds: 500.898
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.192839 | 0.009004 | 0.100922 | 0.844537 | 0.58 | 0.012419 |
| atsp_random_replay | random | score_only | False | 0.192888 | 0.008454 | 0.100671 | 0.910159 | 0.58 | 0.011694 |
| atsp_failure_replay | failure | score_only | False | 0.190811 | 0.009004 | 0.099908 | 0.869649 | 0.58 | 0.018694 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.186239 | 0.030781 | 0.10851 | 0.0 | 0.78 | 0.0 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192839`, synthetic `0.009004`, combined `0.100922`.
- Accepted-epoch count `4`, mean accepted code novelty `0.844537`, and final complexity `0.58`.
- Adaptation efficiency `0.012419` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192839` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.003915, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192888`, synthetic `0.008454`, combined `0.100671`.
- Accepted-epoch count `4`, mean accepted code novelty `0.910159`, and final complexity `0.58`.
- Adaptation efficiency `0.011694` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192888` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004982, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190811`, synthetic `0.009004`, combined `0.099908`.
- Accepted-epoch count `3`, mean accepted code novelty `0.869649`, and final complexity `0.58`.
- Adaptation efficiency `0.018694` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190811` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.186239`, synthetic `0.030781`, combined `0.10851`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.186239` across 4 instances; family means: ft=0.303548, ftv=0.279603, p=0.001423, ry=0.16038.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1973, "family": "ftv", "name": "ftv38", "optimality_gap": 0.289542}, {"best_known_cost": 1286, "cost": 1600, "family": "ftv", "name": "ftv33", "optimality_gap": 0.244168}, {"best_known_cost": 1473, "cost": 1828, "family": "ftv", "name": "ftv35", "optimality_gap": 0.241005}]

## Judge Appendix
### Summary of Results

| Condition                    | Transfer Gap (TSPLIB) | Synthetic Holdout Gap | TSPLIB Gap | Code Novelty (mean) | Complexity | Replay Mode       | Notes                                                                         |
|------------------------------|----------------------|----------------------|------------|---------------------|------------|-------------------|-------------------------------------------------------------------------------|
| **atsp_no_replay**            | 0.1009               | 0.0090               | 0.1928     | 0.8445              | 0.58       | none              | Baseline performance, moderate transfer gap and balanced complexity          |
| **atsp_random_replay**        | 0.1007               | **0.0085**           | 0.1929     | 0.9102 (highest)    | 0.58       | random            | Best synthetic gap (transfer to synthetic data improved), code novelty highest|
| **atsp_failure_replay**       | **0.0999 (best)**    | 0.0090               | **0.1908 (best)** | 0.8696              | 0.58       | failure           | Best transfer gaps (TSPLIB and transfer), lower code novelty than random replay|
| **atsp_failure_replay_compression** | 0.1085 (worst)       | 0.0308 (worst)       | 0.1862 (best) | 0.0 (lowest)        | 0.78 (highest) | failure + compression | Worst transfer and synthetic gaps, lowest code novelty, highest complexity, compression pressure on |

---

### Interpretation

- **Transfer performance (TSPLIB and synthetic holdouts):**  
  - *atsp_failure_replay* condition achieves the **best transfer gaps on TSPLIB (0.1908) and combined transfer measure (0.0999)**, indicating more effective transfer learning across diverse ATSP instances.  
  - *atsp_random_replay* shows the best synthetic holdout gap (0.0085) but slightly worse TSPLIB gap compared to failure replay.  
  - *atsp_failure_replay_compression* performs worse on transfer and synthetic holdouts despite achieving a slightly better TSPLIB gap (0.1862), but with higher complexity and zero code novelty, indicating possible overfitting or stagnation.

- **Code Novelty vs Transfer:**  
  - *atsp_random_replay* maintains the highest average code novelty (~0.91) with similar transfer gap values to baseline no replay, demonstrating that increased lexical novelty does **not** translate to improved transfer gaps.  
  - *atsp_failure_replay* improves transfer while slightly reducing code novelty relative to random replay, suggesting that better transfer is associated with more focused or effective replay (failure-based) rather than raw novelty.  
  - *Compression-aware replay* leads to **lowest code novelty** and worst transfer results, despite higher complexity, implying that compression pressure negatively affects both novelty and transfer.

- **Replay Modes:**  
  - **No replay (baseline)** has modest transfer and novelty.  
  - **Random replay** improves synthetic transfer measure and code novelty but not TSPLIB transfer.  
  - **Failure replay** improves transfer metrics (TSPLIB and transfer gaps) most effectively, supporting targeted replay over random or none.  
  - **Failure replay with compression pressure** degrades transfer and novelty, despite high complexity, indicating complexity increase does not guarantee better performance.

---

### Conservative Conclusions

- The condition **atsp_failure_replay** yields the **best overall transfer performance** (lowest TSPLIB and transfer gaps), validating failure replay as the most effective replay mode to enhance generalization.  
- Improvement in transfer with failure replay occurs **despite a small decrease in code novelty**, indicating that lexical novelty alone does not drive algorithmic improvements in transfer.  
- Random replay increases code novelty but does **not** significantly improve or surpass failure replay in transfer quality.  
- Compression-aware replay suppresses code novelty and harms transfer despite increased complexity, suggesting compression pressure is detrimental under current conditions.  
- No replay baseline performs reasonably but is outperformed by replay-based methods on transfer gaps.

---

### Recommendations

- Prioritize **failure replay** mechanisms to achieve improved transfer to held-out TSPLIB and synthetic ATSP instances.  
- Do not equate higher code novelty or complexity to better transfer unless accompanied by reduced optimality gaps.  
- Avoid compression pressure in failure replay without further tuning due to negative impact on transfer and novelty.  
- Further study is needed to isolate why compression-aware replay increases complexity but harms transfer and novelty.
