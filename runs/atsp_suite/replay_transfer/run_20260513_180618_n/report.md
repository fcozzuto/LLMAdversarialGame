# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_random_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_180618_n
- started_at_local: 2026-05-13 18:06:18
- finished_at_local: 2026-05-13 18:14:40
- duration_hhmm: 00:08
- duration_seconds: 502.447
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.183122 | 0.009004 | 0.096063 | 0.884931 | 0.58 | 0.00821 |
| atsp_random_replay | random | score_only | False | 0.178271 | 0.008418 | 0.093345 | 0.835038 | 0.78 | 0.063932 |
| atsp_failure_replay | failure | score_only | False | 0.210045 | 0.036251 | 0.123148 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193715 | 0.009004 | 0.10136 | 0.750877 | 0.58 | 0.020222 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.183122`, synthetic `0.009004`, combined `0.096063`.
- Accepted-epoch count `6`, mean accepted code novelty `0.884931`, and final complexity `0.58`.
- Adaptation efficiency `0.00821` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.183122` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.003915, ry=0.071419.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.178271`, synthetic `0.008418`, combined `0.093345`.
- Accepted-epoch count `2`, mean accepted code novelty `0.835038`, and final complexity `0.78`.
- Adaptation efficiency `0.063932` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.178271` across 4 instances; family means: ft=0.28979, ftv=0.256045, p=0.012278, ry=0.154972.
- Panel `synthetic_holdout` mean gap `0.008418` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.015345, wind_clusters=0.018328.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 2006, "family": "ftv", "name": "ftv38", "optimality_gap": 0.311111}, {"best_known_cost": 1286, "cost": 1578, "family": "ftv", "name": "ftv33", "optimality_gap": 0.227061}, {"best_known_cost": 1473, "cost": 1765, "family": "ftv", "name": "ftv35", "optimality_gap": 0.198235}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.210045`, synthetic `0.036251`, combined `0.123148`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.210045` across 4 instances; family means: ft=0.4, ftv=0.286423, p=0.008007, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.036251` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.059392, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1841, "family": "ftv", "name": "ftv35", "optimality_gap": 0.24983}, {"best_known_cost": 1530, "cost": 1869, "family": "ftv", "name": "ftv38", "optimality_gap": 0.221569}, {"best_known_cost": 1286, "cost": 1542, "family": "ftv", "name": "ftv33", "optimality_gap": 0.199067}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `3`, mean accepted code novelty `0.750877`, and final complexity `0.58`.
- Adaptation efficiency `0.020222` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
```markdown
### Summary of ATSP Benchmark Replay Conditions

| Condition                    | Replay Mode      | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer and Novelty                        |
|------------------------------|-----------------|-----------------|--------------------|-------------------|---------------------|------------|----------------------------------------------------|
| **atsp_no_replay**            | none            | 0.1831          | 0.0090             | 0.0961            | 0.885               | 0.58       | Baseline transfer moderate; highest code novelty. |
| **atsp_random_replay**        | random          | **0.1783**      | **0.0084**         | **0.0933**        | 0.835               | 0.78       | Best transfer results; slight decrease in code novelty but better gaps. |
| **atsp_failure_replay**       | failure         | 0.2100          | 0.0363             | 0.1231            | 0.0                 | 0.78       | Poorest transfer and synthetic gaps; zero code novelty. |
| **atsp_failure_replay_compression** | failure + compression | 0.1937          | 0.0090             | 0.1014            | 0.751               | 0.58       | Moderate transfer; lower code novelty vs no replay. Compression pressure applied. |

---

### Interpretation

- **Transfer Performance (TSPLIB & Synthetic Gaps):**  
  The **random replay** condition (`atsp_random_replay`) yields the best transfer results on both held-out TSPLIB (~0.178) and synthetic datasets (~0.0084), outperforming no replay and failure replay variants. The improvement is moderate but consistent, indicative of better generalization.  

- **Failure Replay Conditions:**  
  Both failure replay modes yield worse transfer performance, with the no-compression variant showing the highest TSPLIB gap (0.210) and synthetic gap (0.0363), indicating that focusing replay on failure cases does not promote better transfer here. Compression-aware failure replay slightly improves transfer but remains worse than random replay and no replay.

- **Code Novelty vs Transfer:**  
  Code novelty decreases notably in failure replay conditions, especially with failure replay alone (0), indicating little to no algorithmic exploration or invention. Conversely, random replay reduces novelty slightly compared to no replay (0.835 vs 0.885), but this is accompanied by improved transfer gaps. Thus, **code novelty is not necessarily indicative of better transfer**, and the best-performing condition trades off some novelty for improved optimality.

- **Replay Mode Impact:**  
  - **No replay ("none")**: moderate transfer, highest code novelty.  
  - **Random replay**: best transfer, slightly reduced novelty, increased complexity (0.78 vs 0.58).  
  - **Failure replay**: worst transfer, zero/low novelty.  
  - **Failure + compression replay**: intermediate transfer and novelty, complexity lower than random replay.

- **Complexity:**  
  Random replay yields higher complexity (0.78), which might contribute to improved results despite lower novelty. Failure replay variants maintain similar complexity but fail in transfer performance.

---

### Conclusion

- **Random replay enables the best transfer to held-out TSPLIB and synthetic ATSP benchmarks, achieving improved optimality gaps despite a modest reduction in code novelty compared to no replay.**  
- **Failure replay strategies degrade transfer performance, with notably zero code novelty in failure replay without compression, indicating little algorithmic innovation.**  
- **Compression-aware failure replay somewhat mitigates failure replay's negative impact but remains inferior to random replay in transfer.**  
- **The gains in transfer under random replay likely arise from beneficial replay diversity rather than new algorithmic constructs, as code novelty declines somewhat despite improved gaps.**  
- **Prioritize random replay for improved generalization to diverse benchmarks, acknowledging a trade-off with code novelty but clear benefits in optimality gaps.**
```
