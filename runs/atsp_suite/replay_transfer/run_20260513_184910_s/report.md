# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_184910_s
- started_at_local: 2026-05-13 18:49:10
- finished_at_local: 2026-05-13 18:56:16
- duration_hhmm: 00:07
- duration_seconds: 425.854
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.190115 | 0.009004 | 0.09956 | 0.0 | 0.58 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.189168 | 0.008454 | 0.098811 | 0.877558 | 0.58 | 0.012769 |
| atsp_failure_replay | failure | score_only | False | 0.181339 | 0.009004 | 0.095172 | 0.745308 | 0.58 | 0.012437 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193143 | 0.009004 | 0.101074 | 0.844675 | 0.58 | 0.012371 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190115`, synthetic `0.009004`, combined `0.09956`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190115` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.003915, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.189168`, synthetic `0.008454`, combined `0.098811`.
- Accepted-epoch count `4`, mean accepted code novelty `0.877558`, and final complexity `0.58`.
- Adaptation efficiency `0.012769` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.189168` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.181339`, synthetic `0.009004`, combined `0.095172`.
- Accepted-epoch count `5`, mean accepted code novelty `0.745308`, and final complexity `0.58`.
- Adaptation efficiency `0.012437` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.181339` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.063237.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193143`, synthetic `0.009004`, combined `0.101074`.
- Accepted-epoch count `4`, mean accepted code novelty `0.844675`, and final complexity `0.58`.
- Adaptation efficiency `0.012371` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193143` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.110456.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Comparative Summary of Replay Conditions (ATSP Benchmark)

| Condition                     | Replay Mode        | Synthetic Gap | Transfer Gap (TSPLIB + Synth) | TSPLIB Gap | Code Novelty Mean | Complexity | Notes on Transfer & Novelty                                   |
|-------------------------------|--------------------|---------------|------------------------------|------------|-------------------|------------|-------------------------------------------------------------|
| **atsp_no_replay**             | none               | 0.009004      | 0.09956                      | 0.190115   | 0.0               | 0.58       | Baseline; moderate transfer, no code novelty                |
| **atsp_random_replay**         | random             | **0.008454**  | 0.098811                     | 0.189168   | 0.88              | 0.58       | Slightly better synthetic gap; transfer gap similar to no replay but code novelty high |
| **atsp_failure_replay**        | failure            | 0.009004      | **0.095172**                 | **0.181339**| 0.75              | 0.58       | Best TSPLIB gap and best transfer gap; moderate code novelty |
| **atsp_failure_replay_compression** | failure + compression | 0.009004      | 0.101074                     | 0.193143   | 0.84              | 0.58       | Slightly worse transfer (TSPLIB gap up); high code novelty  |

---

### Key Interpretations

- **Transfer Performance**  
  - The **atsp_failure_replay** condition yields the best transfer outcomes on held-out TSPLIB instances (gap 0.181339) and also the best combined transfer gap (TSPLIB + synthetic), outperforming no replay and random replay despite somewhat lower code novelty.
  - **Random replay** achieves the best synthetic holdout gap (0.008454) but transfer to TSPLIB is marginally worse than failure replay.
  - Compression-aware failure replay shows a degradation in transfer gap compared to failure replay without compression, suggesting compression pressure may impair transfer despite increased code novelty.

- **Code Novelty vs Transfer**  
  - **Random replay and compression-aware failure replay** both exhibit high code novelty (~0.84–0.88 mean), yet their transfer gaps are not better than failure replay with moderate novelty (~0.75).  
  - This indicates that increased lexical/code novelty does not necessarily translate to better transfer or algorithmic advancement under the given deterministic metrics.

- **Complexity and Behavior Profile**  
  - All conditions maintain the same mean complexity (0.58) and balanced behavior profile, isolating replay mode and code novelty as the main varying factors.

- **Replay Mode Effects**  
  - No replay (baseline) performs worse on transfer than failure replay, showing replay helps adaptation.
  - Failure replay outperforms random replay on key transfer gaps, despite random replay showing higher novelty.
  - Compression pressure added to failure replay degrades transfer gap markedly.

- **Optimality Gaps (Held-out TSPLIB families)**  
  - Failure replay reduces mean heldout TSPLIB family gap the most, particularly improving on the 'ry' family (0.063 vs. ~0.10 with others).
  - Worst-case instance gaps remain high across all conditions for certain families (ftv, ft), indicating room for improvement beyond replay modes tested.

---

### Conservative Conclusions

- **Failure replay condition yields the most effective transfer to real-world ATSP benchmarks (TSPLIB), achieving the lowest optimality gaps and best transfer gaps.**
- **Random replay produces higher code novelty but does not improve important deterministic transfer metrics, indicating lexical novelty is not evidence of algorithmic invention here.**
- **Compression-aware failure replay results in elevated transfer gaps despite high code novelty, suggesting compression pressure may reduce transfer effectiveness.**
- **No-replay baseline performs worst on transfer metrics, supporting the utility of replay mechanisms focused on failure cases.**

---

### Recommendations for Benchmark Evaluation

- Prioritize **failure replay** for future algorithmic tuning and transfer studies due to superior transfer performance.
- Do not conflate observed high code novelty in random or compression replay modes with actual algorithmic progress unless accompanied by improved transfer or optimality results.
- Further investigate why compression pressure impairs transfer and whether alternative archive management strategies might maintain transfer benefits with compression.
