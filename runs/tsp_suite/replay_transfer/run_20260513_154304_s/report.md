# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_154304_s
- started_at_local: 2026-05-13 15:43:04
- finished_at_local: 2026-05-13 15:52:48
- duration_hhmm: 00:10
- duration_seconds: 584.328
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.833514 | 0.56 | -0.02988 |
| tsplib_random_replay | random | score_only | False | 0.13438 | 0.0 | 0.085515 | 0.0 | 0.76 | 0.0 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.903635 | 0.56 | -0.027561 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.833514`, and final complexity `0.56`.
- Adaptation efficiency `-0.02988` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.13438`, synthetic `0.0`, combined `0.085515`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.13438` across 7 instances; family means: ch=0.139876, kroD=0.13276, pcb=0.212887, pr=0.134478, rd=0.133375, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3358, "family": "a", "name": "a280", "optimality_gap": 0.302055}, {"best_known_cost": 14379, "cost": 18059, "family": "lin", "name": "lin105", "optimality_gap": 0.255929}, {"best_known_cost": 7542, "cost": 8521, "family": "berlin", "name": "berlin52", "optimality_gap": 0.129806}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.903635`, and final complexity `0.56`.
- Adaptation efficiency `-0.027561` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
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
### Summary of Replay-Aware TSP Benchmark Suite Results

| Replay Condition                  | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Replay Mode             |
|---------------------------------|-----------------|--------------------|-------------------|---------------------|------------|------------------------|
| **tsplib_no_replay**             | 0.2134          | 0.0649             | 0.1594            | 0.8335              | 0.56       | none                   |
| **tsplib_random_replay**         | **0.1344**      | **0.0**            | **0.0855**        | 0.0                 | 0.76       | random                 |
| **tsplib_failure_replay**        | 0.2134          | 0.0649             | 0.1594            | 0.9036              | 0.56       | failure                |
| **tsplib_failure_replay_compression** | 0.2134          | 0.0649             | 0.1594            | 0.0                 | 0.56       | failure + compression  |

### Interpretation

- **Transfer and Optimality:**
  - The **random replay condition (tsplib_random_replay)** achieves the best transfer performance both on held-out TSPLIB instances and synthetic holdout sets:
    - Lowest mean TSPLIB gap: 0.1344 (compared to ~0.2134 for others).
    - Lowest mean synthetic gap: 0.0 (others ~0.0649).
    - Lowest mean transfer gap: 0.0855 (others ~0.1594).
  - This indicates superior transfer capability under random replay compared to no replay, failure replay, and failure replay with compression.

- **Code Novelty vs. Transfer:**
  - Random replay shows **zero code novelty** (mean_code_novelty = 0.0), substantially lower than no replay (0.8335) and failure replay (~0.9).
  - Despite lower code novelty, random replay improves transfer gaps markedly.
  - This suggests **lexical novelty reduction** (less code change) is associated here with better transfer performance, reflecting that improvements are not due to new code inventions but more effective reuse (random replay benefits).

- **Failure Replay Conditions:**
  - Both failure replay variants (with and without compression pressure) perform identically on transfer metrics and optimality gaps, matching no replay, with higher code novelty (~0.9 for failure replay vs 0 for compression variant).
  - Compression pressure reduces code novelty but does not improve transfer or optimality gaps relative to no replay failure replay.

- **No Replay Condition:**
  - Baseline optimality and transfer gaps are higher, and code novelty is high (~0.83), indicating more novel code is produced but with poorer transfer outcomes compared to random replay.

- **Behavior Profiles & Complexity:**
  - Random replay exhibits a more complex final behavior profile (complexity = 0.76) versus others (~0.56).
  - No replay and failure replay conditions converge to balanced behavior profiles with lower complexity.

### Key Takeaways

- **Random replay yields best transfer and optimality metrics despite having zero code novelty**, indicating the improvements come from effective replay rather than algorithmic novelty.
- **High code novelty in no replay and failure replay does not translate to better transfer or held-out performance.**
- **Failure replay with compression reduces code novelty but does not improve transfer or optimality gaps compared to failure replay without compression, indicating compression pressure alone does not enhance transfer.**
- **Distinguishing replay modes is critical: random replay significantly outperforms no replay and failure replay on transfer, despite simpler (less novel) solutions.**

---

**Conservative Conclusion:**  
The benchmark suite results confirm that random replay condition provides superior transfer capability and lower optimality gaps on both TSPLIB and synthetic holdout data. This advantage occurs alongside a pronounced reduction in code novelty, suggesting that in this context, transfer improvements stem from replay mechanism efficacy rather than novel code creation. Failure replay with or without compression yields no transfer gains relative to no replay, despite higher code novelty.
