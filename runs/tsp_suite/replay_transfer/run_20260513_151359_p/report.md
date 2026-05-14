# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_151359_p
- started_at_local: 2026-05-13 15:13:59
- finished_at_local: 2026-05-13 15:23:39
- duration_hhmm: 00:10
- duration_seconds: 580.448
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.885473 | 0.56 | -0.028126 |
| tsplib_random_replay | random | score_only | False | 0.090684 | 0.0 | 0.057708 | 0.764056 | 0.76 | 0.043614 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.907154 | 0.56 | -0.027454 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.256667 | 0.015447 | 0.168951 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.885473`, and final complexity `0.56`.
- Adaptation efficiency `-0.028126` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.090684`, synthetic `0.0`, combined `0.057708`.
- Accepted-epoch count `3`, mean accepted code novelty `0.764056`, and final complexity `0.76`.
- Adaptation efficiency `0.043614` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.090684` across 7 instances; family means: ch=0.065127, kroD=0.074105, pcb=0.173796, pr=0.094805, rd=0.083312, st=0.078519.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3494, "family": "a", "name": "a280", "optimality_gap": 0.354789}, {"best_known_cost": 629, "cost": 766, "family": "eil", "name": "eil101", "optimality_gap": 0.217806}, {"best_known_cost": 7542, "cost": 9052, "family": "berlin", "name": "berlin52", "optimality_gap": 0.200212}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.907154`, and final complexity `0.56`.
- Adaptation efficiency `-0.027454` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.256667`, synthetic `0.015447`, combined `0.168951`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.256667` across 7 instances; family means: ch=0.22979, kroD=0.380389, pcb=0.249104, pr=0.299365, rd=0.224526, st=0.183704.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 20134, "family": "lin", "name": "lin105", "optimality_gap": 0.400236}, {"best_known_cost": 2579, "cost": 3528, "family": "a", "name": "a280", "optimality_gap": 0.367972}, {"best_known_cost": 7542, "cost": 9793, "family": "berlin", "name": "berlin52", "optimality_gap": 0.298462}]

## Judge Appendix
### Summary of Main Findings on Replay Conditions in TSPLIB Transfer

| Condition                         | Synthetic Gap | Holdout TSPLIB Gap | Transfer Gap | Code Novelty (mean) | Replay Mode               | Complexity | Notes                                                                                          |
|----------------------------------|---------------|--------------------|--------------|---------------------|---------------------------|------------|------------------------------------------------------------------------------------------------|
| **tsplib_random_replay**          | **0.000**     | **0.0907**         | **0.0577**   | 0.764               | Random replay             | 0.76       | Best transfer performance and lowest gaps. Code novelty decreased compared to no replay, but transfer improved significantly. |
| tsplib_no_replay                 | 0.0649        | 0.2134             | 0.1594       | 0.885               | None                      | 0.56       | Higher gaps, especially on TSPLIB holdout. Highest code novelty.                              |
| tsplib_failure_replay            | 0.0649        | 0.2134             | 0.1594       | 0.907               | Failure replay            | 0.56       | Identical performance to no replay condition, with slightly higher code novelty.             |
| tsplib_failure_replay_compression| 0.0154        | 0.2567             | 0.1690       | 0.0                 | Failure replay + compression | 0.76       | Compression pressure coincides with worse transfer gaps and zero code novelty.               |

---

### Interpretation

- The **random replay** condition (*tsplib_random_replay*) achieves the **best transfer performance**, demonstrated by the lowest mean holdout TSPLIB gap (~9.1%) and synthetic gap (0%), surpassing all other conditions, including no replay.

- Both **no replay** and **failure replay** conditions yield **substantially worse holdout TSPLIB gaps (~21.3%) and transfer gaps (~16%)**, with similar final performance metrics, suggesting failure replay **does not improve transfer** despite slightly higher code novelty.

- The condition with **failure replay under compression pressure** results in both elevated TSPLIB gap (~25.7%) and transfer gap (16.9%) while eliminating code novelty altogether, indicating compression-aware replay harms transfer and restricts exploratory algorithm modifications.

- Code novelty **declines under random replay** (mean ~0.76) compared to no and failure replay (~0.88–0.91), yet the transfer ability improves notably. This supports that **code novelty reduction does not imply degraded transfer**, a critical insight cautioning against equating lexical novelty with algorithmic innovation.

- Complexity is higher (0.76) in random replay and failure replay with compression, contrasting with 0.56 in no replay and failure replay alone. Despite higher complexity in random replay, transfer metrics improve markedly.

---

### Conservative Conclusions

- **Random replay clearly enhances transfer performance** on both synthetic and TSPLIB holdouts relative to no replay and failure-based replay.

- The **improvement in transfer with random replay is achieved despite decreased code novelty and increased complexity**, indicating that lexical novelty metrics alone do not capture algorithmic improvements.

- Failure replay, without randomization, **does not improve transfer nor reduce optimality gaps** compared to no replay, despite higher code novelty.

- Compression-aware replay under failure samples **results in degraded transfer** and loss of code novelty, signaling potentially harmful effects of compressive pressures in replay.

---

### Recommendations for Replay-aware TSP Benchmarking

- Prioritize **random replay** over no replay or failure replay to improve transfer generalization.

- Evaluate **optimality gaps on held-out TSPLIB and synthetic benchmarks as primary evidence of transfer**, rather than code novelty or narrative speculation.

- Interpret **code novelty reductions cautiously** as they may co-occur with transfer gains instead of innovations lost.

- Avoid **compression-driven failure replays** due to their negative impact on transfer and innovation metrics.

---

*End of analysis.*
