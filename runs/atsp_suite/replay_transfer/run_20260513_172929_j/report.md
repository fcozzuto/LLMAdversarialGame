# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay_compression`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_172929_j
- started_at_local: 2026-05-13 17:29:29
- finished_at_local: 2026-05-13 17:37:55
- duration_hhmm: 00:08
- duration_seconds: 506.097
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.190984 | 0.009004 | 0.099994 | 0.0 | 0.58 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.190037 | 0.008454 | 0.099246 | 0.641642 | 0.58 | 0.017328 |
| atsp_failure_replay | failure | score_only | False | 0.201694 | 0.030781 | 0.116238 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.172666 | 0.030781 | 0.101723 | 0.690932 | 0.78 | 0.020358 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190984`, synthetic `0.009004`, combined `0.099994`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190984` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.003915, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190037`, synthetic `0.008454`, combined `0.099246`.
- Accepted-epoch count `4`, mean accepted code novelty `0.641642`, and final complexity `0.58`.
- Adaptation efficiency `0.017328` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190037` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.201694`, synthetic `0.030781`, combined `0.116238`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.201694` across 4 instances; family means: ft=0.325561, ftv=0.288283, p=0.017438, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1596, "family": "ftv", "name": "ftv33", "optimality_gap": 0.241058}, {"best_known_cost": 1530, "cost": 1896, "family": "ftv", "name": "ftv38", "optimality_gap": 0.239216}, {"best_known_cost": 1473, "cost": 1711, "family": "ftv", "name": "ftv35", "optimality_gap": 0.161575}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.172666`, synthetic `0.030781`, combined `0.101723`.
- Accepted-epoch count `2`, mean accepted code novelty `0.690932`, and final complexity `0.78`.
- Adaptation efficiency `0.020358` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.172666` across 4 instances; family means: ft=0.2895, ftv=0.249225, p=0.000712, ry=0.151227.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1574, "family": "ftv", "name": "ftv33", "optimality_gap": 0.22395}, {"best_known_cost": 1530, "cost": 1850, "family": "ftv", "name": "ftv38", "optimality_gap": 0.20915}, {"best_known_cost": 1473, "cost": 1722, "family": "ftv", "name": "ftv35", "optimality_gap": 0.169043}]

## Judge Appendix
### Summary of Results

| Condition                      | Synthetic Gap | Transfer Gap (held-out TSPLIB & synthetic) | TSPLIB Gap | Code Novelty (mean) | Replay Mode               | Selection Mode  | Complexity | Notes                          |
|-------------------------------|---------------|--------------------------------------------|------------|---------------------|---------------------------|-----------------|------------|--------------------------------|
| atsp_no_replay                | 0.009004      | 0.099994 (transfer)                         | 0.190984   | 0.0                 | none                      | score_only      | 0.58       | Baseline; no replay; lowest code novelty |
| **atsp_random_replay**         | **0.008454**  | **0.099246** (best transfer)                | 0.190037   | 0.641642            | random                    | score_only      | 0.58       | Best transfer and synthetic gap; higher code novelty |
| atsp_failure_replay           | 0.030781      | 0.116238                                   | 0.201694   | 0.0                 | failure                   | score_only      | 0.78       | Worse transfer & synthetic gaps; no code novelty     |
| **atsp_failure_replay_compression** | 0.030781      | 0.101723 (best TSPLIB gap)                   | **0.172666**| 0.690932            | failure + compression     | novelty_gate    | 0.78       | Best TSPLIB gap; code novelty increased; compression active |

---

### Interpretation:

- **Transfer (Held-out TSPLIB & Synthetic) Gap:**
  - *atsp_random_replay* condition yields the best combined transfer gap (0.099246) with slightly improved synthetic gap (0.008454) compared to *no_replay*.
  - *atsp_failure_replay_compression* improves held-out TSPLIB gap substantially (best at 0.172666) over other failure replay and baseline conditions, indicating better transfer to realistic TSPLIB benchmarks.
  - *atsp_failure_replay* alone yields poorer transfer and synthetic gaps than both *random* and *no replay* modes.

- **Code Novelty vs Transfer:**
  - Conditions with replay (*random* and *failure + compression*) show substantial increase in code novelty (~0.64-0.69) compared to zero novelty in *no replay* and *failure replay* without compression.
  - Higher code novelty in failure+compression replay aligns with best TSPLIB gap but not with the best synthetic or combined transfer gaps.
  - The *random replay* condition improves transfer without a reduction in code novelty, showing code novelty and transfer can grow together here.
  - Code novelty alone does not signify algorithmic invention given that transfer gains are marginal or mixed across failure replay settings.

- **Replay Mode Effects:**
  - *Random replay* improves transfer gaps relative to *no replay*, with modest code novelty increase.
  - *Failure replay* without compression degrades transfer and synthetic gap, no code novelty gain.
  - *Failure replay with compression* improves TSPLIB transfer gap relative to failure replay without compression, indicating compression-aware replay aids transfer in failure replay context.
  - Selection mode using *novelty_gate* in failure replay+compression coincides with better TSPLIB transfer despite synthetic gap similar to failure replay alone.

- **Complexity:**
  - Failure replay conditions show higher complexity (0.78) compared to no replay and random replay (0.58), which could imply more complex solutions without consistent improvements in transfer.

---

### Conservative Conclusions:

1. **Transfer Evidence:**
   - The strongest evidence for transfer is found for **atsp_random_replay**, which achieves the best combined synthetic and transfer gap.
   - **Failure replay with compression** achieves the best TSPLIB gap, indicating improved transfer to realistic benchmarks in compression-aware failure replay.

2. **Code Novelty:**
   - Code novelty increases with replay, especially failure replay with compression, but increased code novelty does not always correspond to better transfer (e.g., failure replay alone).
   - Since no replay has zero novelty with acceptable transfer, novelty must be interpreted cautiously without attributing algorithmic invention solely to lexical novelty metrics.

3. **Replay mode impacts:**
   - Random replay positively impacts transfer gaps without increasing model complexity.
   - Failure replay without compression decreases transfer quality, indicating that replay must be coupled with mechanisms (compression, novelty gating) to realize benefits.
   - Compression-aware replay combined with failure replay yields a more favorable TSPLIB gap, showing retrieval strategy and replay conditions affect generalization distinctly on held-out datasets.

4. **Complexity vs Optimality-gap:**
   - Increased complexity under failure replay modes does not guarantee better synthetic or transfer gaps.
   - Compression-aware replay manages to balance complexity and transfer more effectively.

---

### Recommendation:

- Prioritize **random replay** for improved and consistent synthetic and transfer optimality gaps with moderate code novelty and low complexity.
- Consider **failure replay with compression and novelty-gate selection** when best TSPLIB performance is critical.
- Avoid interpreting code novelty increases as algorithmic innovation absent concurrent improvement in deterministic transfer metrics.
- Differ between replay conditions carefully; failure replay alone worsens transfer, but when combined with compression-aware replay, transfer improves notably.
