# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay_compression`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay_compression`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_174704_l
- started_at_local: 2026-05-13 17:47:04
- finished_at_local: 2026-05-13 17:58:46
- duration_hhmm: 00:12
- duration_seconds: 701.816
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.192622 | 0.009004 | 0.100813 | 0.889019 | 0.58 | 0.006947 |
| atsp_random_replay | random | score_only | False | 0.193105 | 0.008454 | 0.100779 | 0.832945 | 0.58 | 0.007474 |
| atsp_failure_replay | failure | score_only | False | 0.191028 | 0.009004 | 0.100016 | 0.843266 | 0.58 | 0.012535 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.139721 | 0.020176 | 0.079949 | 0.731389 | 0.78 | 0.026014 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192622`, synthetic `0.009004`, combined `0.100813`.
- Accepted-epoch count `6`, mean accepted code novelty `0.889019`, and final complexity `0.58`.
- Adaptation efficiency `0.006947` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192622` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.003915, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193105`, synthetic `0.008454`, combined `0.100779`.
- Accepted-epoch count `6`, mean accepted code novelty `0.832945`, and final complexity `0.58`.
- Adaptation efficiency `0.007474` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193105` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.191028`, synthetic `0.009004`, combined `0.100016`.
- Accepted-epoch count `4`, mean accepted code novelty `0.843266`, and final complexity `0.58`.
- Adaptation efficiency `0.012535` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.191028` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.139721`, synthetic `0.020176`, combined `0.079949`.
- Accepted-epoch count `3`, mean accepted code novelty `0.731389`, and final complexity `0.78`.
- Adaptation efficiency `0.026014` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.139721` across 4 instances; family means: ft=0.222448, ftv=0.290763, p=0.000534, ry=0.045139.
- Panel `synthetic_holdout` mean gap `0.020176` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1941, "family": "ftv", "name": "ftv35", "optimality_gap": 0.317719}, {"best_known_cost": 1530, "cost": 1966, "family": "ftv", "name": "ftv38", "optimality_gap": 0.284967}, {"best_known_cost": 1286, "cost": 1505, "family": "ftv", "name": "ftv33", "optimality_gap": 0.170295}]

## Judge Appendix
### Summary of Results for Replay-Aware ATSP Benchmark Suite

| Condition                     | Synthetic Gap | TSPLIB Gap | Transfer Gap | Code Novelty (Mean) | Replay Mode      | Complexity | Notes                                               |
|-------------------------------|--------------|------------|--------------|---------------------|------------------|------------|-----------------------------------------------------|
| **No replay**                 | 0.009004     | 0.192622   | 0.100813     | 0.889               | none             | 0.58       | Highest TSPLIB gap, high code novelty, no replay    |
| **Random replay**             | 0.008454     | 0.193105   | 0.100779     | 0.833               | random           | 0.58       | Similar transfer and TSPLIB gaps to no replay        |
| **Failure replay**            | 0.009004     | 0.191028   | 0.100016     | 0.843               | failure          | 0.58       | Slightly improved transfer gap, similar TSPLIB gap  |
| **Failure replay + compression** | 0.020176     | 0.139721   | 0.079949     | 0.731               | failure + compression | 0.78       | Best TSPLIB (0.1397) and transfer gaps (0.0799); lower code novelty; higher complexity |

---

### Interpretation

- **Transfer evidence prioritization**:
  - The **failure replay + compression** condition shows the **best transfer performance** indicated by the lowest mean held-out TSPLIB gap (0.1397) and transfer gap (0.0799).
  - Synthetic holdout gap is worse in this condition (0.020176 vs ~0.009 in others), but the held-out realistic TSPLIB and holdout transfer gaps are more critical for transfer evaluation and show improvement.
  
- **Replay Mode Effects**:
  - Failure replay conditions (with or without compression) yield **slightly better transfer gaps** than no replay or random replay, which have nearly identical TSPLIB and transfer gaps.
  - Compression pressure combined with failure replay further improves transfer results but at the cost of increased behavioral complexity (0.78 vs 0.58) and reduced code novelty (~0.73 vs ~0.83–0.89).

- **Code Novelty vs Transfer**:
  - Code novelty is highest for no replay (mean ~0.889) and random replay (~0.833), but these do not translate to improved transfer.
  - Transfer improves in failure replay conditions despite a decrease in code novelty indicators.
  - This indicates that the **improvements in transfer do not stem from increased code novelty**, suggesting that **lexical novelty is not aligned with algorithmic invention here**.

- **Complexity and Behavior**:
  - The best performing transfer condition also corresponds to the highest complexity (0.78) and a "clustered_constructor" behavior profile.
  - Other conditions maintain a consistent moderate complexity (0.58) and balanced behavior.

---

### Conclusion

- **Failure replay with compression is the optimal replay-aware strategy to improve transfer performance on held-out TSPLIB ATSP benchmarks.**
- This approach reduces the mean transfer and TSPLIB optimality gaps significantly relative to no replay, random replay, and failure replay without compression.
- The strategy also incurs a moderate increase in complexity and a reduction in code novelty.
- Therefore, **improved transfer comes with diminished code novelty, implying that code novelty is not a reliable proxy for algorithmic transfer performance in this setting.**
- Random replay and no replay conditions exhibit similar transfer gaps and complexity but higher code novelty, indicating less efficient adaptation or informative replay conditioning.

---

### Key Metrics (TSPLIB heldout panel mean optimality gaps):

| Condition                     | TSPLIB Gap |
|------------------------------|------------|
| No replay                    | 0.1926     |
| Random replay                | 0.1931     |
| Failure replay              | 0.1910     |
| Failure replay + compression | 0.1397     |  

---

### Recommendations

- Prioritize **failure replay combined with compression pressure** for improved transfer in ATSP tasks despite increased complexity and lower novelty.
- Do not interpret code novelty metrics as evidence of algorithmic innovation without supportive transfer or optimality improvements.
- Distinguish replay modes carefully as failure replay variants yield better practical transfer even without lexical novelty gains.
