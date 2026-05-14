# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_no_replay`.
- Best TSPLIB holdout gap: `tsplib_no_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_123823_a
- started_at_local: 2026-05-13 12:38:23
- finished_at_local: 2026-05-13 12:50:40
- duration_hhmm: 00:12
- duration_seconds: 736.891
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.113341 | 0.0 | 0.072126 | 0.743278 | 0.76 | 0.03087 |
| tsplib_random_replay | random | score_only | False | 0.145818 | 0.0 | 0.092793 | 0.669863 | 0.76 | 0.058627 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.903546 | 0.56 | -0.027564 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.174803 | 0.016511 | 0.117242 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.113341`, synthetic `0.0`, combined `0.072126`.
- Accepted-epoch count `4`, mean accepted code novelty `0.743278`, and final complexity `0.76`.
- Adaptation efficiency `0.03087` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.113341` across 7 instances; family means: ch=0.131838, kroD=0.106368, pcb=0.211312, pr=0.157592, rd=0.036662, st=0.017778.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3393, "family": "a", "name": "a280", "optimality_gap": 0.315626}, {"best_known_cost": 629, "cost": 778, "family": "eil", "name": "eil101", "optimality_gap": 0.236884}, {"best_known_cost": 14379, "cost": 17673, "family": "lin", "name": "lin105", "optimality_gap": 0.229084}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.145818`, synthetic `0.0`, combined `0.092793`.
- Accepted-epoch count `2`, mean accepted code novelty `0.669863`, and final complexity `0.76`.
- Adaptation efficiency `0.058627` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.145818` across 7 instances; family means: ch=0.121798, kroD=0.192777, pcb=0.30013, pr=0.025657, rd=0.165234, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3470, "family": "a", "name": "a280", "optimality_gap": 0.345483}, {"best_known_cost": 14379, "cost": 17603, "family": "lin", "name": "lin105", "optimality_gap": 0.224216}, {"best_known_cost": 7542, "cost": 8535, "family": "berlin", "name": "berlin52", "optimality_gap": 0.131663}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.903546`, and final complexity `0.56`.
- Adaptation efficiency `-0.027564` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.174803`, synthetic `0.016511`, combined `0.117242`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.174803` across 7 instances; family means: ch=0.140367, kroD=0.200902, pcb=0.239139, pr=0.301186, rd=0.112769, st=0.088889.
- Panel `synthetic_holdout` mean gap `0.016511` across 4 instances; family means: clustered_gaussian=0.024674, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 20172, "family": "lin", "name": "lin105", "optimality_gap": 0.402879}, {"best_known_cost": 2579, "cost": 3434, "family": "a", "name": "a280", "optimality_gap": 0.331524}, {"best_known_cost": 7542, "cost": 9619, "family": "berlin", "name": "berlin52", "optimality_gap": 0.275391}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Results

| Condition                        | Replay Mode          | Selection Mode   | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (Mean) | Complexity | Interpretation |
|---------------------------------|----------------------|------------------|-----------------|--------------------|-------------------|---------------------|------------|----------------|
| **tsplib_no_replay**             | None                 | Score Only       | **0.1133**      | 0.0                | **0.0721**        | 0.743               | 0.76       | Best optimality gaps and transfer metrics; no replay yielded the best transfer despite high code novelty. |
| tsplib_random_replay             | Random Replay        | Score Only       | 0.1458          | 0.0                | 0.0928            | 0.67                | 0.76       | Lower code novelty than no replay but worse transfer and TSPLIB gaps; replay did not improve transfer. |
| tsplib_failure_replay            | Failure Replay       | Score Only       | 0.2134          | 0.0649             | 0.1594            | 0.90                | 0.56       | Highest gaps in all metrics despite highest code novelty; failure replay negatively impacted transfer and optimality. |
| tsplib_failure_replay_compression| Failure Replay + Compression | Novelty Gate   | 0.1748          | 0.0165             | 0.1172            | 0.0                 | 0.76       | Code novelty dropped to zero while transfer and TSPLIB gaps worsened vs. no replay; compression pressure appears detrimental for transfer. |

---

### Key Interpretations

- **Transfer Metrics Priority**: According to the main evidence (held-out TSPLIB and synthetic gap), **tsplib_no_replay** outperforms all replay conditions for transfer and optimality.
- **Replay Impact**: Replay modes (random, failure) result in higher mean TSPLIB optimality gaps and transfer gaps compared to no replay.
- **Code Novelty vs. Transfer**:
  - Failure replay condition increases code novelty but correlates with worse transfer and optimality.
  - Compression-aware failure replay reduces code novelty to zero but does not improve transfer compared to random or failure replay without compression.
  - Thus, increases in code novelty do not imply algorithmic invention or better transfer.
- **Replay Modes Differences**:
  - No replay yields better transfer and optimization results.
  - Random replay degrades transfer slightly with lower code novelty than no replay.
  - Failure replay leads to highest gaps and code novelty, indicating instability or less effective adaptation.
  - Compression-aware failure replay further reduces code novelty but fails to improve transfer, indicating compression pressure may hinder performance in replay.

---

### Conservative Conclusion
The **no replay** condition is optimal for transfer and held-out performance. Replay (random or failure) lowers transfer quality despite varying effects on code novelty. Failure replay conditions produce higher optimality gaps and worse transfer metrics, and compression pressure reduces code novelty without performance gains. Hence, replay modes tested do not improve generalization or transfer relative to no replay. Also, code novelty metrics should not be conflated with algorithmic invention absent improvements in transfer or optimality gaps.
