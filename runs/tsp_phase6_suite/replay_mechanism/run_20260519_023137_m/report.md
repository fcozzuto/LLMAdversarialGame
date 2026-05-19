# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_weighted_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_weighted_replay`.
- Best synthetic holdout gap: `phase6_failure_replay`.

## Run Metadata
- run_name: run_20260519_023137_m
- started_at_local: 2026-05-19 02:31:37
- finished_at_local: 2026-05-19 02:51:03
- duration_hhmm: 00:19
- duration_seconds: 1165.295
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.10708 | 0.003941 | 0.069575 | 0.236772 | 0.185832 | 0.0 | 0.794158 | 0.76 | 0.056868 |
| phase6_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.857086 | 0.56 | -0.029058 |
| phase6_failure_replay | failure | score_only | False | 0.121787 | 0.0 | 0.077501 | 0.171206 | 0.23931 | 0.221051 | 0.648022 | 0.76 | 0.059623 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.122153 | 0.001628 | 0.078326 | 0.236772 | 0.156985 | 0.221162 | 0.850377 | 0.76 | 0.062297 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.076002 | 0.006169 | 0.050608 | 0.236772 | 0.161517 | 0.130039 | 0.760188 | 0.76 | 0.042501 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.886718 | 0.56 | -0.028087 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.140392 | 0.001628 | 0.089932 | 0.171206 | 0.258194 | 0.17235 | 0.787879 | 0.76 | 0.051766 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.10708`, synthetic `0.003941`, combined `0.069575`.
- Accepted-epoch count `3`, mean accepted code novelty `0.794158`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.185832`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.056868` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.10708` across 7 instances; family means: ch=0.074431, kroD=0.176951, pcb=0.233979, pr=0.054466, rd=0.041972, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3447, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.336565, "residual_gap": -0.069949}, {"best_known_cost": 629, "cost": 766, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.217806, "residual_gap": -0.039746}, {"best_known_cost": 14379, "cost": 17442, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.213019, "residual_gap": -0.115822}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.857086`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133793`, mean selected residual gap `0.037573`.
- Adaptation efficiency `-0.029058` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.406204, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.004886}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.000807}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.121787`, synthetic `0.0`, combined `0.077501`.
- Accepted-epoch count `2`, mean accepted code novelty `0.648022`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.23931`, size bias `0.120322`, and failure concentration `0.221051`.
- Replay selection diversity `0.188305`, mean selected expected gap `0.32049`, mean selected residual gap `-0.03642`.
- Adaptation efficiency `0.059623` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.121787` across 7 instances; family means: ch=0.125157, kroD=0.102048, pcb=0.264898, pr=0.036113, rd=0.147282, st=0.051852.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18716, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.30162, "residual_gap": -0.025037}, {"best_known_cost": 629, "cost": 791, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.257552, "residual_gap": 0.002862}, {"best_known_cost": 2579, "cost": 3180, "expected_gap": 0.408608, "family": "a", "name": "a280", "optimality_gap": 0.233036, "residual_gap": -0.175572}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132582`, mean selected residual gap `0.038784`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.409771, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.008453}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.002156}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.122153`, synthetic `0.001628`, combined `0.078326`.
- Accepted-epoch count `2`, mean accepted code novelty `0.850377`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.156985`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237011`, mean selected residual gap `-0.017589`.
- Adaptation efficiency `0.062297` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.122153` across 7 instances; family means: ch=0.142714, kroD=0.079224, pcb=0.184292, pr=0.099049, rd=0.101896, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3520, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.36487, "residual_gap": -0.039473}, {"best_known_cost": 14379, "cost": 19404, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.349468, "residual_gap": 0.02448}, {"best_known_cost": 629, "cost": 823, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.308426, "residual_gap": 0.052146}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.076002`, synthetic `0.006169`, combined `0.050608`.
- Accepted-epoch count `3`, mean accepted code novelty `0.760188`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.161517`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.263651`, mean selected expected gap `0.167812`, mean selected residual gap `-0.020868`.
- Adaptation efficiency `0.042501` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.076002` across 7 instances; family means: ch=0.055566, kroD=0.097962, pcb=0.168341, pr=0.056565, rd=0.041719, st=0.056296.
- Panel `synthetic_holdout` mean gap `0.006169` across 4 instances; family means: clustered_gaussian=0.024674, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 20125, "expected_gap": 0.325433, "family": "lin", "name": "lin105", "optimality_gap": 0.399611, "residual_gap": 0.074178}, {"best_known_cost": 2579, "cost": 3530, "expected_gap": 0.40318, "family": "a", "name": "a280", "optimality_gap": 0.368748, "residual_gap": -0.034432}, {"best_known_cost": 629, "cost": 784, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.246423, "residual_gap": -0.007631}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.886718`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.267129`, mean selected residual gap `0.085263`.
- Adaptation efficiency `-0.028087` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001629}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.004952}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.140392`, synthetic `0.001628`, combined `0.089932`.
- Accepted-epoch count `2`, mean accepted code novelty `0.787879`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.258194`, size bias `0.120322`, and failure concentration `0.17235`.
- Replay selection diversity `0.201683`, mean selected expected gap `0.306411`, mean selected residual gap `-0.048111`.
- Adaptation efficiency `0.051766` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.140392` across 7 instances; family means: ch=0.109168, kroD=0.125106, pcb=0.24164, pr=0.160338, rd=0.143995, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3333, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.292361, "residual_gap": -0.10981}, {"best_known_cost": 14379, "cost": 18147, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.262049, "residual_gap": -0.059462}, {"best_known_cost": 629, "cost": 760, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.208267, "residual_gap": -0.058824}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301724`, mean selected residual gap `0.048265`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.000853}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.001975}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Analysis

## Main Evidence: Held-Out TSPLIB and Synthetic Holdout Gaps (Optimality and Transfer)

| Condition                         | Replay Type                  | Mean Synthetic Gap | Mean Transfer Gap | Mean TSPLIB Gap | Transfer Rank (Lower Better) | TSPLIB Rank (Lower Better) |
|----------------------------------|------------------------------|--------------------|-------------------|-----------------|------------------------------|----------------------------|
| **phase6_diversity_weighted_replay** | Diversity-weighted Replay     | 0.006169           | **0.050608**      | **0.076002**    | **1**                        | **1**                      |
| phase6_failure_replay            | Failure Replay                | 0.0                | 0.077501          | 0.121787        | 3                            | 3                          |
| phase6_stratified_random_replay | Stratified Random Replay      | 0.001628           | 0.078326          | 0.122153        | 4                            | 4                          |
| phase6_diversity_failure_replay | Diversity + Failure Replay    | 0.001628           | 0.089932          | 0.140392        | 5                            | 5                          |
| phase6_no_replay                | No Replay                    | 0.003941           | 0.069575          | 0.10708         | 2                            | 2                          |
| phase6_random_replay            | Random Replay                | 0.064916           | 0.159398          | 0.213387        | 8                            | 8                          |
| phase6_residual_failure_replay  | Residual Failure Replay       | 0.064916           | 0.159398          | 0.213387        | 8                            | 8                          |
| phase6_random_replay_compression| Random Replay + Compression   | 0.064916           | 0.159398          | 0.213387        | 8                            | 8                          |
| phase6_diversity_failure_replay_compression | Diversity + Failure Replay + Compression | 0.064916 | 0.159398 | 0.213387 | 8 | 8 |

- **phase6_diversity_weighted_replay** shows the best transfer (lowest gaps on both held-out TSPLIB and synthetic holdout) and best held-out TSPLIB optimality gap.
- Failure replay (phase6_failure_replay) improves synthetic holdout gap to zero but shows moderate transfer gap and TSPLIB gap, slightly worse than no replay condition.
- Random based replays and residual failure replay show significant degradation on transfer metrics and held-out performance.
- Compression-aware versions lose code novelty (mean_code_novelty=0) and do not improve transfer or gaps over their non-compressed counterparts.

## Replay Archive Analysis (Diversity, Hardness, Size Bias, Replay Failure Concentration)

| Condition                         | Archive Key        | Archive Size | Descriptor Diversity | Mean Hardness | Size Bias   | Replay Failure Concentration (mean/final) | Replay Selection Diversity | Final Behavior Profile  |
|----------------------------------|--------------------|--------------|----------------------|---------------|-------------|------------------------------------------|----------------------------|-----------------------|
| phase6_no_replay                | experience_archive | 30           | 0.236772             | 0.185832      | ~0.0        | 0.0 / 0.0                               | 0.0                        | clustered_constructor |
| phase6_random_replay            | experience_archive | 31           | 0.236772             | 0.214847      | ~0.0        | 0.19457 / 0.16                         | 0.262174                   | balanced              |
| phase6_failure_replay          | worst_archive      | 29           | 0.171206             | 0.23931       | 0.120322    | 0.221051 / 0.219955                     | 0.188305                   | clustered_constructor |
| phase6_random_replay_compression| experience_archive | 31           | 0.236772             | 0.214847      | ~0.0        | 0.19457 / 0.16                         | 0.262174                   | balanced              |
| phase6_stratified_random_replay| experience_archive | 30           | 0.236772             | 0.156985      | ~0.0        | 0.221162 / 0.251701                     | 0.187367                   | clustered_constructor |
| phase6_diversity_weighted_replay| experience_archive | 28           | 0.236772             | 0.181434      | ~0.0        | 0.130039 / 0.102041                     | 0.263651                   | clustered_constructor |
| phase6_residual_failure_replay | experience_archive | 31           | 0.149653             | 0.33856       | 0.094391    | 0.17024 / 0.291666                       | 0.177489                   | balanced              |
| phase6_diversity_failure_replay | worst_archive      | 29           | 0.174718             | 0.258194      | 0.120322    | 0.17235 / 0.174603                      | 0.201683                   | clustered_constructor |
| phase6_diversity_failure_replay_compression | worst_archive | 31      | 0.174718             | 0.348017      | 0.120322    | 0.17024 / 0.170068                     | 0.199284                   | balanced              |

- Replay diversity is highest for the best transfer condition (diversity_weighted_replay) and no_replay (both ~0.237).
- Hardness is generally higher for conditions selecting failure or residual failure archives (0.24–0.35) but the highest hardness coincides with poor transfer and gaps (residual_failure_replay with 0.338 or diversity_failure_replay_compression with 0.348).
- Size bias is near-zero in experience archive-based replay; failure archive conditions show positive size bias (~0.12).
- Failure concentration is low in no_replay (0.0), moderate in diversity_weighted_replay (~0.13), and higher (~0.17–0.25) for failure or random replay conditions.

## Code Novelty and Complexity

| Condition                         | Mean Code Novelty | Last Code Novelty | Mean Complexity |
|----------------------------------|-------------------|-------------------|-----------------|
| phase6_diversity_weighted_replay| 0.760188          | 0.662355          | 0.76            |
| phase6_failure_replay          | 0.648022          | 0.648022          | 0.76            |
| phase6_stratified_random_replay| 0.850377          | 0.850377          | 0.76            |
| phase6_no_replay                | 0.794158          | 0.853692          | 0.76            |
| phase6_random_replay            | 0.857086          | 0.830563          | 0.56            |
| phase6_random_replay_compression| 0.0               | 0.0               | 0.56            |
| phase6_residual_failure_replay | 0.0               | 0.648022          | 0.56            |
| phase6_diversity_failure_replay| 0.787879          | 0.787879          | 0.76            |
| phase6_diversity_failure_replay_compression| 0.0 | 0.0               | 0.56            |

- Compression-aware conditions (random replay + compression, diversity failure replay + compression) show zero code novelty with no transfer improvement.
- The best transfer condition (diversity_weighted_replay) maintains high code novelty and complexity.
- Random replay conditions have lower complexity (0.56) than others (mostly 0.76).

## Replay Mechanism Insights

- **Diversity-Weighted Replay** balances high archive diversity (~0.237), low failure concentration (~0.13), and moderate hardness (~0.18), achieving highest transfer and best TSPLIB optimality.
- **Failure Replay** concentrates on failure cases with higher hardness (0.24) and size bias (~0.12) but achieves zero synthetic gap yet moderate transfer and TSPLIB gaps.
- **Random Replay** with or without compression has higher failure concentration (~0.19) and selection diversity (~0.26), but poorest transfer and TSPLIB gaps.
- **Residual Failure Replay** has low diversity (~0.15), highest hardness (0.34), and high failure concentration (~0.17–0.29), but worst gaps, indicating overfitting or narrow focus.
- Compression pressures eliminate code novelty without transfer benefits.

## Final Takeaways

- **phase6_diversity_weighted_replay** is the best transfer condition, showing the smallest gaps on held-out TSPLIB (0.076) and synthetic holdout (0.006) with low transfer gap (0.051) and highest code novelty among top performers. Archive diversity and moderate hardness support balanced learning.
- The **phase6_failure_replay** condition excels in synthetic holdout (0 gap), but has lower transfer and TSPLIB generalization than diversity-weighted replay.
- Random and residual failure replays have worse transfer performance and held-out optimality gaps despite some having higher failure concentration and selection diversity.
- Compression-aware replay variants sacrifice code novelty without improving transfer, suggesting a detrimental effect on learning.
- Code novelty positively correlates with transfer performance; conditions with zero novelty (compression) perform worse.
- Hardness and size bias alone do not guarantee transfer; balanced diversity and failure concentration are important.
- No replay performs reasonably but inferior to diversity-weighted replay in transfer gaps and TSPLIB performance.
- Lexical novelty (code novelty) is maintained in successful replay strategies but not in compression-aware runs.
- There is no evidence that residual failure replay or compressed replay produces superior transfer despite their algorithmic difference.

---

# Conclusion

- Prioritize **phase6_diversity_weighted_replay** for best transfer generalization, balancing replay archive diversity, failure concentration, and code novelty.
- Failure replay improves synthetic holdout optimality gap but not overall transfer relative to diversity-weighted replay.
- Compression-aware replay reduces code novelty with no transfer gain.
- Failure concentration and hardness should be balanced; high value does not ensure better transfer.
- Random replay provides least transfer benefit.
- Lexical novelty corresponds here with transfer, but no isolated algorithmic invention from code novelty alone is indicated.

This conservative interpretation endorses **diversity-weighted replay** as the optimal replay mechanism for broad transfer in this benchmark suite.
