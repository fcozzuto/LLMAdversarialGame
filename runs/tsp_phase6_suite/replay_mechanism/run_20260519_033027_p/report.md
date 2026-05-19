# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_no_replay`.
- Best TSPLIB holdout gap: `phase6_no_replay`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260519_033027_p
- started_at_local: 2026-05-19 03:30:27
- finished_at_local: 2026-05-19 03:49:26
- duration_hhmm: 00:19
- duration_seconds: 1138.716
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.070305 | 0.015447 | 0.050357 | 0.236772 | 0.185541 | 0.0 | 0.651562 | 0.76 | 0.063188 |
| phase6_random_replay | random | score_only | False | 0.134742 | 0.0 | 0.085745 | 0.236772 | 0.141857 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_failure_replay | failure | score_only | False | 0.11596 | 0.0 | 0.073793 | 0.171206 | 0.32623 | 0.214526 | 0.77161 | 0.76 | 0.037481 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.153484 | 0.0 | 0.097672 | 0.236772 | 0.161596 | 0.221162 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.158723 | 0.0 | 0.101006 | 0.236772 | 0.165022 | 0.157119 | 0.0 | 0.76 | 0.0 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.850599 | 0.56 | -0.029279 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.856496 | 0.56 | -0.029078 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.070305`, synthetic `0.015447`, combined `0.050357`.
- Accepted-epoch count `3`, mean accepted code novelty `0.651562`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.185541`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.063188` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.070305` across 7 instances; family means: ch=0.060074, kroD=0.085282, pcb=0.236283, pr=0.004882, rd=0.020354, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3409, "expected_gap": 0.40822, "family": "a", "name": "a280", "optimality_gap": 0.32183, "residual_gap": -0.08639}, {"best_known_cost": 629, "cost": 827, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.314785, "residual_gap": 0.057233}, {"best_known_cost": 14379, "cost": 16308, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.134154, "residual_gap": -0.190806}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.134742`, synthetic `0.0`, combined `0.085745`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.141857`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133408`, mean selected residual gap `-0.009805`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.134742` across 7 instances; family means: ch=0.120922, kroD=0.122805, pcb=0.234629, pr=0.216154, rd=0.072946, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18560, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.290771, "residual_gap": -0.03099}, {"best_known_cost": 2579, "cost": 3183, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.234199, "residual_gap": -0.169756}, {"best_known_cost": 7542, "cost": 8126, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.077433, "residual_gap": -0.159189}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.11596`, synthetic `0.0`, combined `0.073793`.
- Accepted-epoch count `4`, mean accepted code novelty `0.77161`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.32623`, size bias `0.120322`, and failure concentration `0.214526`.
- Replay selection diversity `0.204223`, mean selected expected gap `0.316883`, mean selected residual gap `0.032031`.
- Adaptation efficiency `0.037481` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.11596` across 7 instances; family means: ch=0.102726, kroD=0.084296, pcb=0.272736, pr=0.119186, rd=0.081163, st=0.048889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3269, "expected_gap": 0.403722, "family": "a", "name": "a280", "optimality_gap": 0.267546, "residual_gap": -0.136176}, {"best_known_cost": 629, "cost": 676, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.074722, "residual_gap": -0.179968}, {"best_known_cost": 7542, "cost": 7990, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.059401, "residual_gap": -0.173747}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132217`, mean selected residual gap `0.039149`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001629}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.005619}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.153484`, synthetic `0.0`, combined `0.097672`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.161596`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236357`, mean selected residual gap `-0.020462`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.153484` across 7 instances; family means: ch=0.042933, kroD=0.239034, pcb=0.287565, pr=0.295648, rd=0.141087, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3389, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.314075, "residual_gap": -0.088096}, {"best_known_cost": 14379, "cost": 18147, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.262049, "residual_gap": -0.060324}, {"best_known_cost": 629, "cost": 754, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.198728, "residual_gap": -0.057552}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.158723`, synthetic `0.0`, combined `0.101006`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.165022`, size bias `8.3e-05`, and failure concentration `0.157119`.
- Replay selection diversity `0.269935`, mean selected expected gap `0.1547`, mean selected residual gap `0.001098`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.158723` across 7 instances; family means: ch=0.091954, kroD=0.295858, pcb=0.209835, pr=0.240627, rd=0.151201, st=0.02963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 17755, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.234787, "residual_gap": -0.087016}, {"best_known_cost": 2579, "cost": 3183, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.234199, "residual_gap": -0.168748}, {"best_known_cost": 7542, "cost": 8264, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.095731, "residual_gap": -0.137337}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.850599`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.264336`, mean selected residual gap `0.088057`.
- Adaptation efficiency `-0.029279` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.405273, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003955}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007302}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.856496`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301618`, mean selected residual gap `0.048371`.
- Adaptation efficiency `-0.029078` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.405351, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.004033}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.124006}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007302}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.300417`, mean selected residual gap `0.049571`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.405739, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.004421}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007539}]

## Judge Appendix
# Analysis of Replay-Aware TSP Benchmark Suite Results

## Summary
- **Best holdout TSPLIB gap:** `phase6_no_replay` (0.0703)
- **Best synthetic holdout gap:** `phase6_random_replay` (0.0)
- **Best overall transfer condition:** `phase6_no_replay` (transfer gap 0.0504)
- **Total conditions analyzed:** 9

## Key Metrics per Condition (mean gaps lower is better)

| Condition                         | Synthetic Holdout Gap | TSPLIB Holdout Gap | Transfer Gap | Replay Mode        | Code Novelty (mean) |
|----------------------------------|----------------------|--------------------|--------------|--------------------|---------------------|
| phase6_no_replay                 | 0.0154               | **0.0703 (best)**  | 0.0504 (best) | none               | 0.6516              |
| phase6_random_replay             | **0.0 (best)**       | 0.1347              | 0.0857       | random             | 0.0                 |
| phase6_failure_replay            | **0.0**              | 0.1160              | 0.0738       | failure            | 0.7716              |
| phase6_random_replay_compression | 0.0649               | 0.2134              | 0.1594       | random             | 0.0                 |
| phase6_stratified_random_replay  | 0.0                  | 0.1535              | 0.0977       | stratified_random  | 0.0                 |
| phase6_diversity_weighted_replay | 0.0                  | 0.1587              | 0.1010       | diversity_weighted | 0.0                 |
| phase6_residual_failure_replay   | 0.0649               | 0.2134              | 0.1594       | residual_failure   | 0.8506              |
| phase6_diversity_failure_replay  | 0.0649               | 0.2134              | 0.1594       | diversity_failure  | 0.8565              |
| phase6_diversity_failure_replay_compression | 0.0649         | 0.2134              | 0.1594       | diversity_failure  | 0.0                 |

## Interpretation of Main Transfer and Optimality-Gap Evidence

- **Transfer performance (TSPLIB gap and synthetic holdout gap):**
  - The no-replay condition `phase6_no_replay` achieves the best transfer gap (0.0504) and lowest TSPLIB holdout gap (0.0703), suggesting strongest generalization.
  - Random replay (`phase6_random_replay`) achieves perfect synthetic holdout gap (0.0) but has significantly worse TSPLIB gap (0.1347) and transfer gap (0.0857).
  - All replay-based conditions with compression or diversity weighting show *worse* transfer gaps (~0.1-0.16) and TSPLIB gaps (≥0.15), indicating reduced transfer despite varied replay strategies.
  - Failure-focused replay modes (`phase6_failure_replay`) have intermediate performance (transfer gap 0.0738, TSPLIB gap 0.1160), better than diversity/compression replay.

- **Code novelty:**
  - Conditions with replay have near-zero code novelty, except `phase6_no_replay` (mean 0.6516) and failure replay modes (`phase6_failure_replay` and `phase6_residual_failure_replay`, ~0.77-0.85).
  - Compression and diversity-based conditions have zero code novelty despite worse transfer, indicating no new code inventions under those replay modes.

## Archive and Replay Mechanism Insights

| Condition                       | Archive Key        | Archive Descriptor Diversity | Archive Hardness | Archive Size Bias | Replay Failure Concentration | Replay Selection Diversity |
|--------------------------------|--------------------|------------------------------|------------------|-------------------|------------------------------|----------------------------|
| phase6_no_replay               | experience_archive  | 0.240                        | 0.204            | 0.0               | 0.0                          | 0.0                        |
| phase6_random_replay           | experience_archive  | 0.237                        | 0.142            | 8.3e-05           | 0.195 (final)                | 0.262                      |
| phase6_failure_replay          | worst_archive       | 0.172                        | 0.335            | 0.125             | 0.243                        | 0.204                      |
| phase6_random_replay_compression | experience_archive | 0.237                        | 0.212            | 0.0               | 0.195                        | 0.262                      |
| phase6_stratified_random_replay | experience_archive  | 0.237                        | 0.188            | 0.0               | 0.170                        | 0.269                      |
| phase6_diversity_weighted_replay | experience_archive | 0.240                        | 0.197            | 0.0               | 0.105                        | 0.270                      |
| phase6_residual_failure_replay | residual_archive    | 0.150                        | 0.339            | 0.094             | 0.292 (mean)                 | 0.177                      |
| phase6_diversity_failure_replay | worst_archive      | 0.175                        | 0.349            | 0.125             | 0.170                        | 0.199                      |
| phase6_diversity_failure_replay_compression | worst_archive | 0.175                       | 0.349            | 0.125             | 0.170                        | 0.199                      |

- Replay failure concentration is zero for no replay (as expected).
- Failure replay and residual failure replay have highest failure concentration (≥0.24), focusing on harder cases.
- Diversity-weighted and stratified replay have moderate replay selection diversity (~0.2-0.27), indicating efforts to diversify, but still don't improve transfer.
- Archive descriptor diversity is highest (~0.24) in no replay and experience archives; worst and residual archives have lower diversity (~0.15-0.17).
- Archive hardness is notably higher in failure and residual replay modes (>0.33) compared to no-replay (~0.20) or random playback (~0.14).

## Conservative Conclusions

- **Transfer performance is strongest without replay (`phase6_no_replay`), with lowest TSPLIB and transfer gaps, despite moderate synthetic holdout gap.**
- Replay strategies, including random, stratified, diversity-weighted, and failure-based replay, do not improve transfer performance compared to no replay.
- Synthetic holdout gap is minimized (even zero) for random and diversity replay modes but this does not translate into improved transfer or TSPLIB generalization.
- Code novelty is *not* correlated with better transfer; notably, zero code novelty replay conditions (e.g., random replay) have worse transfer.
- Failures concentrate more with failure-based replay modes, increasing archive hardness but without corresponding transfer improvements.
- Compression-aware replay reduces complexity but also reduces transfer and increases gaps.
- Overall, replay variants do not show consistent benefit over no replay; replay introduces data biases (e.g., size bias, failure concentration) not beneficial for transfer.
- Lexical code novelty reduction under replay does not imply algorithmic innovation; measured adaptations appear limited or negative on transfer metrics.

---

# Summary:

- **Top transfer and TSPLIB holdout performance observed for `phase6_no_replay` (no replay), with low transfer gaps (~0.05-0.07).**
- **Random replay and other replay modes achieve better synthetic holdout performance but at cost of worse transfer and TSPLIB gaps.**
- **Failure replay modes yield more focused/harder archives but don't improve transfer compared to no replay.**
- **Replay reduces code novelty but no algorithmic advantage is evident as per gap metrics.**
- **Diversified or compression-aware replay does not improve generalization or replay benefit per transfer gaps and archive metrics.**

Hence, monitoring optimality gap and transfer gaps suggests no replay is preferable for transfer, while replay strategies often hurt or fail to enhance transfer despite archival or code impact.
