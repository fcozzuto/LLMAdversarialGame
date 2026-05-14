# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_no_replay`.
- Best TSPLIB holdout gap: `tsplib_no_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_131240_d
- started_at_local: 2026-05-13 13:12:40
- finished_at_local: 2026-05-13 13:22:31
- duration_hhmm: 00:10
- duration_seconds: 590.409
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.80218 | 0.56 | -0.031047 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.823575 | 0.56 | -0.03024 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.853124 | 0.56 | -0.029193 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.80218`, and final complexity `0.56`.
- Adaptation efficiency `-0.031047` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.823575`, and final complexity `0.56`.
- Adaptation efficiency `-0.03024` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.853124`, and final complexity `0.56`.
- Adaptation efficiency `-0.029193` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

## Judge Appendix
### Summary of Results for Replay-Aware TSP Benchmark Suite

| Condition                         | Replay Mode            | Selection Mode | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Mean Code Novelty | Compression Pressure | Comment                              |
|----------------------------------|-----------------------|----------------|-----------------|--------------------|-------------------|-------------------|----------------------|------------------------------------|
| **tsplib_no_replay**              | none                  | score_only     | 0.213387        | 0.064916           | 0.159398          | 0.80218           | false                | Best overall transfer and gaps      |
| tsplib_random_replay              | random                | score_only     | 0.213387        | 0.064916           | 0.159398          | 0.823575          | false                | Same gaps as no_replay, higher novelty |
| tsplib_failure_replay             | failure               | score_only     | 0.213387        | 0.064916           | 0.159398          | 0.853124          | false                | Same transfer/gaps, higher novelty  |
| tsplib_failure_replay_compression | failure + compression | novelty_gate   | 0.213387        | 0.064916           | 0.159398          | 0.0               | true                 | Equal gaps but zero code novelty, compression pressure |

---

### Interpretation

- **Transfer Performance (Key metric):**  
  All conditions exhibit identical mean TSPLIB holdout gaps (0.2134), synthetic holdout gaps (0.0649), and transfer gaps (0.1594). This indicates **no measurable difference in transfer ability between replay modes** (no replay, random replay, failure replay, or compression-aware replay).

- **Code Novelty vs Transfer:**  
  Despite identical gaps, conditions with random replay and failure replay show **higher code novelty (~0.82-0.85)** compared to no replay (~0.80) and zero novelty under compression-aware failure replay. Therefore, **code novelty does not correlate with improved transfer or optimality gaps here.**

- **Compression Pressure:**  
  The failure replay with compression mode shows zero code novelty yet no decline in transfer or gap metrics. This suggests the compression impacts code novelty significantly but **without harming final transfer or solution quality**.

- **Replay Mode Impact on Optimality Gap:**  
  No replay achieves the best transfer and holdout gaps, and replay conditions (random or failure) do not improve or degrade these gaps. Compression-aware replay does not affect gaps either.

- **Behavior and Complexity:**  
  Across all conditions, complexity and behavior profiles remain stable (complexity ~0.56, balanced behavior).

---

### Conservative Conclusions

- **Best transfer and gap metrics are achieved under the no replay condition (tsplib_no_replay).**  
- **Replay modes (random or failure) do not improve transfer or reduce optimality gaps despite higher code novelty.**  
- **Compression-aware failure replay removes code novelty but maintains equal transfer and optimality performance.**  
- **Lexical or code novelty increases observed under replay do not correspond to algorithmic improvements in gap or transfer metrics.**  
- **No empirical evidence supports that replay (random or failure) or compression-aware replay improves optimality-gap or transfer beyond no replay baseline in this suite.**
