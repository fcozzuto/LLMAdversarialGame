# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_no_replay`.
- Best TSPLIB holdout gap: `tsplib_no_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_134222_g
- started_at_local: 2026-05-13 13:42:22
- finished_at_local: 2026-05-13 13:51:55
- duration_hhmm: 00:10
- duration_seconds: 572.307
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.864896 | 0.56 | -0.028795 |
| tsplib_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.872001 | 0.56 | -0.028561 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.883365 | 0.56 | -0.028193 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.864896`, and final complexity `0.56`.
- Adaptation efficiency `-0.028795` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.872001`, and final complexity `0.56`.
- Adaptation efficiency `-0.028561` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.883365`, and final complexity `0.56`.
- Adaptation efficiency `-0.028193` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
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

| Condition                       | Replay Mode   | Adaptation Efficiency | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Compression Pressure | Comments                                                    |
|--------------------------------|---------------|-----------------------|-----------------|--------------------|-------------------|---------------------|----------------------|-------------------------------------------------------------|
| **tsplib_no_replay**            | none          | -0.028795             | 0.213387        | 0.064916           | 0.159398          | 0.864896            | no                   | Best transfer and gaps. Highest code novelty among replay conditions. |
| **tsplib_random_replay**        | random        | -0.028561             | 0.213387        | 0.064916           | 0.159398          | 0.872001            | no                   | Identical performance to no replay despite slightly lower novelty. |
| **tsplib_failure_replay**       | failure       | -0.028193             | 0.213387        | 0.064916           | 0.159398          | 0.883365            | no                   | Same transfer and optimality gaps as no replay, with marginally higher code novelty than no replay condition. |
| **tsplib_failure_replay_compression** | failure + compression | 0.0                   | 0.213387        | 0.064916           | 0.159398          | 0.0                 | yes                  | Identical transfer and gaps but zero code novelty due to compression-aware replay and novelty gating which limited changes. |

---

### Conservative Interpretation:

- **Optimality Gaps & Transfer Evidence:**  
  Across all four conditions, the **mean TSPLIB gap (~0.2134)**, **synthetic gap (~0.0649)**, and **transfer gap (~0.1594)** are exactly the same, indicating no measurable improvement or degradation under any replay regime in this benchmark suite.

- **Replay Modes:**  
  - *No replay (tsplib_no_replay)* performed equally well and is identified as the best condition overall.
  - *Random replay* and *failure replay* did not improve transfer or gaps relative to no replay.
  - *Compression-aware failure replay* with novelty gating showed a collapse in code novelty (mean = 0), but did not improve transfer outcomes. This suggests that increased compression pressure and novelty gating limited code changes without positively impacting transfer or optimality gaps.

- **Code Novelty vs Transfer:**  
  Although the *tsplib_failure_replay* condition had slightly higher mean code novelty (0.883) than *no replay* (0.865), the transfer and gap results were identical. Hence, increased code novelty does **not** translate here into better algorithmic generalization or transfer performance.  
  Conversely, the compression-aware replay condition drastically reduces code novelty to zero but does not outperform other conditions; transfer metrics remain matched.

- **Algorithmic Novelty:**  
  Given that all optimality gaps and transfer metrics are identical across conditions, **none of the replay modes provided algorithmic improvements**. The lexical/code novelty metric variation alone is insufficient to claim algorithmic invention.

- **Archived Archives and Behavior:**  
  All conditions maintain balanced final behavior profiles and similar elite/total archive sizes, with no compression pressure except in the compression-aware replay.

---

### Conclusion:

- The **no replay condition** currently provides the best empirical evidence for transfer effectiveness, showing minimal gaps and good transfer without replay complexity.
- Replay modes (random, failure) do not improve transfer or final optimality gaps compared to no replay, despite minor differences in code novelty.
- Compression-aware replay with novelty gating suppresses code novelty but does not improve transfer.
- Optimality gap and transfer metrics provide no support for claims that replay mechanism variations yield better performance in this benchmark.
- Code novelty differences among conditions do not correlate with improved transfer results and should not be interpreted as algorithmic advancement.

---

**Recommendations:**  
Prioritize the no replay baseline in further development until replay modes demonstrate improved transfer or reduced optimality gaps. Code novelty alone is insufficient evidence of algorithmic invention without corresponding improvements in deterministic metrics.
