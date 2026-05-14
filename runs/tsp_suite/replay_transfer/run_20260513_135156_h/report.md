# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_135156_h
- started_at_local: 2026-05-13 13:51:56
- finished_at_local: 2026-05-13 14:01:45
- duration_hhmm: 00:10
- duration_seconds: 589.216
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.882029 | 0.56 | -0.028236 |
| tsplib_random_replay | random | score_only | False | 0.073344 | 0.006169 | 0.048917 | 0.672212 | 0.76 | 0.052384 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.78455 | 0.56 | -0.031744 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.173003 | 0.017074 | 0.116302 | 0.817808 | 0.76 | 0.06617 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.882029`, and final complexity `0.56`.
- Adaptation efficiency `-0.028236` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.073344`, synthetic `0.006169`, combined `0.048917`.
- Accepted-epoch count `3`, mean accepted code novelty `0.672212`, and final complexity `0.76`.
- Adaptation efficiency `0.052384` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.073344` across 7 instances; family means: ch=0.039647, kroD=0.074199, pcb=0.176592, pr=0.043621, rd=0.081922, st=0.057778.
- Panel `synthetic_holdout` mean gap `0.006169` across 4 instances; family means: clustered_gaussian=0.024674, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10061, "family": "berlin", "name": "berlin52", "optimality_gap": 0.333996}, {"best_known_cost": 14379, "cost": 19018, "family": "lin", "name": "lin105", "optimality_gap": 0.322623}, {"best_known_cost": 2579, "cost": 3404, "family": "a", "name": "a280", "optimality_gap": 0.319891}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.78455`, and final complexity `0.56`.
- Adaptation efficiency `-0.031744` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.173003`, synthetic `0.017074`, combined `0.116302`.
- Accepted-epoch count `2`, mean accepted code novelty `0.817808`, and final complexity `0.76`.
- Adaptation efficiency `0.06617` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.173003` across 7 instances; family means: ch=0.16062, kroD=0.169203, pcb=0.23262, pr=0.199937, rd=0.19469, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.017074` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3451, "family": "a", "name": "a280", "optimality_gap": 0.338116}, {"best_known_cost": 7542, "cost": 9545, "family": "berlin", "name": "berlin52", "optimality_gap": 0.265579}, {"best_known_cost": 14379, "cost": 17825, "family": "lin", "name": "lin105", "optimality_gap": 0.239655}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Results

| Condition                     | Replay Mode   | Selection Mode  | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (Mean) | Complexity | Adaptation Efficiency |
|-------------------------------|---------------|-----------------|-----------------|--------------------|-------------------|---------------------|------------|-----------------------|
| tsplib_no_replay              | none          | score_only      | 0.2134          | 0.0649             | 0.1594            | 0.8820              | 0.56       | -0.0282               |
| tsplib_random_replay          | random        | score_only      | **0.0733**      | **0.0062**         | **0.0489**        | 0.6722              | 0.76       | 0.0524                |
| tsplib_failure_replay         | failure       | score_only      | 0.2134          | 0.0649             | 0.1594            | 0.7846              | 0.56       | -0.0317               |
| tsplib_failure_replay_compression | failure + compression | novelty_gate | 0.1730          | 0.0171             | 0.1163            | 0.8178              | 0.76       | 0.0662                |

---

### Interpretation

- **Best transfer performance** (lowest TSPLIB and synthetic holdout gaps) is given by **tsplib_random_replay**:
  - Mean TSPLIB gap (0.0733) and mean synthetic gap (0.0062) substantially outperform all other conditions.
  - Mean transfer gap (0.0489) is also the lowest, indicating strongest generalization to held-out and synthetic data.
  
- **Code novelty** decreases in tsplib_random_replay (mean 0.6722) compared to no replay (0.8820), despite improved transfer metrics.
  - This suggests that improved transfer is achieved **not by increasing code novelty**, but by more effective reuse via random replay.
  
- **No replay** and **failure replay** without compression have identical final gaps, showing no transfer improvement and negative adaptation efficiencies.
  
- The **failure replay with compression and novelty gate** has some transfer improvement over no replay/failure replay:
  - It reduces mean TSPLIB gap from 0.2134 to 0.1730 and synthetic gap from 0.0649 to 0.0171.
  - Adaptation efficiency is positive (0.0662), but transfer remains worse than random replay.
  - Code novelty (0.8178) is intermediate but still higher than random replay.
  - Compression pressure is active here, indicating an added constraint during replay.

- **Complexity** is higher (~0.76) in random replay and failure replay with compression compared to 0.56 in no replay and failure replay without compression.

---

### Conservative Conclusions

- **Random replay yields the strongest evidence of improved generalization and transfer** based on both the held-out TSPLIB and synthetic holdout gaps.
- The improvement in transfer performance with random replay occurs alongside a **drop in code novelty**, meaning better performance is due to effective exploitation rather than new algorithmic invention.
- Failure replay without compression does not improve transfer relative to no replay, indicating that replay type matters.
- Adding compression pressure with failure replay improves transfer gaps somewhat but fails to outperform random replay.
- Complexity increases moderately with replay modes that facilitate transfer, reflecting potentially richer behavior profiles.
- Adaptation efficiency correlates positively with improved transfer: random replay and failure replay with compression have positive adaptation efficiencies, while others are negative.

---

### Key Takeaways

- Prioritize **random replay** for maximizing transfer and optimality-gap improvements in this replay-aware TSP benchmark.
- Code novelty metrics alone are insufficient to claim algorithmic innovation; lower novelty with better transfer suggests effective learning or memory utilization instead.
- Different replay modes distinctly impact transfer, underlining the need to differentiate no replay, random replay, failure replay, and compression-aware replay in analysis.
- Compression-aware failure replay partially closes the transfer gap but does not surpass random replay, indicating room for further methods combining replay types and complexity control.
