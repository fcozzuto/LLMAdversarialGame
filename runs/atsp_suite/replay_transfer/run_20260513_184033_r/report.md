# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay_compression`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay_compression`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_184033_r
- started_at_local: 2026-05-13 18:40:33
- finished_at_local: 2026-05-13 18:49:09
- duration_hhmm: 00:09
- duration_seconds: 516.817
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.212881 | 0.02698 | 0.11993 | 0.699104 | 0.78 | 0.022781 |
| atsp_random_replay | random | score_only | False | 0.193105 | 0.008454 | 0.100779 | 0.0 | 0.58 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.202334 | 0.034191 | 0.118263 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.150416 | 0.041579 | 0.095997 | 0.0 | 0.78 | 0.0 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.212881`, synthetic `0.02698`, combined `0.11993`.
- Accepted-epoch count `2`, mean accepted code novelty `0.699104`, and final complexity `0.78`.
- Adaptation efficiency `0.022781` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.212881` across 4 instances; family means: ft=0.278349, ftv=0.345939, p=0.003203, ry=0.224033.
- Panel `synthetic_holdout` mean gap `0.02698` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.041205, wind_clusters=0.066716.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1607, "family": "ftv", "name": "ftv33", "optimality_gap": 0.249611}, {"best_known_cost": 1473, "cost": 1821, "family": "ftv", "name": "ftv35", "optimality_gap": 0.236253}, {"best_known_cost": 1530, "cost": 1842, "family": "ftv", "name": "ftv38", "optimality_gap": 0.203922}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193105`, synthetic `0.008454`, combined `0.100779`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193105` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.202334`, synthetic `0.034191`, combined `0.118263`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.202334` across 4 instances; family means: ft=0.425923, ftv=0.270304, p=0.000712, ry=0.112398.
- Panel `synthetic_holdout` mean gap `0.034191` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.051151, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1640, "family": "ftv", "name": "ftv33", "optimality_gap": 0.275272}, {"best_known_cost": 1530, "cost": 1863, "family": "ftv", "name": "ftv38", "optimality_gap": 0.217647}, {"best_known_cost": 1473, "cost": 1758, "family": "ftv", "name": "ftv35", "optimality_gap": 0.193483}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.150416`, synthetic `0.041579`, combined `0.095997`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.150416` across 4 instances; family means: ft=0.203765, ftv=0.295102, p=0.001423, ry=0.101373.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1943, "family": "ftv", "name": "ftv35", "optimality_gap": 0.319077}, {"best_known_cost": 1286, "cost": 1649, "family": "ftv", "name": "ftv33", "optimality_gap": 0.282271}, {"best_known_cost": 1530, "cost": 1857, "family": "ftv", "name": "ftv38", "optimality_gap": 0.213725}]

## Judge Appendix
### Summary of Results by Replay Condition

| Condition                      | Replay Mode    | Compression Pressure | TSPLIB Gap (mean) | Synthetic Gap (mean) | Transfer Gap (mean) | Code Novelty (mean) | Complexity (mean) |
|-------------------------------|----------------|---------------------|-------------------|---------------------|---------------------|---------------------|-------------------|
| **atsp_no_replay**             | None           | No                  | 0.2129            | 0.0270              | 0.1199              | 0.6991              | 0.78              |
| **atsp_random_replay**         | Random         | No                  | 0.1931            | **0.0085**          | 0.1008              | 0                   | 0.58              |
| **atsp_failure_replay**        | Failure        | No                  | 0.2023            | 0.0342              | 0.1183              | 0                   | 0.78              |
| **atsp_failure_replay_compression** | Failure + Compression | Yes                 | **0.1504**         | 0.0416              | **0.0960**          | 0                   | 0.78              |

---

### Interpretation

- **Main Transfer Metrics** (held-out TSPLIB and synthetic gaps):
  - The **lowest mean TSPLIB gap (0.1504) and transfer gap (0.0960)** occur under the **atsp_failure_replay_compression** condition.
  - Synthetic holdout gap is best under **atsp_random_replay** (0.0085), but transfer gaps are slightly worse than failure replay with compression.
  - **No replay** has higher TSPLIB and transfer gaps despite high code novelty, indicating that code novelty does not translate to better transfer.
  - Pure **failure replay without compression** shows modest improvements over no replay but worse than failure replay with compression.

- **Code Novelty vs Transfer:**
  - Code novelty is **high only in no replay** (around 0.7), but this coincides with **worst TSPLIB and transfer gaps**.
  - All replay conditions with replay (random, failure, failure+compression) have **zero code novelty**, indicating no new synthetic structural variation introduced.
  - Despite zero code novelty, failure replay with compression outperforms others in transfer metrics, suggesting that improved transfer is achieved through replay mechanisms rather than new code innovation.

- **Effect of Replay Modes:**
  - **No replay:** High code novelty but poor transfer and TSPLIB performance.
  - **Random replay:** Best synthetic holdout gap, moderate transfer and TSPLIB gaps, no code novelty.
  - **Failure replay:** Slightly worse than random replay for synthetic and TSPLIB gaps, no code novelty.
  - **Failure replay + compression:** Best transfer and TSPLIB performance, highest complexity (same as other failure replay), no code novelty.

- **Complexity and Archive Sizes:**
  - All conditions maintain similar archive sizes (11 total), with similar distribution among adversarial, failure, worst cases.
  - Complexity is highest (0.78) in no replay and failure replay variants, lowest (0.58) in random replay.
  - Compression pressure is only applied in failure replay with compression.

---

### Conditional Ranking by Transfer (TSPLIB held-out gap prioritized)

1. **atsp_failure_replay_compression:** Best transfer and held-out TSPLIB gap (0.0960, 0.1504), no code novelty.
2. **atsp_random_replay:** Second best transfer (0.1008), best synthetic holdout gap (0.0085), no code novelty.
3. **atsp_failure_replay:** Moderate transfer (0.1183), higher TSPLIB gap (0.2023), no code novelty.
4. **atsp_no_replay:** Worst transfer (0.1199) and TSPLIB gap (0.2129), highest code novelty (0.6991).

---

### Conclusions

- **Replay improves transfer metrics compared to no replay**, with **failure replay combined with compression yielding the best held-out TSPLIB and transfer gaps**.
- This improvement occurs **despite zero code novelty**, meaning replay mechanisms and compression, rather than algorithmic innovation, drive generalization gains.
- **Random replay achieves the best synthetic holdout gap but slightly worse transfer**, indicating synthetic performance does not always translate to transfer.
- **No replay condition's high code novelty does not correspond to better transfer or TSPLIB performance**, suggesting code novelty here reflects non-effective exploration.
- Distinguishing replay modes is critical: **failure replay with compression is superior to failure replay alone** and both surpass no replay.
- Prioritize **atsp_failure_replay_compression** condition for best evidence of transfer improvement.

---

### Key Metrics for Best Transfer Condition (atsp_failure_replay_compression)

- TSPLIB gap: 0.1504 (best)
- Transfer gap: 0.0960 (best)
- Synthetic gap: 0.0416 (worst among replay, but acceptable)
- Code novelty: 0 (lowest)
- Complexity: 0.78 (high)
- Replay mode: failure replay + compression pressure enabled

---

This conservative interpretation focuses on transfer gaps and shows that replay (especially failure replay with compression) enhances generalization despite no accompanying code novelty increase.
