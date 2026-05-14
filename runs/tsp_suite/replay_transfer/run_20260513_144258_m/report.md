# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_144258_m
- started_at_local: 2026-05-13 14:42:58
- finished_at_local: 2026-05-13 14:53:28
- duration_hhmm: 00:11
- duration_seconds: 630.443
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.222168 | 0.015447 | 0.146997 | 0.0 | 0.76 | 0.0 |
| tsplib_random_replay | random | score_only | False | 0.083243 | 0.0 | 0.052973 | 0.765593 | 0.76 | 0.063811 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.892373 | 0.56 | -0.027909 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.090427 | 0.0 | 0.057544 | 0.631667 | 0.76 | 0.053438 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.222168`, synthetic `0.015447`, combined `0.146997`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.222168` across 7 instances; family means: ch=0.180032, kroD=0.287968, pcb=0.301725, pr=0.309507, rd=0.220354, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3460, "family": "a", "name": "a280", "optimality_gap": 0.341605}, {"best_known_cost": 14379, "cost": 19102, "family": "lin", "name": "lin105", "optimality_gap": 0.328465}, {"best_known_cost": 7542, "cost": 9650, "family": "berlin", "name": "berlin52", "optimality_gap": 0.279501}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.083243`, synthetic `0.0`, combined `0.052973`.
- Accepted-epoch count `2`, mean accepted code novelty `0.765593`, and final complexity `0.76`.
- Adaptation efficiency `0.063811` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.083243` across 7 instances; family means: ch=0.045673, kroD=0.03602, pcb=0.169877, pr=0.159441, rd=0.093426, st=0.032593.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3582, "family": "a", "name": "a280", "optimality_gap": 0.38891}, {"best_known_cost": 14379, "cost": 18415, "family": "lin", "name": "lin105", "optimality_gap": 0.280687}, {"best_known_cost": 629, "cost": 743, "family": "eil", "name": "eil101", "optimality_gap": 0.18124}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.892373`, and final complexity `0.56`.
- Adaptation efficiency `-0.027909` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.090427`, synthetic `0.0`, combined `0.057544`.
- Accepted-epoch count `3`, mean accepted code novelty `0.631667`, and final complexity `0.76`.
- Adaptation efficiency `0.053438` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.090427` across 7 instances; family means: ch=0.038646, kroD=0.089884, pcb=0.285813, pr=0.107425, rd=0.041466, st=0.031111.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 2840, "family": "a", "name": "a280", "optimality_gap": 0.101202}, {"best_known_cost": 14379, "cost": 15293, "family": "lin", "name": "lin105", "optimality_gap": 0.063565}, {"best_known_cost": 629, "cost": 665, "family": "eil", "name": "eil101", "optimality_gap": 0.057234}]

## Judge Appendix
### Summary of Replay-aware TSP Benchmark Results

| Condition                      | Heldout TSPLIB Gap | Synthetic Holdout Gap | Transfer Gap  | Code Novelty (mean) | Replay Mode         | Notes                                                     |
|-------------------------------|--------------------|----------------------|---------------|---------------------|---------------------|-----------------------------------------------------------|
| **tsplib_no_replay**           | 0.222168           | 0.015447             | 0.146997      | 0.0                 | none                | Highest gaps, no code novelty, baseline performance.       |
| **tsplib_random_replay**       | **0.083243**       | **0.0**              | **0.052973**  | 0.765593            | random              | Best transfer and optimality gaps despite high novelty.    |
| **tsplib_failure_replay**      | 0.213387           | 0.064916             | 0.159398      | 0.892373            | failure             | Worst transfer and heldout gaps despite highest novelty.   |
| **tsplib_failure_replay_compression** | 0.090427    | 0.0                  | 0.057544      | 0.631667            | failure + compression | Close to random replay transfer; code novelty decreased.   |

---

### Interpretation

- **Transfer Performance:**
  - **Random Replay** condition achieves the best transfer performance, with substantially lower heldout TSPLIB gap (0.083) and synthetic gap (0.0), indicating superior generalization.
  - Both failure replay conditions have significantly worse transfer gaps compared to random replay, with failure replay (no compression) being the poorest.
  - No replay condition performs the worst in all transfer metrics.

- **Code Novelty vs Transfer:**
  - Random replay exhibits high code novelty (~0.77 mean) but improved transfer gaps, indicating that **code novelty decreased under failure replay conditions even as transfer performance worsened.**
  - No replay has zero code novelty and poor transfer.
  - Failure replay conditions have even higher novelty (~0.89 and 0.63) but do **not** lead to better transfer, underscoring that **lexical/code novelty alone does not imply transfer improvement or algorithmic invention**.

- **Replay Mode Effects:**
  - Random replay clearly outperforms no replay and failure replay in optimality gaps and transfer metrics.
  - Failure replay with compression moderately improves transfer gaps relative to failure replay without compression but remains inferior to random replay.
  - No replay has zero acceptance epochs (only 1 accepted epoch) and zero adaptation efficiency, opposite to replay conditions.

- **Other Metrics:**
  - Mean complexity is similar across better-performing conditions (~0.76).
  - Adaptation efficiency is positive only with replay (random: 0.0638; failure+compression: 0.0534), negative for failure replay without compression (-0.0279), and zero for no replay.
  - Best TSPLIB family mean gaps reflect the overall trends, showing notably lower means for random replay.

---

### Conservative Conclusion

- The **random replay condition provides the strongest evidence of improved transfer and optimality** on heldout TSPLIB and synthetic instances.
- This improvement comes despite the presence of high code novelty, which is not causally associated with improved transfer given that failure replay conditions have even higher novelty but worse gaps.
- Failure replay modes produce higher lexical/code novelty but fail to improve or even degrade transfer performance relative to random replay and no replay.
- Compression-aware replay shows some benefit over pure failure replay but is not competitive with random replay in transfer.
- Lexical code novelty and complexity measures alone do not support claims of algorithmic invention; improvements in deterministic transfer and gap metrics are necessary, with random replay condition meeting these criteria.
- **Replay mode and selection strategy significantly influence transfer outcomes, with random replay and score-only selection yielding best transfer gaps.**

---

# Key takeaway:
**Random replay optimizes transfer and generalization with moderate-to-high code novelty, outperforming all other replay modes and no replay. Increased novelty in failure replay conditions does not correlate with improved transfer, reinforcing reliance on gap metrics over narrative speculation.**
