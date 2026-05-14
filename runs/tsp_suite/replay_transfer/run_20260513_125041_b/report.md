# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_no_replay`.
- Best TSPLIB holdout gap: `tsplib_no_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_125041_b
- started_at_local: 2026-05-13 12:50:41
- finished_at_local: 2026-05-13 13:01:51
- duration_hhmm: 00:11
- duration_seconds: 670.014
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.09697 | 0.0 | 0.061708 | 0.743669 | 0.76 | 0.023044 |
| tsplib_random_replay | random | score_only | False | 0.104374 | 0.0 | 0.06642 | 0.858904 | 0.76 | 0.074691 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.877854 | 0.56 | -0.02837 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.09697`, synthetic `0.0`, combined `0.061708`.
- Accepted-epoch count `4`, mean accepted code novelty `0.743669`, and final complexity `0.76`.
- Adaptation efficiency `0.023044` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.09697` across 7 instances; family means: ch=0.065484, kroD=0.065089, pcb=0.216432, pr=0.128588, rd=0.081416, st=0.056296.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3302, "family": "a", "name": "a280", "optimality_gap": 0.280341}, {"best_known_cost": 7542, "cost": 9203, "family": "berlin", "name": "berlin52", "optimality_gap": 0.220233}, {"best_known_cost": 629, "cost": 758, "family": "eil", "name": "eil101", "optimality_gap": 0.205087}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.104374`, synthetic `0.0`, combined `0.06642`.
- Accepted-epoch count `2`, mean accepted code novelty `0.858904`, and final complexity `0.76`.
- Adaptation efficiency `0.074691` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.104374` across 7 instances; family means: ch=0.163967, kroD=0.056964, pcb=0.216038, pr=0.004882, rd=0.062579, st=0.062222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3490, "family": "a", "name": "a280", "optimality_gap": 0.353238}, {"best_known_cost": 629, "cost": 816, "family": "eil", "name": "eil101", "optimality_gap": 0.297297}, {"best_known_cost": 14379, "cost": 16930, "family": "lin", "name": "lin105", "optimality_gap": 0.177412}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.877854`, and final complexity `0.56`.
- Adaptation efficiency `-0.02837` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
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
### Summary of Replay-Aware TSP Benchmark Results

| Condition                         | Replay Mode        | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Adaptation Efficiency | Comments                                                                                  |
|----------------------------------|--------------------|-----------------|--------------------|-------------------|---------------------|------------|-----------------------|-------------------------------------------------------------------------------------------|
| **tsplib_no_replay**              | None               | **0.0970**      | **0.0000**         | **0.0617**        | 0.7437              | 0.76       | 0.0230                | Best performance on transfer and test gaps. Moderate code novelty.                       |
| tsplib_random_replay              | Random             | 0.1044          | 0.0000             | 0.0664            | 0.8589              | 0.76       | 0.0747                | Slightly worse transfer and test gaps despite higher code novelty and adaptation efficiency. |
| tsplib_failure_replay             | Failure            | 0.2134          | 0.0649             | 0.1594            | 0.8779              | 0.56       | -0.0284               | Substantially worse gaps despite highest code novelty and reasonable complexity.          |
| tsplib_failure_replay_compression | Failure + Compression | 0.2134          | 0.0649             | 0.1594            | 0.0000              | 0.56       | 0.0000                | No code novelty, equal gaps to failure replay without compression.                        |


### Interpretation

- **Transfer and Optimality Gap Metrics:**  
  The **no replay (tsplib_no_replay)** condition strongly outperforms all replay modes, showing the lowest mean gaps on both held-out TSPLIB (0.0970) and synthetic benchmarks (0.0). It also yields the best transfer gap (0.0617). This establishes tsplib_no_replay as the best transfer condition.

- **Replay Mode Impact:**  
  Introducing **random replay** slightly increases transfer and test gaps and improves adaptation efficiency and code novelty. However, this does not translate into better transfer performance, indicating no algorithmic improvement despite higher novelty.

  Both **failure replay** modes (with and without compression) perform substantially worse on transfer and test gaps, with mean gaps more than doubled compared to no replay. They also suffer from lower final behavior complexity (0.56 vs 0.76), which may relate to poorer solution quality.

- **Code Novelty vs Transfer:**  
  Code novelty is highest in failure replay conditions but the transfer performance is worst there. Conversely, tsplib_no_replay has moderate code novelty but the best transfer results. The compression-aware failure replay condition uniquely has zero code novelty but shares the failure replay's poor transfer performance. Hence, higher code novelty does **not** correspond to improved transfer in this suite.

- **Replay Type Distinctions:**  
  - **No replay:** best transfer and optimality gaps  
  - **Random replay:** slightly worse transfer and test gaps, higher code novelty  
  - **Failure replay:** worst gaps, highest code novelty but negative adaptation efficiency  
  - **Failure replay + compression:** no code novelty, worst gaps, no adaptation efficiency gain

- **Algorithmic Invention vs Lexical Novelty:**  
  The data indicates that the observed increases in code novelty (especially in failure replay modes) do not lead to better transfer or optimality results. Therefore, lexical/code novelty here does not imply algorithmic invention as measured by deterministic transfer metrics.

---

### Conclusion

- The **"tsplib_no_replay"** condition shows the best transfer robustness and optimality gaps across held-out and synthetic benchmarks, validating it as the superior approach under this evaluation framework.
- Replay strategies (random or failure) do **not** improve transfer performance; failure replay notably degrades it despite higher code novelty, showing a disconnect between novelty and effective algorithmic improvement.
- Compression pressure reduces code novelty to zero without improving transfer gaps in failure replay.
- Overall, transfer metrics clearly prioritize **no replay** for effective generalization, with code novelty alone not predictive or indicative of algorithmic gains in this setting.
