# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_170341_g
- started_at_local: 2026-05-13 17:03:41
- finished_at_local: 2026-05-13 17:12:35
- duration_hhmm: 00:09
- duration_seconds: 533.825
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.174864 | 0.021916 | 0.09839 | 0.808852 | 0.78 | 0.032243 |
| atsp_random_replay | random | score_only | False | 0.189168 | 0.008454 | 0.098811 | 0.0 | 0.58 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.127101 | 0.041579 | 0.08434 | 0.800347 | 0.78 | 0.030266 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193143 | 0.009004 | 0.101074 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.174864`, synthetic `0.021916`, combined `0.09839`.
- Accepted-epoch count `2`, mean accepted code novelty `0.808852`, and final complexity `0.78`.
- Adaptation efficiency `0.032243` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.174864` across 4 instances; family means: ft=0.287328, ftv=0.226286, p=0.001957, ry=0.183886.
- Panel `synthetic_holdout` mean gap `0.021916` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.069338, wind_clusters=0.018328.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1551, "family": "ftv", "name": "ftv33", "optimality_gap": 0.206065}, {"best_known_cost": 1530, "cost": 1800, "family": "ftv", "name": "ftv38", "optimality_gap": 0.176471}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.189168`, synthetic `0.008454`, combined `0.098811`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.189168` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.127101`, synthetic `0.041579`, combined `0.08434`.
- Accepted-epoch count `3`, mean accepted code novelty `0.800347`, and final complexity `0.78`.
- Adaptation efficiency `0.030266` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.127101` across 4 instances; family means: ft=0.223606, ftv=0.249225, p=0.004093, ry=0.03148.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1979, "family": "ftv", "name": "ftv35", "optimality_gap": 0.343517}, {"best_known_cost": 1286, "cost": 1649, "family": "ftv", "name": "ftv33", "optimality_gap": 0.282271}, {"best_known_cost": 1530, "cost": 1857, "family": "ftv", "name": "ftv38", "optimality_gap": 0.213725}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193143`, synthetic `0.009004`, combined `0.101074`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193143` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.110456.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Replay Conditions on ATSP Benchmark Suite

| Condition                      | Replay Mode        | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty Mean | Complexity | Notes on Transfer and Code Novelty                               |
|-------------------------------|--------------------|-----------------|--------------------|-------------------|-------------------|------------|-----------------------------------------------------------------|
| **atsp_no_replay**             | none               | 0.174864        | 0.021916           | 0.09839           | 0.808852          | 0.78       | Moderate transfer gap; high code novelty; no replay            |
| **atsp_random_replay**         | random             | 0.189168        | **0.008454**       | 0.098811          | 0.0               | 0.58       | Best synthetic holdout gap; transfer gap similar to no replay; no code novelty |
| **atsp_failure_replay**        | failure            | **0.127101**    | 0.041579           | **0.08434**       | 0.800347          | 0.78       | Best overall transfer (TSPLIB + transfer gap) despite higher synthetic gap; high code novelty maintained |
| **atsp_failure_replay_compression** | failure + compression | 0.193143        | 0.009004           | 0.101074          | 0.0               | 0.58       | Worst transfer gaps; compression pressure reduces code novelty and transfer |

---

### Conservative Interpretation

- **Transfer Performance (Main Evidence):**

  - *Held-out TSPLIB Gap* (primary transfer metric): The **atsp_failure_replay** condition achieves the **lowest mean TSPLIB gap (0.1271)**, indicating superior transfer to held-out ATSP instances.
  - *Synthetic Holdout Gap*: **atsp_random_replay** achieves the best synthetic evaluation gap (0.00845), showing strong synthetic holdout optimality but its TSPLIB gap is higher (0.189168).
  - *Mean Transfer Gap* confirms **atsp_failure_replay** is best overall (0.08434), reinforcing confidence in that replay mode for enabling transfer.

- **Code Novelty vs Transfer:**
  
  - The **failure replay without compression** maintains high code novelty (~0.80), similar to no replay (~0.81), yet achieves improved transfer metrics (TSPLIB gap reduced from 0.1749 to 0.1271, a significant gain).
  - **Random replay** and **failure replay with compression** have zero code novelty but show worse or equivalent transfer gaps compared to failure replay without compression.
  - This indicates that **code novelty decreases in random replay and compression-aware replay conditions, while transfer does not improve or even deteriorates in those cases**.
  - Thus, **improved transfer with failure replay occurs alongside maintained code novelty, whereas lowering code novelty (random, compressed replay) does not yield transfer benefits.**

- **Replay Mode Impact:**

  - **No Replay (none):** Acceptable transfer performance with high novelty.
  - **Random Replay:** Best synthetic gap but worse transfer gaps; no code novelty; reduced complexity.
  - **Failure Replay (best_holdout & best_transfer):** Best held-out and transfer performance; moderate synthetic gap; high code novelty; complex behavioral profile.
  - **Failure Replay + Compression:** Worst transfer and TSPLIB performance; minimal novelty; compression pressure likely harms transfer.

- **Complexity and Archive Sizes:**

  - Failure replay conditions show higher complexity (0.78) and larger elite archive (3) compared to random and compressed conditions (0.58 complexity, archive size 1).
  - Compression pressure in failure replay compresses behavior and code novelty, hurting transfer.

---

### Key Takeaways

- **Failure Replay (without compression) maximizes transfer performance to held-out TSPLIB ATSP problems, yielding the lowest optimality gaps in transfer benchmarks.**
- **This improvement in transfer is accompanied by sustained high code novelty and behavioral complexity, not reduced code novelty.**
- **Random replay improves synthetic holdout gap but fails to improve actual transfer (held-out TSPLIB), and shows zero code novelty.**
- **Failure replay with compression reduces code novelty and transfer quality, indicating compression pressure negatively impacts transfer despite replay.**
- **No replay and failure replay both show high code novelty, but failure replay improves transfer metrics clearly.**

---

### Recommendation

- Prioritize **failure replay without compression** for optimal transfer performance in replay-aware ATSP benchmarks.
- Avoid compression-induced novelty gating during failure replay as it detrimentally affects transfer learning.
- Recognize that algorithmic invention (as measured by transfer and performance gains) correlates here with maintained or elevated code novelty rather than lexical novelty reduction.
- Interpret synthetic holdout improvements cautiously and prioritize TSPLIB held-out gaps as main evidence for transfer success.

---

Let me know if you need numerical drilling into individual instance results or deeper analysis of complexity/adaptation.
