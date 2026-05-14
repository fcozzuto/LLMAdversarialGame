# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_173756_k
- started_at_local: 2026-05-13 17:37:56
- finished_at_local: 2026-05-13 17:47:03
- duration_hhmm: 00:09
- duration_seconds: 547.084
- seed_offset: 10000
- replicate_label: k
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.18892 | 0.03547 | 0.112195 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.189222 | 0.008454 | 0.098838 | 0.855891 | 0.58 | 0.009659 |
| atsp_failure_replay | failure | score_only | False | 0.193715 | 0.009004 | 0.10136 | 0.839307 | 0.58 | 0.007402 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193715 | 0.009004 | 0.10136 | 0.900851 | 0.58 | 0.017241 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.18892`, synthetic `0.03547`, combined `0.112195`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.18892` across 4 instances; family means: ft=0.32281, ftv=0.269684, p=0.017438, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.03547` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.056266, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1857, "family": "ftv", "name": "ftv38", "optimality_gap": 0.213725}, {"best_known_cost": 1286, "cost": 1560, "family": "ftv", "name": "ftv33", "optimality_gap": 0.213064}, {"best_known_cost": 1473, "cost": 1720, "family": "ftv", "name": "ftv35", "optimality_gap": 0.167685}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.189222`, synthetic `0.008454`, combined `0.098838`.
- Accepted-epoch count `5`, mean accepted code novelty `0.855891`, and final complexity `0.58`.
- Adaptation efficiency `0.009659` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.189222` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.093884.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `6`, mean accepted code novelty `0.839307`, and final complexity `0.58`.
- Adaptation efficiency `0.007402` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `3`, mean accepted code novelty `0.900851`, and final complexity `0.58`.
- Adaptation efficiency `0.017241` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Main Evidence (Held-out TSPLIB and Synthetic Gaps)

| Condition                     | Replay Mode          | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (Mean) | Complexity | Notes on Replay |
|-------------------------------|---------------------|-----------------|--------------------|-------------------|---------------------|------------|----------------|
| **atsp_no_replay**             | None                | 0.18892         | 0.03547            | 0.112195          | 0.0                 | 0.78       | No replay       |
| **atsp_random_replay**         | Random replay       | 0.189222        | **0.008454**       | **0.098838**      | 0.855891            | 0.58       | Random replay   |
| **atsp_failure_replay**        | Failure replay      | 0.193715        | 0.009004           | 0.10136           | 0.839307            | 0.58       | Failure replay  |
| **atsp_failure_replay_compression** | Failure replay + compression | 0.193715        | 0.009004           | 0.10136           | 0.900851            | 0.58       | Failure + compression |

---

### Interpretation

- **Best Holdout TSPLIB Optimality Gap:**  
  - Achieved by **atsp_no_replay** (0.18892), narrowly better than replay modes (0.1892-0.1937 range).  
  - Suggests no replay yields slightly better TSPLIB benchmark results.

- **Best Synthetic Holdout and Transfer Optimality Gap:**  
  - **atsp_random_replay** produces the best synthetic holdout gap (0.008454) and lowest transfer gap (0.098838), outperforming no replay and failure replay conditions.  
  - Indicates improved transfer capability on synthetic and related test domains when using random replay.

- **Code Novelty vs Transfer:**  
  - Code novelty is near zero for no replay but substantially higher (around 0.85-0.90) for all replay modes.  
  - Despite increased code novelty with replay, transfer and TSPLIB performance do not improve in held-out TSPLIB gaps (slightly worse or comparable).  
  - Thus, increased code novelty from replay does **not** translate to improved held-out TSPLIB performance, but correspond to better synthetic and transfer gaps.

- **Replay Mode Differences:**  
  - Random replay leads to the best transfer and synthetic gap metrics, outperforming failure replay and failure replay + compression.  
  - Failure replay with compression does not yield measurable transfer improvements over failure replay without compression (identical gap results).  
  - Complexity is lower for replay modes (~0.58) than no replay (~0.78), potentially indicating simpler or more consistent learned behavior with replay.

- **Optimality Gap Details:**  
  - On held-out TSPLIB, all replay modes show worse gaps on difficult families (ft, ftv) compared to no replay.  
  - For synthetic holdout, replay modes achieve zero gaps on some families and very low on others, supporting better synthetic generalization.

---

### Conservative Summary

- **No replay provides the best held-out TSPLIB benchmark optimality gap (0.18892), indicating stronger performance on classical TSPLIB instances without replay.**  
- **Random replay improves synthetic holdout and overall transfer gaps significantly (approx. 0.00845 synthetic, 0.099 transfer) compared to no replay, demonstrating superior adaptability to synthetic test distributions.**  
- **Increased code novelty correlates with replay but does not improve (and may slightly degrade) optimality on held-out TSPLIB, cautioning against equating lexical novelty with algorithmic invention.**  
- **Failure replay and failure replay with compression do not outperform random replay in transfer or hold-out gaps, nor does compression pressure improve transfer, suggesting limited benefit of compression-aware replay here.**

---

### Key Takeaway

- While replay (especially random replay) enhances transfer performance to synthetic domains, it comes with no TSPLIB optimality gap gains and incurs greater code novelty without proven invention. No replay yields slightly better classical benchmark results, implying transfer improvements must be weighed against potential TSPLIB performance and algorithmic novelty.
