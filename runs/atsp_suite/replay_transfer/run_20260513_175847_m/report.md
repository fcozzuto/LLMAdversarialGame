# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_failure_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_failure_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_175847_m
- started_at_local: 2026-05-13 17:58:47
- finished_at_local: 2026-05-13 18:06:17
- duration_hhmm: 00:07
- duration_seconds: 449.849
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.183215 | 0.041579 | 0.112397 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.18982 | 0.008454 | 0.099137 | 0.795527 | 0.58 | 0.013731 |
| atsp_failure_replay | failure | score_only | False | 0.181339 | 0.009004 | 0.095172 | 0.853419 | 0.58 | 0.014278 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193143 | 0.009004 | 0.101074 | 0.813678 | 0.58 | 0.018837 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.183215`, synthetic `0.041579`, combined `0.112397`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.183215` across 4 instances; family means: ft=0.27386, ftv=0.295102, p=0.018149, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1750, "family": "ftv", "name": "ftv33", "optimality_gap": 0.360809}, {"best_known_cost": 1530, "cost": 2042, "family": "ftv", "name": "ftv38", "optimality_gap": 0.334641}, {"best_known_cost": 1473, "cost": 1798, "family": "ftv", "name": "ftv35", "optimality_gap": 0.220638}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.18982`, synthetic `0.008454`, combined `0.099137`.
- Accepted-epoch count `4`, mean accepted code novelty `0.795527`, and final complexity `0.58`.
- Adaptation efficiency `0.013731` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.18982` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.181339`, synthetic `0.009004`, combined `0.095172`.
- Accepted-epoch count `4`, mean accepted code novelty `0.853419`, and final complexity `0.58`.
- Adaptation efficiency `0.014278` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.181339` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.063237.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193143`, synthetic `0.009004`, combined `0.101074`.
- Accepted-epoch count `3`, mean accepted code novelty `0.813678`, and final complexity `0.58`.
- Adaptation efficiency `0.018837` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193143` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.110456.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Results for Replay-Aware ATSP Benchmark Suite

| Condition                      | Replay Mode        | TSPLIB Gap (Heldout) | Synthetic Gap (Holdout) | Transfer Gap (TSPLIB & Synthetic) | Code Novelty (Mean) | Compression Pressure | Notes on Transfer & Novelty                                    |
|-------------------------------|--------------------|---------------------|------------------------|----------------------------------|---------------------|----------------------|---------------------------------------------------------------|
| **atsp_no_replay**             | None               | 0.183215            | 0.041579               | 0.112397                         | 0.0                 | No                   | Baseline transfer performance; no code novelty               |
| **atsp_random_replay**         | Random replay      | 0.18982             | **0.008454 (best synthetic)** | 0.099137                         | 0.796               | No                   | Improved synthetic transfer; code novelty high but no TSPLIB gap improvement |
| **atsp_failure_replay**        | Failure replay     | **0.181339 (best TSPLIB)** | 0.009004               | **0.095172 (best transfer)**    | 0.853               | No                   | Best transfer results; significant code novelty present        |
| **atsp_failure_replay_compression** | Failure replay + Compression | 0.193143            | 0.009004               | 0.101074                         | 0.814               | Yes                  | Slightly worse transfer than failure replay without compression; high code novelty |

---

### Key Interpretations

- **Transfer Metrics Priority**:  
  The main evidence for transfer capability lies in the TSPLIB and synthetic holdout gaps:  
  - *atsp_failure_replay* provides the lowest TSPLIB mean gap (0.181339) and best combined transfer gap (0.095172), marking it as the best overall for meaningful transfer on external benchmarks.  
  - *atsp_random_replay* shows superior performance on synthetic holdout gap (0.008454), but TSPLIB transfer gap is higher (0.099137 vs. 0.095172) and TSPLIB gap is worse (0.18982 vs. 0.181339).  
  - No replay yields worse transfer gaps overall, confirming the benefit of replay.

- **Code Novelty vs. Transfer**:  
  - Both **atsp_random_replay** and **atsp_failure_replay** conditions yield high code novelty (~0.8+), much larger than no replay (0.0).  
  - However, improved code novelty does not guarantee improved TSPLIB gaps since random replay exhibits higher novelty but does not outperform failure replay on TSPLIB benchmarks.  
  - Hence, lexical/code novelty alone does not imply algorithmic invention or better transfer without supporting gap improvements.

- **Replay Modes Distinction**:  
  - **No replay**: baseline, no memory of prior cases, lowest transfer performance.  
  - **Random replay**: improves synthetic gap significantly and code novelty but slightly worsens TSPLIB gap vs. failure replay.  
  - **Failure replay**: prioritized replay of failure cases yields best TSPLIB transfer gaps, better generalization, and high novelty.  
  - **Failure replay + compression**: compression pressure slightly degrades transfer performance compared to failure replay alone, despite high novelty.

- **Compression Pressure Impact**:  
  - Compression-aware failure replay reduces mean transfer efficiency marginally (transfer gap 0.101074 vs. 0.095172 without compression) while maintaining code novelty high. This suggests compression pressure may mildly degrade transfer performance.

---

### Conservative Conclusion

- **Failure replay** condition is the most effective for transfer, based on held-out TSPLIB and synthetic gap metrics, supporting the use of failure memory for replay.  
- **Random replay** improves synthetic holdout gap drastically and code novelty but offers less benefit or slight worsening for TSPLIB transfer gaps.  
- Code novelty increases markedly with replay conditions but does not inherently indicate algorithmic advancement without corroborating improvements in transfer-related metrics.  
- Compression-aware replay does not improve transfer metrics beyond failure replay alone and may slightly hinder it.  
- Rankings for transfer:  
  1. atsp_failure_replay  
  2. atsp_random_replay  
  3. atsp_failure_replay_compression  
  4. atsp_no_replay

---

If prioritizing transfer and optimality gap improvements, **failure replay without compression** should be considered the best strategy among those tested.
