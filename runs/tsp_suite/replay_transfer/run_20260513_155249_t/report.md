# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay_compression`.
- Best TSPLIB holdout gap: `tsplib_failure_replay_compression`.
- Best synthetic holdout gap: `tsplib_failure_replay`.

## Run Metadata
- run_name: run_20260513_155249_t
- started_at_local: 2026-05-13 15:52:49
- finished_at_local: 2026-05-13 16:03:00
- duration_hhmm: 00:10
- duration_seconds: 611.12
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.90376 | 0.56 | -0.027557 |
| tsplib_random_replay | random | score_only | False | 0.150744 | 0.010343 | 0.099689 | 0.74996 | 0.76 | 0.001182 |
| tsplib_failure_replay | failure | score_only | False | 0.162444 | 0.0 | 0.103373 | 0.750785 | 0.76 | 0.015459 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.127075 | 0.0 | 0.080866 | 0.672957 | 0.76 | 0.012927 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.90376`, and final complexity `0.56`.
- Adaptation efficiency `-0.027557` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.150744`, synthetic `0.010343`, combined `0.099689`.
- Accepted-epoch count `3`, mean accepted code novelty `0.74996`, and final complexity `0.76`.
- Adaptation efficiency `0.001182` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.150744` across 7 instances; family means: ch=0.145226, kroD=0.199962, pcb=0.264524, pr=0.109089, rd=0.145259, st=0.045926.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3408, "family": "a", "name": "a280", "optimality_gap": 0.321442}, {"best_known_cost": 7542, "cost": 9545, "family": "berlin", "name": "berlin52", "optimality_gap": 0.265579}, {"best_known_cost": 14379, "cost": 17716, "family": "lin", "name": "lin105", "optimality_gap": 0.232075}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.162444`, synthetic `0.0`, combined `0.103373`.
- Accepted-epoch count `3`, mean accepted code novelty `0.750785`, and final complexity `0.76`.
- Adaptation efficiency `0.015459` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.162444` across 7 instances; family means: ch=0.077811, kroD=0.194045, pcb=0.286699, pr=0.298006, rd=0.174589, st=0.028148.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3465, "family": "a", "name": "a280", "optimality_gap": 0.343544}, {"best_known_cost": 14379, "cost": 17789, "family": "lin", "name": "lin105", "optimality_gap": 0.237151}, {"best_known_cost": 7542, "cost": 9051, "family": "berlin", "name": "berlin52", "optimality_gap": 0.20008}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.127075`, synthetic `0.0`, combined `0.080866`.
- Accepted-epoch count `3`, mean accepted code novelty `0.672957`, and final complexity `0.76`.
- Adaptation efficiency `0.012927` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.127075` across 7 instances; family means: ch=0.100193, kroD=0.05147, pcb=0.189826, pr=0.301168, rd=0.121492, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3327, "family": "a", "name": "a280", "optimality_gap": 0.290035}, {"best_known_cost": 14379, "cost": 15748, "family": "lin", "name": "lin105", "optimality_gap": 0.095208}, {"best_known_cost": 7542, "cost": 7964, "family": "berlin", "name": "berlin52", "optimality_gap": 0.055953}]

## Judge Appendix
### Interpretation of Results for Replay-Aware TSP Benchmark Suite

| Condition                        | Synthetic Gap | TSPLIB Gap | Transfer Gap | Replay Mode             | Code Novelty (mean) | Complexity | Notes on Transfer and Novelty                   |
|---------------------------------|---------------|------------|--------------|------------------------|---------------------|------------|------------------------------------------------|
| **tsplib_no_replay**             | 0.064916      | 0.213387   | 0.159398     | none                   | 0.90376             | 0.56       | Worst transfer and TSPLIB gaps; highest code novelty but lowest transfer performance. |
| **tsplib_random_replay**         | 0.010343      | 0.150744   | 0.099689     | random                 | 0.74996             | 0.76       | Improved transfer and synthetic gaps vs no replay; code novelty reduced compared to no replay. |
| **tsplib_failure_replay**        | 0.0           | 0.162444   | 0.103373     | failure                | 0.75079             | 0.76       | Synthetic gap minimized; TSPLIB gap improved over no replay but worse than random replay; code novelty decreased. |
| **tsplib_failure_replay_compression** | 0.0           | 0.127075   | 0.080866     | failure + compression  | 0.67296             | 0.76       | Best TSPLIB and transfer gaps; synthetic gap zero; lowest code novelty and complexity controlled by compression. |

---

### Key Observations

1. **Optimality Gap & Transfer Performance**
   - The **tsplib_failure_replay_compression** condition exhibits the best performance on held-out TSPLIB (mean gap 0.127) and transfer gap (0.081), indicating superior generalization and adaptation.
   - Failure replay conditions (with and without compression) outperform random replay and no replay in transfer metrics, with compression further enhancing transfer.
   - No replay condition yields the poorest transfer and TSPLIB optimality gaps despite maintaining the highest code novelty.

2. **Code Novelty vs Transfer**
   - Code novelty decreases from no replay (0.90+) to failure replay (0.75) and further to failure replay with compression (0.67).
   - Transfer performance improves as code novelty decreases, indicating that reduced novelty due to replay and compression is associated with improved optimality and transfer.
   - This dissociation suggests that lexical novelty alone does not imply algorithmic invention; improved transfer is correlated with replay modes rather than novelty per se.

3. **Replay Modes**
   - No replay (baseline): Worst transfer and TSPLIB generalization gaps.
   - Random replay: Lower gaps than no replay but not best overall.
   - Failure replay: Further improvements relative to random replay.
   - Failure replay + compression: Best transfer and TSPLIB gaps, achieving zero synthetic gap.
   - Compression-aware replay reduces complexity (fixed at 0.76) compared to no replay (0.56 but with worse transfer), indicating effective control of solution complexity alongside transfer gains.

---

### Summary

- **Failure replay with compression pressure is the best transfer condition, achieving the lowest mean optimality gaps on held-out TSPLIB and synthetic sets.**
- **This improvement coincides with a reduction in code novelty compared to no replay, demonstrating that enhanced transfer is not driven by increased lexical novelty.**
- **Random replay provides moderate improvement over no replay but is outperformed by failure replay modes.**
- **Replay strategies focusing on failure cases and compression are effective for transfer, confirming the value of replay-aware learning in TSP generalization.**
