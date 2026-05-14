# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_no_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_failure_replay`.

## Run Metadata
- run_name: run_20260513_171236_h
- started_at_local: 2026-05-13 17:12:36
- finished_at_local: 2026-05-13 17:21:04
- duration_hhmm: 00:08
- duration_seconds: 507.918
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.169705 | 0.030781 | 0.100243 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.258493 | 0.037956 | 0.148224 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay | failure | score_only | False | 0.192846 | 0.009004 | 0.100925 | 0.0 | 0.58 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.192846 | 0.009004 | 0.100925 | 0.858717 | 0.58 | 0.036479 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.169705`, synthetic `0.030781`, combined `0.100243`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.169705` across 4 instances; family means: ft=0.228675, ftv=0.292622, p=0.002135, ry=0.155388.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1914, "family": "ftv", "name": "ftv38", "optimality_gap": 0.25098}, {"best_known_cost": 1286, "cost": 1491, "family": "ftv", "name": "ftv33", "optimality_gap": 0.159409}, {"best_known_cost": 1473, "cost": 1690, "family": "ftv", "name": "ftv35", "optimality_gap": 0.147318}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.258493`, synthetic `0.037956`, combined `0.148224`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.258493` across 4 instances; family means: ft=0.447647, ftv=0.398016, p=0.012811, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.037956` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.066212, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1574, "family": "ftv", "name": "ftv33", "optimality_gap": 0.22395}, {"best_known_cost": 1530, "cost": 1827, "family": "ftv", "name": "ftv38", "optimality_gap": 0.194118}, {"best_known_cost": 1473, "cost": 1722, "family": "ftv", "name": "ftv35", "optimality_gap": 0.169043}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192846`, synthetic `0.009004`, combined `0.100925`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192846` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.192846`, synthetic `0.009004`, combined `0.100925`.
- Accepted-epoch count `2`, mean accepted code novelty `0.858717`, and final complexity `0.58`.
- Adaptation efficiency `0.036479` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192846` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Results for Replay-Aware ATSP Benchmark Suite

| Condition                   | Synthetic Gap | TSPLIB Gap | Transfer Gap | Replay Mode          | Complexity | Code Novelty | Notes on Transfer and Novelty                        |
|-----------------------------|---------------|------------|--------------|----------------------|------------|--------------|-----------------------------------------------------|
| **atsp_no_replay** (best holdout & transfer) | 0.0308       | 0.1697     | 0.1002       | none                 | 0.78       | 0.0          | Best transfer to held-out TSPLIB and synthetic; no code novelty observed. |
| **atsp_failure_replay** (best synthetic) | 0.0090       | 0.1928     | 0.1009       | failure              | 0.58       | 0.0          | Best synthetic gap (holdout synthetic close to zero); transfer gap slightly worse than no_replay. |
| **atsp_failure_replay_compression** | 0.0090       | 0.1928     | 0.1009       | failure + compression | 0.58       | 0.86         | Same transfer and gaps as failure_replay but elevated code novelty and compression pressure present. |
| **atsp_random_replay**        | 0.0380       | 0.2585     | 0.1482       | random               | 0.78       | 0.0          | Worst transfer and TSPLIB gaps; no code novelty observed. |

---

### Interpretation

1. **Held-Out TSPLIB ATSP Gap & Transfer Evidence (Primary Metrics):**
   - The **no replay** (atsp_no_replay) condition yields the **lowest mean TSPLIB gap (0.1697)** and best transfer gap (0.1002), indicating superior generalization to real-world TSPLIB instances.
   - Both **failure replay conditions** (with and without compression) have slightly higher TSPLIB gaps (~0.193) and similar transfer gaps (~0.101), slightly worse than no replay.
   - **Random replay** performs worst on TSPLIB (0.2585) and transfer gaps (0.1482), showing degradation from replaying indiscriminately.

2. **Synthetic Holdout Gap:**
   - Failure replay (both standard and compression-aware) achieves the lowest synthetic holdout gaps (~0.009), substantially better than no replay (0.031) or random replay (0.038), demonstrating clear synthetic domain improvement with failure replay.
   - This suggests failure replay promotes more specialized adaption to synthetic distributions.

3. **Code Novelty vs. Transfer:**
   - **No replay, random replay, and failure replay (standard) conditions have zero code novelty.**
   - **Failure replay compression condition exhibits high code novelty (mean ~0.86).** However, this does not improve transfer or TSPLIB performance over standard failure replay.
   - Hence, **increased code novelty due to compression pressure does not translate into better transfer** metrics.
   - This indicates that lexical/code novelty here is not synonymous with algorithmic innovation in transfer performance.

4. **Replay Mode Effects:**
   - **No replay yields best transfer and TSPLIB performance, despite zero adaptation efficiency and code novelty.**
   - **Failure replay improves synthetic holdout gap strongly, with comparable transfer to no replay, but no code novelty.**
   - **Random replay harms transfer and TSPLIB gaps, suggesting naive replay can be detrimental.**
   - **Compression-aware failure replay increases code novelty and adaptation efficiency slightly but does not improve transfer or TSPLIB gap relative to failure replay without compression.**

5. **Complexity:**
   - Failure replay (with/without compression) conditions have lower mean complexity (0.58) compared to no replay and random replay (0.78). 
   - Lower complexity with similar or slightly worse TSPLIB gaps may indicate more streamlined strategies under failure replay.

---

### Conclusions

- **For transfer (TSPLIB and synthetic holdout), no replay yields the best held-out transfer gap and TSPLIB gap**; thus, replay is not strictly necessary or beneficial for transfer in this benchmark.
- **Failure replay significantly improves synthetic holdout gaps but does not improve (may slightly degrade) transfer on held-out TSPLIB problems compared to no replay.**
- **Random replay consistently harms performance.**
- **Compression-aware failure replay increases code novelty substantially but without corresponding transfer gains over failure replay without compression, indicating novelty here is not algorithmically advantageous transfer-wise.**
- Overall, prioritize **no replay** for best transfer generalization and **failure replay** for synthetic holdout accuracy; be cautious of indiscriminate or random replay harms.
- Lexical/code novelty increases under compression-aware replay, but this is not supported by deterministic transfer metrics as algorithmic invention.

---

**Recommendation:**

Focus on no replay or targeted failure replay adaptations for robust transfer in ATSP benchmarks, and treat code novelty gains under compression with skepticism unless accompanied by lowered transfer or TSPLIB gaps.
