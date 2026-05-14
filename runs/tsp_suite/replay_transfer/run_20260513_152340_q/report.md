# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_no_replay`.
- Best TSPLIB holdout gap: `tsplib_no_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_152340_q
- started_at_local: 2026-05-13 15:23:40
- finished_at_local: 2026-05-13 15:33:45
- duration_hhmm: 00:10
- duration_seconds: 604.771
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.078414 | 0.0 | 0.0499 | 0.676264 | 0.76 | 0.08058 |
| tsplib_random_replay | random | score_only | False | 0.097539 | 0.0 | 0.06207 | 0.623686 | 0.76 | 0.03663 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.913641 | 0.56 | -0.027259 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.082055 | 0.010343 | 0.055978 | 0.597264 | 0.76 | 0.046972 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.078414`, synthetic `0.0`, combined `0.0499`.
- Accepted-epoch count `3`, mean accepted code novelty `0.676264`, and final complexity `0.76`.
- Adaptation efficiency `0.08058` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.078414` across 7 instances; family means: ch=0.077853, kroD=0.096271, pcb=0.182953, pr=0.056565, rd=0.036662, st=0.020741.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 9644, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706}, {"best_known_cost": 2579, "cost": 3294, "family": "a", "name": "a280", "optimality_gap": 0.277239}, {"best_known_cost": 14379, "cost": 17216, "family": "lin", "name": "lin105", "optimality_gap": 0.197302}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.097539`, synthetic `0.0`, combined `0.06207`.
- Accepted-epoch count `3`, mean accepted code novelty `0.623686`, and final complexity `0.76`.
- Adaptation efficiency `0.03663` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.097539` across 7 instances; family means: ch=0.050092, kroD=0.074058, pcb=0.189255, pr=0.112871, rd=0.130847, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3174, "family": "a", "name": "a280", "optimality_gap": 0.23071}, {"best_known_cost": 629, "cost": 684, "family": "eil", "name": "eil101", "optimality_gap": 0.08744}, {"best_known_cost": 14379, "cost": 15601, "family": "lin", "name": "lin105", "optimality_gap": 0.084985}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.913641`, and final complexity `0.56`.
- Adaptation efficiency `-0.027259` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.082055`, synthetic `0.010343`, combined `0.055978`.
- Accepted-epoch count `3`, mean accepted code novelty `0.597264`, and final complexity `0.76`.
- Adaptation efficiency `0.046972` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.082055` across 7 instances; family means: ch=0.061264, kroD=0.060346, pcb=0.206881, pr=0.037704, rd=0.084703, st=0.062222.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3224, "family": "a", "name": "a280", "optimality_gap": 0.250097}, {"best_known_cost": 14379, "cost": 15729, "family": "lin", "name": "lin105", "optimality_gap": 0.093887}, {"best_known_cost": 7542, "cost": 7964, "family": "berlin", "name": "berlin52", "optimality_gap": 0.055953}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Suite Results

| Condition                      | Replay Mode         | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (Mean) | Complexity | Notes                                                                                             |
|-------------------------------|---------------------|-----------------|--------------------|-------------------|---------------------|------------|-------------------------------------------------------------------------------------------------|
| **tsplib_no_replay**           | None                | **0.078414**    | **0.0**            | **0.0499**        | 0.676               | 0.76       | Best transfer and optimality gaps. No replay yields lowest gaps despite moderate code novelty.  |
| tsplib_random_replay           | Random              | 0.097539        | 0.0                | 0.06207           | 0.624               | 0.76       | Slightly worse transfer and TSPLIB gaps with lower code novelty than no_replay.                 |
| tsplib_failure_replay          | Failure             | 0.213387        | 0.064916           | 0.159398          | **0.914**           | 0.56       | Substantially worse transfer and TSPLIB gaps despite highest code novelty; no transfer benefit. |
| tsplib_failure_replay_compression | Failure + Compression | 0.082055        | 0.010343           | 0.055978          | 0.597               | 0.76       | Moderate gaps, better than failure_replay alone; code novelty falls while transfer improves.     |

---

### Key Interpretations

- **Transfer and Optimality Gaps as Primary Indicators**  
  The **no replay** condition achieves the best held-out TSPLIB gap (0.0784) and synthetic gap (0.0), indicating superior transfer across problem families. The mean transfer gap is lowest (0.0499), confirming the best generalization. This condition should be considered the benchmark for transfer performance.

- **Effect of Replay on Transfer Performance**  
  - **Random replay** results in slightly degraded transfer and TSPLIB gaps compared to no replay; code novelty also decreases.  
  - **Failure replay without compression** yields the worst transfer and TSPLIB gaps despite showing the highest code novelty (0.91 mean). This suggests that increased code novelty does *not* translate to improved transfer or optimality, likely reflecting overfitting or ineffective replay dynamics.  
  - **Failure replay with compression** partly recovers transfer performance and optimality gaps (close to no replay) while code novelty drops significantly (to 0.60 mean), indicating compression modulates code novelty and supports better generalization.

- **Code Novelty vs. Transfer**  
  High code novelty under failure replay conditions does not correspond with better transfer or solution quality; in fact, the reverse is true. Conversely, the no replay condition maintains moderate novelty but achieves the best transfer metrics. This demonstrates that lexical novelty alone is an insufficient proxy for algorithmic invention without improvements in deterministic metrics.

- **Replay Modes Distinction**  
  The **no replay** mode outperforms **random replay** and **failure replay** modes clearly in transfer and held-out TSPLIB gaps. Failure replay results are particularly poor unless combined with compression-aware replay, which partly restores performance by reducing code novelty and maintaining complexity.

- **Complexity and Behavior**  
  Complexity is generally stable at 0.76 except for failure replay (0.56). Behavior profiles differ by replay mode but do not align simplistically with transfer performance—balanced profile in no replay condition has best results.

---

### Conclusion

- The **no replay** condition demonstrates superior transfer to held-out TSPLIB and synthetic benchmarks, achieving the lowest optimality gaps and transfer gaps.  
- Replay strategies (random, failure) degrade transfer and solution quality, despite failure replay increasing code novelty substantially.  
- Compression-aware failure replay reduces code novelty and partially improves transfer metrics, though it does not surpass no replay.  
- Lexical/code novelty elevation alone does not imply effective algorithmic invention without accompanying improvements in transfer or optimality gaps.  
- Therefore, from a conservative, metric-prioritized perspective, **no replay is the most effective condition**, and replay methods require further refinement to improve transfer rather than merely increase novelty.
