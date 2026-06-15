# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_failure_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_010943_i
- started_at_local: 2026-05-19 01:09:43
- finished_at_local: 2026-05-19 01:29:04
- duration_hhmm: 00:19
- duration_seconds: 1160.547
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.152008 | 0.0 | 0.096732 | 0.236772 | 0.158253 | 0.0 | 0.629021 | 0.76 | 0.034627 |
| phase6_random_replay | random | score_only | False | 0.101948 | 0.0 | 0.064876 | 0.236772 | 0.157262 | 0.19457 | 0.638472 | 0.76 | 0.060473 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.913465 | 0.56 | -0.027264 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.157489 | 0.003941 | 0.101653 | 0.236772 | 0.172033 | 0.19457 | 0.798354 | 0.76 | 0.044768 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.174134 | 0.0 | 0.110813 | 0.236772 | 0.163224 | 0.221162 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.130039 | 0.894426 | 0.56 | -0.027845 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.098826 | 0.014284 | 0.068083 | 0.038798 | 0.122645 | 0.194445 | 0.869774 | 0.76 | 0.099436 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.084911 | 0.0 | 0.054034 | 0.171206 | 0.266037 | 0.175969 | 0.658181 | 0.76 | 0.097602 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.158373 | 0.010343 | 0.104544 | 0.171206 | 0.269051 | 0.172748 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.152008`, synthetic `0.0`, combined `0.096732`.
- Accepted-epoch count `2`, mean accepted code novelty `0.629021`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.158253`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.034627` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.152008` across 7 instances; family means: ch=0.135771, kroD=0.074152, pcb=0.177813, pr=0.223347, rd=0.201643, st=0.115556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3174, "expected_gap": 0.40822, "family": "a", "name": "a280", "optimality_gap": 0.23071, "residual_gap": -0.17751}, {"best_known_cost": 14379, "cost": 17655, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.227832, "residual_gap": -0.097156}, {"best_known_cost": 629, "cost": 757, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.203498, "residual_gap": -0.054054}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.101948`, synthetic `0.0`, combined `0.064876`.
- Accepted-epoch count `2`, mean accepted code novelty `0.638472`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.157262`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133654`, mean selected residual gap `-0.011002`.
- Adaptation efficiency `0.060473` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.101948` across 7 instances; family means: ch=0.078705, kroD=0.157979, pcb=0.226653, pr=0.056214, rd=0.039823, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3055, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.184568, "residual_gap": -0.219387}, {"best_known_cost": 629, "cost": 702, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.116057, "residual_gap": -0.140223}, {"best_known_cost": 14379, "cost": 15411, "expected_gap": 0.325433, "family": "lin", "name": "lin105", "optimality_gap": 0.071771, "residual_gap": -0.253662}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.913465`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.308783`, mean selected residual gap `0.066974`.
- Adaptation efficiency `-0.027264` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.403722, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.002404}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.004952}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.157489`, synthetic `0.003941`, combined `0.101653`.
- Accepted-epoch count `2`, mean accepted code novelty `0.798354`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.172033`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.13247`, mean selected residual gap `0.011597`.
- Adaptation efficiency `0.044768` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.157489` across 7 instances; family means: ch=0.144398, kroD=0.158261, pcb=0.187207, pr=0.213889, rd=0.160936, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3487, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.352074, "residual_gap": -0.050873}, {"best_known_cost": 629, "cost": 850, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.351351, "residual_gap": 0.097933}, {"best_known_cost": 14379, "cost": 18111, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.259545, "residual_gap": -0.061966}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.174134`, synthetic `0.0`, combined `0.110813`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.163224`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237473`, mean selected residual gap `-0.012027`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.174134` across 7 instances; family means: ch=0.17463, kroD=0.226026, pcb=0.180945, pr=0.273172, rd=0.164349, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3356, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.30128, "residual_gap": -0.100891}, {"best_known_cost": 629, "cost": 806, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.281399, "residual_gap": 0.025119}, {"best_known_cost": 14379, "cost": 18147, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.262049, "residual_gap": -0.064789}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.894426`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.266358`, mean selected expected gap `0.168427`, mean selected residual gap `0.025262`.
- Adaptation efficiency `-0.027845` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001629}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137043}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.001836}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.098826`, synthetic `0.014284`, combined `0.068083`.
- Accepted-epoch count `2`, mean accepted code novelty `0.869774`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.038798`, mean hardness `0.122645`, size bias `0.029507`, and failure concentration `0.194445`.
- Replay selection diversity `0.077595`, mean selected expected gap `0.258116`, mean selected residual gap `0.061398`.
- Adaptation efficiency `0.099436` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.098826` across 7 instances; family means: ch=0.052307, kroD=0.068846, pcb=0.120466, pr=0.18483, rd=0.107838, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.014284` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10207, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.353355, "residual_gap": 0.112437}, {"best_known_cost": 2579, "cost": 3401, "expected_gap": 0.405273, "family": "a", "name": "a280", "optimality_gap": 0.318728, "residual_gap": -0.086545}, {"best_known_cost": 629, "cost": 752, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.195548, "residual_gap": -0.066455}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.084911`, synthetic `0.0`, combined `0.054034`.
- Accepted-epoch count `3`, mean accepted code novelty `0.658181`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.266037`, size bias `0.120322`, and failure concentration `0.175969`.
- Replay selection diversity `0.198205`, mean selected expected gap `0.305588`, mean selected residual gap `-0.034026`.
- Adaptation efficiency `0.097602` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.084911` across 7 instances; family means: ch=0.063492, kroD=0.109843, pcb=0.192583, pr=0.034523, rd=0.087484, st=0.042963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3201, "expected_gap": 0.405351, "family": "a", "name": "a280", "optimality_gap": 0.241179, "residual_gap": -0.164172}, {"best_known_cost": 629, "cost": 700, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.112878, "residual_gap": -0.154213}, {"best_known_cost": 14379, "cost": 15974, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.110926, "residual_gap": -0.210835}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.158373`, synthetic `0.010343`, combined `0.104544`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.269051`, size bias `0.120322`, and failure concentration `0.172748`.
- Replay selection diversity `0.196929`, mean selected expected gap `0.300716`, mean selected residual gap `-0.024669`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.158373` across 7 instances; family means: ch=0.117164, kroD=0.181366, pcb=0.229863, pr=0.247053, rd=0.11378, st=0.102222.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3343, "expected_gap": 0.405739, "family": "a", "name": "a280", "optimality_gap": 0.296239, "residual_gap": -0.1095}, {"best_known_cost": 14379, "cost": 18560, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.290771, "residual_gap": -0.030503}, {"best_known_cost": 629, "cost": 743, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.18124, "residual_gap": -0.082671}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Suite Results

## Overview
- **Best holdout TSPLIB gap**: **phase6_diversity_failure_replay** (mean gap 0.0849)
- **Best synthetic holdout gap**: **phase6_no_replay** (mean gap 0.0)
- **Best transfer gap (combined)**: **phase6_diversity_failure_replay** (mean gap 0.0540)
- Total conditions: 9, including variants with and without replay, and variants of replay modes.

## Transfer Performance (Primary Evidence)

| Condition                          | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Replay Mode                | Selection Mode   | Archive Diversity | Archive Hardness | Replay Failure Concentration |
|----------------------------------|-----------------|--------------------|-------------------|---------------------------|------------------|-------------------|------------------|------------------------------|
| phase6_diversity_failure_replay  | **0.084911**    | 0.0                | **0.054034**      | diversity_failure         | score_only       | 0.174718          | 0.319583         | 0.175969                     |
| phase6_no_replay                 | 0.152008        | 0.0                | 0.096732          | none                      | score_only       | 0.240179          | 0.179316         | 0.0                          |
| phase6_random_replay             | 0.101948        | 0.0                | 0.064876          | random                    | score_only       | 0.240179          | 0.187794         | 0.19457                      |
| phase6_random_replay_compression | 0.157489        | 0.003941           | 0.101653          | random                    | novelty_gate     | 0.240179          | 0.194657         | 0.19457                      |
| phase6_failure_replay            | 0.213387        | 0.064916           | 0.159398          | failure                   | score_only       | 0.174718          | 0.34902          | 0.261637                     |
| phase6_stratified_random_replay | 0.174134        | 0.0                | 0.110813          | stratified_random         | score_only       | 0.240179          | 0.189768         | 0.25                         |
| phase6_diversity_weighted_replay| 0.213387        | 0.064916           | 0.159398          | diversity_weighted        | score_only       | 0.240179          | 0.212361         | 0.174603                     |
| phase6_residual_failure_replay  | 0.098826        | 0.014284           | 0.068083          | residual_failure          | score_only       | 0.155191          | 0.342131         | 0.194445                     |
| phase6_diversity_failure_replay_compression | 0.158373 | 0.010343         | 0.104544          | diversity_failure         | novelty_gate     | 0.174718          | 0.340218         | 0.170068                     |

### Interpretations:
- **phase6_diversity_failure_replay** leads in TSPLIB holdout and transfer gaps, showing best generalization to real TSPLIB and synthetic instances.
- **phase6_no_replay** yields zero synthetic holdout gaps but worse gaps on TSPLIB, indicating lack of transfer robustness.
- Replay modes involving failure cases (diversity_failure, failure_replay) generally improve transfer gap compared to no replay or random replay.
- Compression-aware replay (random_replay_compression, diversity_failure_replay_compression) slightly reduces final archive diversity but does not improve transfer gap compared to diversity_failure_replay.

## Replay Archive Characteristics & Mechanism Analysis

| Condition                         | Archive Size | Archive Descriptor Diversity | Archive Hardness | Archive Size Bias | Replay Failure Concentration | Replay Selection Diversity | Adaptation Efficiency |
|---------------------------------|--------------|------------------------------|------------------|-------------------|------------------------------|----------------------------|-----------------------|
| phase6_diversity_failure_replay | 30           | 0.1747                       | 0.3196           | 0.125             | 0.17597                      | 0.198                      | 0.098                 |
| phase6_no_replay                | 28           | 0.2402                       | 0.1793           | 0.0               | 0.0                          | 0.0                        | 0.035                 |
| phase6_random_replay            | 30           | 0.2402                       | 0.1878           | 0.0               | 0.19457                      | 0.262                      | 0.060                 |
| phase6_failure_replay           | 31           | 0.1747                       | **0.3490**       | **0.125**         | **0.262**                    | 0.178                      | -0.027                |
| phase6_stratified_random_replay | 30           | 0.2402                       | 0.1898           | 0.0               | 0.2517                       | 0.187                      | 0.0                   |
| phase6_diversity_weighted_replay| 31           | 0.2402                       | 0.2124           | 0.0               | 0.1300                       | 0.266                      | -0.028                |
| phase6_residual_failure_replay | 28           | 0.1552                       | 0.3421           | 0.061             | 0.1944                       | 0.078                      | 0.099                 |
| phase6_random_replay_compression| 30           | 0.2402                       | 0.1947           | 0.0               | 0.19457                      | 0.262                      | 0.045                 |
| phase6_diversity_failure_replay_compression| 31 | 0.1747                   | 0.3402           | 0.125             | 0.1701                       | 0.197                      | 0.0                   |

- Replay archive diversity is highest without selection pressure or diversity weighting (e.g., no_replay and random replay).
- Failure replay methods concentrate replay failures (high failure concentration ~0.17-0.26), indicating replay is focused on tough cases.
- Adaptation efficiency is negative for failure replay and diversity_weighted replay, suggesting less efficient learning despite failure focus.
- Residual_failure_replay achieves the highest adaptation efficiency (0.099) and maintains moderate transfer and TSPLIB gaps.
- Compression pressure lowers archive diversity but does not clearly improve transfer performance.

## Code Novelty & Complexity

| Condition                         | Last Code Novelty | Mean Code Novelty | Mean Complexity |
|---------------------------------|-------------------|-------------------|-----------------|
| phase6_diversity_failure_replay | 0.90              | 0.66              | 0.76            |
| phase6_no_replay                | 0.63              | 0.63              | 0.76            |
| phase6_random_replay            | 0.64              | 0.64              | 0.76            |
| phase6_failure_replay           | 0.90              | 0.91              | 0.56            |
| phase6_stratified_random_replay | 0.0               | 0.0               | 0.76            |
| phase6_diversity_weighted_replay| 0.87              | 0.66              | 0.56            |
| phase6_residual_failure_replay | 0.87              | 0.87              | 0.76            |
| phase6_random_replay_compression| 0.80              | 0.80              | 0.76            |
| phase6_diversity_failure_replay_compression| 0.0      | 0.0               | 0.76            |

- Conditions with improved transfer gaps (e.g., diversity_failure replay) do not systematically show code novelty gains when compression or novelty gating is used.
- Stratified random replay and diversity_failure replay compression show zero code novelty but moderate transfer gaps.
- Algorithmic invention is not strongly indicated by lexical code novelty, matching the rule to prioritize deterministic metrics.
- Complexity varies modestly; failure replay conditions have lower complexity (0.56) but higher archive hardness.

## Concentration and Diversity of Failure Replay

- Failure replay conditions show higher replay failure concentration (0.17-0.26), indicating focused replay around challenging failures.
- Diversity-weighted replay achieves decent replay selection diversity (~0.20-0.27) along with moderate failure concentration.
- Residual failure replay shows lower failure concentration (~0.10-0.19) and lower selection diversity, which may affect transfer.

## Key Insights

- **Best Transfer:** phase6_diversity_failure_replay achieves the best transfer gap (0.054) and lowest TSPLIB gap (0.085), indicating effective transfer.
- **No Replay Baseline:** phase6_no_replay has zero synthetic gap but higher TSPLIB gap (0.152), showing limited transfer ability without replay.
- **Failure Replay vs Random Replay:** Failure replay increases archive hardness and failure concentration but does not always improve adaptation efficiency and transfer compared to random replay.
- **Residual Failure Replay:** Yields good adaptation efficiency and low transfer gap (~0.068), with slightly lower archive diversity.
- **Code Novelty:** Declines with compression and novelty gate selection, but transfer gaps can improve or remain stable, indicating code novelty is not a proxy for transfer quality.
- **Diversity and Hardness:** The best transfer condition balances archive diversity (~0.17) and hardness (~0.32), favoring inclusion of difficult instances with moderate diversity.

---

# Conclusion and Recommendations

- Prefer **phase6_diversity_failure_replay** as the benchmark condition due to its superior transfer and held-out TSPLIB optimality gaps.
- The **no replay** condition, while achieving perfect synthetic gaps, underperforms on real TSPLIB transfer, marking replay as beneficial.
- Failure-focused replay methods improve transfer but may reduce adaptation efficiency; balancing replay diversity and failure concentration is critical.
- Compression or novelty gating can reduce code novelty without harming transfer, suggesting that reducing lexical novelty is not detrimental.
- Recommend deeper mechanism analysis on replay failure concentration and diversity to optimize replay buffer construction.
- Do not conflate code novelty with algorithmic innovation: effective transfer was achieved where code novelty varied, supporting focus on deterministic transfer and gap metrics.
