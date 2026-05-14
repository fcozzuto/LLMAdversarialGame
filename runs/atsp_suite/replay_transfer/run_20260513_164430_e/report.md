# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_164430_e
- started_at_local: 2026-05-13 16:44:30
- finished_at_local: 2026-05-13 16:52:54
- duration_hhmm: 00:08
- duration_seconds: 504.172
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.164661 | 0.041579 | 0.10312 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.189222 | 0.008454 | 0.098838 | 0.862456 | 0.58 | 0.012982 |
| atsp_failure_replay | failure | score_only | False | 0.193715 | 0.009004 | 0.10136 | 0.846892 | 0.58 | 0.018339 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193715 | 0.009004 | 0.10136 | 0.856054 | 0.58 | 0.018143 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.164661`, synthetic `0.041579`, combined `0.10312`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.164661` across 4 instances; family means: ft=0.246054, ftv=0.272784, p=0.004804, ry=0.135002.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1690, "family": "ftv", "name": "ftv33", "optimality_gap": 0.314152}, {"best_known_cost": 1530, "cost": 1982, "family": "ftv", "name": "ftv38", "optimality_gap": 0.295425}, {"best_known_cost": 1473, "cost": 1840, "family": "ftv", "name": "ftv35", "optimality_gap": 0.249151}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.189222`, synthetic `0.008454`, combined `0.098838`.
- Accepted-epoch count `4`, mean accepted code novelty `0.862456`, and final complexity `0.58`.
- Adaptation efficiency `0.012982` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.189222` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.093884.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `3`, mean accepted code novelty `0.846892`, and final complexity `0.58`.
- Adaptation efficiency `0.018339` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `3`, mean accepted code novelty `0.856054`, and final complexity `0.58`.
- Adaptation efficiency `0.018143` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
```markdown
# Benchmark Suite Interpretation: Replay-aware ATSP

## Summary of Conditions and Key Metrics

| Condition                    | Replay Mode                | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Accepted Epochs |
|------------------------------|----------------------------|-----------------|--------------------|-------------------|---------------------|------------|-----------------|
| atsp_no_replay               | none                       | **0.1647**      | 0.0416             | 0.1031            | 0.0                 | 0.78       | 1               |
| atsp_random_replay           | random                     | 0.1892          | **0.0085**         | **0.0988**        | **0.8625**           | 0.58       | 4               |
| atsp_failure_replay          | failure                    | 0.1937          | 0.0090             | 0.1014            | 0.8469              | 0.58       | 3               |
| atsp_failure_replay_compression | failure + compression aware | 0.1937          | 0.0090             | 0.1014            | 0.8561              | 0.58       | 3               |

## Key Observations

### Transfer & Optimality Gaps

- **Best Transfer Performance:**  
  The atsp_random_replay condition shows the lowest mean transfer gap (0.0988) and best synthetic holdout gap (0.0085), indicating superior transfer compared to others.

- **TSPLIB Performance:**  
  The atsp_no_replay condition performs best on TSPLIB held-out instances with the lowest mean optimality gap of 0.1647, compared to higher gaps (~0.19) under all replay conditions.

- **Replay Impact on Transfer:**  
  Both random replay and failure replay conditions yield improved transfer gaps over no replay (0.0988 / 0.1014 vs. 0.1031), but at the cost of slightly increased TSPLIB gaps.

- **Compression:**  
  The compression-aware failure replay condition shows identical gaps to failure replay without compression, suggesting no degradation or improvement in transfer or optimality gaps due to compression pressure.

### Code Novelty vs Transfer

- Replay conditions (random, failure, failure+compression) have **high code novelty (mean ~0.85-0.86)**, but this does **not correspond to better TSPLIB gaps**; in fact, TSPLIB gaps worsen versus no replay (code novelty 0).

- The **no replay condition maintains zero code novelty but has better TSPLIB transfer**, indicating lexical/code novelty alone does not imply algorithmic invention or improved real-world transfer.

### Complexity and Adaptation

- Replay conditions have **lower complexity (0.58)** compared to no replay (0.78), suggesting simpler final behaviors under replay.

- Adaptation efficiency is near zero for no replay vs small positive (~0.013-0.018) for replay, reflecting some efficiency gain with replay.

## Condition Distinctions

- **No Replay (atsp_no_replay):**  
  Best TSPLIB transfer (optimality gap 0.1647) but worse synthetic and transfer gaps. Zero code novelty. Higher complexity.

- **Random Replay (atsp_random_replay):**  
  Best synthetic and transfer gaps (0.0085 and 0.0988). High code novelty (~0.86). Slightly worse TSPLIB gap (0.1892).

- **Failure Replay (atsp_failure_replay):**  
  Similar transfer gaps as random replay but slightly worse TSPLIB gap (0.1937). High code novelty (~0.85).

- **Failure Replay + Compression (atsp_failure_replay_compression):**  
  Same gaps as failure replay without compression. High code novelty. Compression pressure present with no observed gain.

## Conservative Interpretation

- **Replay improves synthetic and transfer gaps**, indicating better adaptation and generalization on synthetic and transfer probes.

- **TSPLIB held-out gaps worsen with replay**, meaning transfer benefit is dataset dependent and replay may reduce performance on standard TSPLIB benchmarks.

- **Code novelty increases with replay but does not correlate with TSPLIB transfer gains**, implying code novelty signals code diversity rather than algorithmic improvement.

- **Compression-aware replay neither improves nor degrades transfer or optimality compared to failure replay alone**.

## Recommendations

- Prioritize **no replay condition for TSPLIB benchmark scenarios** due to better held-out gaps.

- Employ **random replay for improved transfer and synthetic gap performance**, suitable for synthetic environment adaptation.

- Avoid overinterpreting code novelty as algorithmic novelty without corresponding gains in TSPLIB or synthetic gaps.

- Further investigation needed to understand why replay improves synthetic but not TSPLIB performance.

---

**In summary:**

While replay modes (random and failure) boost transfer and synthetic gap metrics and code novelty, the deterministic TSPLIB benchmark gaps indicate the no replay condition achieves better real-world transfer optimality. Therefore, evidence suggests replay methods help synthetic adaptation but can degrade general TSPLIB transfer performance; code novelty reflects diversification rather than guaranteed innovation. Compression-aware replay adds no significant benefit over standard failure replay.
```
