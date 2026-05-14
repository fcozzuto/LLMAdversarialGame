# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay`.
- Best TSPLIB holdout gap: `tsplib_failure_replay`.
- Best synthetic holdout gap: `tsplib_failure_replay_compression`.

## Run Metadata
- run_name: run_20260513_140147_i
- started_at_local: 2026-05-13 14:01:47
- finished_at_local: 2026-05-13 14:11:58
- duration_hhmm: 00:10
- duration_seconds: 611.317
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.778745 | 0.56 | -0.031981 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.822825 | 0.56 | -0.030268 |
| tsplib_failure_replay | failure | score_only | False | 0.087678 | 0.010343 | 0.059556 | 0.80747 | 0.76 | 0.058506 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.135725 | 0.0 | 0.08637 | 0.757872 | 0.76 | 0.009792 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.778745`, and final complexity `0.56`.
- Adaptation efficiency `-0.031981` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.822825`, and final complexity `0.56`.
- Adaptation efficiency `-0.030268` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.087678`, synthetic `0.010343`, combined `0.059556`.
- Accepted-epoch count `3`, mean accepted code novelty `0.80747`, and final complexity `0.76`.
- Adaptation efficiency `0.058506` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.087678` across 7 instances; family means: ch=0.069489, kroD=0.070583, pcb=0.203691, pr=0.089757, rd=0.036662, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3379, "family": "a", "name": "a280", "optimality_gap": 0.310198}, {"best_known_cost": 7542, "cost": 9363, "family": "berlin", "name": "berlin52", "optimality_gap": 0.241448}, {"best_known_cost": 629, "cost": 760, "family": "eil", "name": "eil101", "optimality_gap": 0.208267}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.135725`, synthetic `0.0`, combined `0.08637`.
- Accepted-epoch count `3`, mean accepted code novelty `0.757872`, and final complexity `0.76`.
- Adaptation efficiency `0.009792` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.135725` across 7 instances; family means: ch=0.102957, kroD=0.132573, pcb=0.174682, pr=0.246406, rd=0.147535, st=0.042963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3541, "family": "a", "name": "a280", "optimality_gap": 0.373013}, {"best_known_cost": 14379, "cost": 18335, "family": "lin", "name": "lin105", "optimality_gap": 0.275123}, {"best_known_cost": 629, "cost": 778, "family": "eil", "name": "eil101", "optimality_gap": 0.236884}]

## Judge Appendix
```markdown
# Review Summary of Replay-aware TSP Benchmark Suite

## Main Evidence: Optimality Gaps and Transfer Metrics

| Condition                     | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Replay Mode             | Code Novelty (mean) | Complexity | Notes on Transfer and Optimality Gap                      |
|-------------------------------|-----------------|--------------------|-------------------|------------------------|---------------------|------------|------------------------------------------------------------|
| tsplib_no_replay              | 0.213387        | 0.064916           | 0.159398          | none                   | 0.7787              | 0.56       | Highest TSPLIB gaps and transfer gaps, lowest transfer performance |
| tsplib_random_replay          | 0.213387        | 0.064916           | 0.159398          | random                 | 0.8228              | 0.56       | Identical to no replay in gaps; code novelty decreased slightly |
| tsplib_failure_replay         | **0.087678**    | **0.010343**       | **0.059556**      | failure                | 0.8075              | 0.76       | Best transfer and TSPLIB gaps; improved optimality and transfer |
| tsplib_failure_replay_compression | 0.135725        | 0.0                | 0.08637           | failure + compression  | 0.7579              | 0.76       | Best synthetic gap (0), intermediate TSPLIB and transfer gaps; lower code novelty |

---

## Interpretation

### Transfer and Optimality
- **Failure replay (tsplib_failure_replay)** achieves the best transfer results, with TSPLIB gap reduced ~59% compared to no replay, and synthetic gap near zero (0.01).
- The **compression-aware variant** of failure replay (tsplib_failure_replay_compression) further reduces synthetic gap to zero but increases TSPLIB and transfer gaps compared to failure replay without compression.
- Both failure replay conditions exhibit notably better optimality gaps on heldout TSPLIB instances than no replay or random replay, indicating that replaying failure cases selectively improves transfer quality.

### Code Novelty vs. Transfer
- Code novelty mean slightly drops from no replay (0.7787) and random replay (0.8228) to failure replay compression (0.7579), but transfer metrics improve markedly.
- This suggests that **improved transfer is achieved despite, or even alongside, a decrease in code novelty**.
- Lexical code novelty does not correspond directly to performance improvements; algorithmic gains are supported by deterministic optimality and transfer metrics rather than novelty scores alone.

### Replay Mode Effects
- No replay and random replay yield the same (worst) gaps, showing that **random replay does not improve transfer compared to no replay**.
- Selective failure replay (with or without compression) enhances transfer and reduces optimality gaps significantly.
- Compression-aware failure replay slightly compromises transfer compared to failure replay without compression but improves synthetic optimality gap to zero.

---

## Additional Observations

- Complexity increases from 0.56 (no and random replay) to 0.76 (failure replay variants), which might be correlated with improved solution quality.
- Adaptation efficiency is positive only in failure replay conditions, further supporting their effectiveness.
- Worst-case TSPLIB gaps decrease substantially in failure replay: e.g., pr76 gap drops from 0.35 (no replay) to ~0.09.

---

## Summary Conclusion

- **Failure replay conditions provide the strongest evidence for improved transfer and optimality gaps on held-out TSPLIB and synthetic instances.**
- **Random replay does not improve transfer over no replay, despite minor changes in code novelty.**
- Use of compression in failure replay reduces code novelty and increases TSPLIB and transfer gaps slightly compared to failure replay without compression, indicating a trade-off between synthetic optimality and transfer performance.
- Improvements in transfer are supported by deterministic metrics rather than lexical code novelty, confirming that algorithmic advantage stems from selective replay of failure cases rather than mere novelty.

```
