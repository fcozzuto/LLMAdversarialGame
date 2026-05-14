# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay`.
- Best synthetic holdout gap: `atsp_no_replay`.

## Run Metadata
- run_name: run_20260513_183147_q
- started_at_local: 2026-05-13 18:31:47
- finished_at_local: 2026-05-13 18:40:32
- duration_hhmm: 00:09
- duration_seconds: 525.155
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.183339 | 0.009004 | 0.096172 | 0.901717 | 0.58 | 0.019985 |
| atsp_random_replay | random | score_only | False | 0.188164 | 0.030781 | 0.109473 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.151975 | 0.013889 | 0.082932 | 0.711538 | 0.78 | 0.081453 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193498 | 0.009004 | 0.101251 | 0.858717 | 0.58 | 0.036301 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.183339`, synthetic `0.009004`, combined `0.096172`.
- Accepted-epoch count `3`, mean accepted code novelty `0.901717`, and final complexity `0.58`.
- Adaptation efficiency `0.019985` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.183339` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.003915, ry=0.071419.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.188164`, synthetic `0.030781`, combined `0.109473`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.188164` across 4 instances; family means: ft=0.32281, ftv=0.269684, p=0.014413, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1649, "family": "ftv", "name": "ftv33", "optimality_gap": 0.282271}, {"best_known_cost": 1530, "cost": 1943, "family": "ftv", "name": "ftv38", "optimality_gap": 0.269935}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.151975`, synthetic `0.013889`, combined `0.082932`.
- Accepted-epoch count `2`, mean accepted code novelty `0.711538`, and final complexity `0.78`.
- Adaptation efficiency `0.081453` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.151975` across 4 instances; family means: ft=0.275018, ftv=0.233726, p=0.002847, ry=0.096311.
- Panel `synthetic_holdout` mean gap `0.013889` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.048593, wind_clusters=0.006965.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1551, "family": "ftv", "name": "ftv33", "optimality_gap": 0.206065}, {"best_known_cost": 1530, "cost": 1779, "family": "ftv", "name": "ftv38", "optimality_gap": 0.162745}, {"best_known_cost": 1473, "cost": 1710, "family": "ftv", "name": "ftv35", "optimality_gap": 0.160896}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193498`, synthetic `0.009004`, combined `0.101251`.
- Accepted-epoch count `2`, mean accepted code novelty `0.858717`, and final complexity `0.58`.
- Adaptation efficiency `0.036301` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193498` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Replay-Aware ATSP Benchmark Conditions

| Condition                        | Replay Mode             | TSPLIB Gap | Synthetic Gap | Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer & Novelty       |
|---------------------------------|------------------------|------------|---------------|--------------|---------------------|------------|----------------------------------|
| **atsp_no_replay**               | None                   | 0.183339   | **0.009004**  | 0.096172     | 0.9017              | 0.58       | Best synthetic gap; moderate transfer gap; highest code novelty with no replay.  |
| **atsp_random_replay**           | Random                 | 0.188164   | 0.030781      | 0.109473     | 0.0                 | 0.78       | Worst transfer and synthetic gaps; zero code novelty.  |
| **atsp_failure_replay**          | Failure replay          | **0.151975** | 0.013889    | **0.082932** | 0.7115              | 0.78       | Best TSPLIB and transfer gaps; lower code novelty than no replay but transfer improved.  |
| **atsp_failure_replay_compression** | Failure replay + compression | 0.193498  | 0.009004      | 0.101251     | 0.8587              | 0.58       | Compression reduces complexity and novelty; higher TSPLIB gap than failure replay without compression, transfer gap also higher. |

---

### Key Interpretations

- **Main Transfer Evidence (TSPLIB & synthetic holdout gaps):**  
  - The best **transfer** condition is **atsp_failure_replay** with the lowest TSPLIB gap (0.151975) and lowest transfer gap (0.082932).  
  - **atsp_no_replay** performed best on synthetic holdout data (0.009004 synthetic gap), but TSPLIB gap is higher (0.183339), indicating less transfer robustness.

- **Code Novelty vs. Transfer:**  
  - **No replay** (atsp_no_replay) has the highest code novelty (~0.9) but worse transfer metrics, indicating high lexical novelty without corresponding algorithmic improvements as measured.  
  - **Failure replay** conditions reduce code novelty (~0.71-0.86) but improve transfer, showing a trade-off: transfer improves even as code novelty drops.  
  - **Random replay** yields no code novelty and worse transfer, confirming poor adaptation without targeted replay.

- **Replay Modes and Effects:**  
  - **No replay:** Highest code novelty but suboptimal transfer and TSPLIB gaps.  
  - **Random replay:** Zero novelty and worst transfer performance, suggesting ineffective replay strategy.  
  - **Failure replay:** Best transfer performance, confirming replay focusing on failures aids generalization and transfer.  
  - **Failure replay with compression:** Complexity and code novelty reduced relative to failure replay alone, but transfer and TSPLIB gaps increase slightly, implying compression pressure trades off transfer optimality.

---

### Conservative Conclusions

- Failure replay significantly improves benchmark transfer (TSPLIB and synthetic holdout gaps) compared to no replay or random replay, despite lower code novelty.  
- High code novelty alone (seen in no replay) does not guarantee better transfer, so lexical novelty should not be conflated with algorithmic invention.  
- Random replay and compression-aware replay conditions result in inferior or comparable transfer relative to pure failure replay, indicating the importance of replay type and overhead.  
- Compression-aware replay reduces complexity and novelty but at a small cost to transfer metrics, suggesting a trade-off between compactness and transfer optimality.  

---

### Recommendations for Use

- Prioritize **atsp_failure_replay** for best overall transfer in replay-aware ATSP heuristics.  
- Avoid random replay due to lack of novelty and poor transfer.  
- Consider cost-benefit of compression-aware failure replay if lower complexity is required but note possible transfer loss.  
- Code novelty metrics should be interpreted cautiously and not as proof of algorithmic advancement without corroborating transfer improvements.
