# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay_compression`.
- Best TSPLIB holdout gap: `tsplib_failure_replay_compression`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_130152_c
- started_at_local: 2026-05-13 13:01:52
- finished_at_local: 2026-05-13 13:12:39
- duration_hhmm: 00:11
- duration_seconds: 647.091
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.819021 | 0.56 | -0.030408 |
| tsplib_random_replay | random | score_only | False | 0.15793 | 0.0 | 0.100501 | 0.815172 | 0.76 | 0.126262 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.892558 | 0.58 | -0.027903 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.092257 | 0.0 | 0.058709 | 0.835391 | 0.76 | 0.075976 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.819021`, and final complexity `0.56`.
- Adaptation efficiency `-0.030408` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.15793`, synthetic `0.0`, combined `0.100501`.
- Accepted-epoch count `2`, mean accepted code novelty `0.815172`, and final complexity `0.76`.
- Adaptation efficiency `0.126262` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.15793` across 7 instances; family means: ch=0.179697, kroD=0.185921, pcb=0.215014, pr=0.106399, rd=0.121745, st=0.117037.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3540, "family": "a", "name": "a280", "optimality_gap": 0.372625}, {"best_known_cost": 629, "cost": 828, "family": "eil", "name": "eil101", "optimality_gap": 0.316375}, {"best_known_cost": 14379, "cost": 17442, "family": "lin", "name": "lin105", "optimality_gap": 0.213019}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.892558`, and final complexity `0.56`.
- Adaptation efficiency `-0.027903` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.092257`, synthetic `0.0`, combined `0.058709`.
- Accepted-epoch count `2`, mean accepted code novelty `0.835391`, and final complexity `0.76`.
- Adaptation efficiency `0.075976` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.092257` across 7 instances; family means: ch=0.077617, kroD=0.108904, pcb=0.203828, pr=0.119777, rd=0.03287, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3449, "family": "a", "name": "a280", "optimality_gap": 0.33734}, {"best_known_cost": 629, "cost": 734, "family": "eil", "name": "eil101", "optimality_gap": 0.166932}, {"best_known_cost": 14379, "cost": 16255, "family": "lin", "name": "lin105", "optimality_gap": 0.130468}]

## Judge Appendix
```markdown
# Replay-Aware TSP Benchmark Suite Analysis

## Conditions Overview
- **No replay** (`tsplib_no_replay`): Replay mode = none, selection = score_only
- **Random replay** (`tsplib_random_replay`): Replay mode = random, selection = score_only
- **Failure replay** (`tsplib_failure_replay`): Replay mode = failure, selection = score_only
- **Failure replay with compression** (`tsplib_failure_replay_compression`): Replay mode = failure, selection = novelty_gate, compression applied

---

## Key Metrics for Transfer (Held-out TSPLIB & Synthetic Holdout)

| Condition                         | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Replay Mode | Selection Mode     |
|----------------------------------|-----------------|--------------------|-------------------|---------------------|-------------|--------------------|
| tsplib_no_replay                 | 0.213387        | 0.064916           | 0.159398          | 0.819021            | none        | score_only         |
| tsplib_random_replay             | 0.15793         | 0.0                | 0.100501          | 0.815172            | random      | score_only         |
| tsplib_failure_replay            | 0.213387        | 0.064916           | 0.159398          | 0.892558            | failure     | score_only         |
| tsplib_failure_replay_compression| **0.092257**    | **0.0**            | **0.058709**      | 0.835391            | failure     | novelty_gate       |

---

## Interpretation

1. **Optimality gaps indicate best transfer with `tsplib_failure_replay_compression`:**
   - Lowest mean TSPLIB gap (0.092257) compared to all other conditions.
   - Zero synthetic holdout gap, matching or outperforming others.
   - Lowest mean transfer gap (0.058709).

2. **Random replay improves transfer over no replay despite slight code novelty reduction:**
   - `tsplib_random_replay` has lower TSPLIB and transfer gaps than no replay.
   - Code novelty slightly lower than no replay (0.815 vs 0.819).
   - This shows improved transfer not driven by higher code novelty or algorithmic novelty.

3. **Failure replay without compression does not improve transfer over no replay:**
   - Has identical TSPLIB and transfer gaps as no replay condition.
   - However, this condition shows increased code novelty (~0.89 vs ~0.82).
   - Thus, increased code novelty here did not yield better transfer.

4. **Compression-aware failure replay enhances transfer and lowers optimality gaps, with modest code novelty:**
   - Despite slightly lower code novelty (0.835 vs 0.89 in failure replay), this condition achieves the best transfer metrics.
   - Use of novelty gating for selection and compression pressure likely contribute to improved performance.

5. **Behavior profiles and complexity:**
   - Conditions with better transfer (`random_replay` and `failure_replay_compression`) have higher final complexity (0.76) vs others (0.56), possibly indicating more sophisticated strategies.
   - `failure_replay_compression` uses novelty gating, which differs from other score-only selection modes, possibly contributing to improvements.

---

## Summary

- **Best transfer performance is achieved by `tsplib_failure_replay_compression`**, with the lowest optimality gaps on held-out TSPLIB and synthetic benchmarks.
- **Random replay condition improves transfer over no replay despite slightly lower code novelty**, showing that increased transfer is not always linked with code novelty spikes.
- **Failure replay without compression did not improve transfer despite higher code novelty**, indicating lexical novelty alone does not imply algorithmic improvement.
- **Compression-aware replay with novelty-based selection enhances transfer**, outperforming other replay modes.
- Careful distinction between replay types and use of compression-aware strategies is critical for improved generalization and optimality gap reduction.

---

**No evidence from optimality-gap or transfer data suggests that lexical code novelty equates to algorithmic invention here.** Improvements in transfer correlate more with replay type and compression-aware selection than with higher code novelty alone.
```
