# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_no_replay`.
- Best TSPLIB holdout gap: `phase6_no_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_040959_r
- started_at_local: 2026-05-19 04:09:59
- finished_at_local: 2026-05-19 04:30:35
- duration_hhmm: 00:21
- duration_seconds: 1236.776
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.078538 | 0.0 | 0.049979 | 0.236772 | 0.1501 | 0.0 | 0.799532 | 0.76 | 0.025584 |
| phase6_random_replay | random | score_only | False | 0.104797 | 0.003941 | 0.068122 | 0.236772 | 0.175118 | 0.19457 | 0.850208 | 0.76 | 0.113967 |
| phase6_failure_replay | failure | score_only | False | 0.099242 | 0.0 | 0.063154 | 0.171206 | 0.300914 | 0.261637 | 0.786883 | 0.76 | 0.034508 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.195726 | 0.010343 | 0.128314 | 0.236772 | 0.163361 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.131903 | 0.0 | 0.083938 | 0.236772 | 0.159309 | 0.221162 | 0.829235 | 0.76 | 0.043764 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.133808 | 0.0 | 0.085151 | 0.236772 | 0.163657 | 0.157984 | 0.0 | 0.76 | 0.0 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.851031 | 0.56 | -0.029265 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.101901 | 0.0 | 0.064846 | 0.171206 | 0.269935 | 0.171012 | 0.78994 | 0.76 | 0.037351 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.175893 | 0.0 | 0.111932 | 0.171206 | 0.293959 | 0.172748 | 0.723666 | 0.76 | 0.02042 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.078538`, synthetic `0.0`, combined `0.049979`.
- Accepted-epoch count `4`, mean accepted code novelty `0.799532`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.1501`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.025584` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.078538` across 7 instances; family means: ch=0.026933, kroD=0.03602, pcb=0.219642, pr=0.114295, rd=0.100759, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3104, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.203567, "residual_gap": -0.197209}, {"best_known_cost": 629, "cost": 691, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.098569, "residual_gap": -0.158983}, {"best_known_cost": 7542, "cost": 8121, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.07677, "residual_gap": -0.168337}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.104797`, synthetic `0.003941`, combined `0.068122`.
- Accepted-epoch count `2`, mean accepted code novelty `0.850208`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.175118`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133843`, mean selected residual gap `0.016398`.
- Adaptation efficiency `0.113967` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.104797` across 7 instances; family means: ch=0.078327, kroD=0.154363, pcb=0.187365, pr=0.053782, rd=0.076233, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3376, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.309035, "residual_gap": -0.091741}, {"best_known_cost": 7542, "cost": 9473, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.256033, "residual_gap": 0.011005}, {"best_known_cost": 14379, "cost": 17487, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.216149, "residual_gap": -0.110828}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.099242`, synthetic `0.0`, combined `0.063154`.
- Accepted-epoch count `4`, mean accepted code novelty `0.786883`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.300914`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.21241`, mean selected expected gap `0.304752`, mean selected residual gap `0.011468`.
- Adaptation efficiency `0.034508` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.099242` across 7 instances; family means: ch=0.072119, kroD=0.063492, pcb=0.229962, pr=0.099677, rd=0.096587, st=0.060741.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3458, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.34083, "residual_gap": -0.061109}, {"best_known_cost": 14379, "cost": 16397, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.140344, "residual_gap": -0.184616}, {"best_known_cost": 7542, "cost": 8194, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.086449, "residual_gap": -0.154469}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.195726`, synthetic `0.010343`, combined `0.128314`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.163361`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132156`, mean selected residual gap `-0.000676`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.195726` across 7 instances; family means: ch=0.259572, kroD=0.250305, pcb=0.241778, pr=0.176019, rd=0.157649, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3452, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.338503, "residual_gap": -0.065142}, {"best_known_cost": 14379, "cost": 19077, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.326726, "residual_gap": 0.004965}, {"best_known_cost": 629, "cost": 755, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.200318, "residual_gap": -0.0531}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.131903`, synthetic `0.0`, combined `0.083938`.
- Accepted-epoch count `2`, mean accepted code novelty `0.829235`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.159309`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236082`, mean selected residual gap `-0.026283`.
- Adaptation efficiency `0.043764` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.131903` across 7 instances; family means: ch=0.134471, kroD=0.224289, pcb=0.173618, pr=0.096349, rd=0.115676, st=0.044444.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3421, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.326483, "residual_gap": -0.080031}, {"best_known_cost": 14379, "cost": 18147, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.262049, "residual_gap": -0.059225}, {"best_known_cost": 629, "cost": 754, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.198728, "residual_gap": -0.057552}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.133808`, synthetic `0.0`, combined `0.085151`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.163657`, size bias `8.3e-05`, and failure concentration `0.157984`.
- Replay selection diversity `0.26167`, mean selected expected gap `0.167861`, mean selected residual gap `-0.016493`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.133808` across 7 instances; family means: ch=0.096662, kroD=0.125998, pcb=0.205561, pr=0.216931, rd=0.169659, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19215, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.336324, "residual_gap": 0.01313}, {"best_known_cost": 629, "cost": 810, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.287758, "residual_gap": 0.033704}, {"best_known_cost": 2579, "cost": 3232, "expected_gap": 0.406049, "family": "a", "name": "a280", "optimality_gap": 0.253199, "residual_gap": -0.15285}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.851031`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.264849`, mean selected residual gap `0.087544`.
- Adaptation efficiency `-0.029265` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.404963, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003645}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00644}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.101901`, synthetic `0.0`, combined `0.064846`.
- Accepted-epoch count `3`, mean accepted code novelty `0.78994`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.269935`, size bias `0.120322`, and failure concentration `0.171012`.
- Replay selection diversity `0.195273`, mean selected expected gap `0.301938`, mean selected residual gap `-0.025534`.
- Adaptation efficiency `0.037351` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.101901` across 7 instances; family means: ch=0.114136, kroD=0.060862, pcb=0.249813, pr=0.075001, rd=0.062326, st=0.037037.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3470, "expected_gap": 0.402482, "family": "a", "name": "a280", "optimality_gap": 0.345483, "residual_gap": -0.056999}, {"best_known_cost": 14379, "cost": 19140, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.331108, "residual_gap": 0.009305}, {"best_known_cost": 7542, "cost": 8516, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.129143, "residual_gap": -0.103925}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.175893`, synthetic `0.0`, combined `0.111932`.
- Accepted-epoch count `2`, mean accepted code novelty `0.723666`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.293959`, size bias `0.120322`, and failure concentration `0.172748`.
- Replay selection diversity `0.194842`, mean selected expected gap `0.298989`, mean selected residual gap `0.000536`.
- Adaptation efficiency `0.02042` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.175893` across 7 instances; family means: ch=0.124171, kroD=0.223537, pcb=0.270491, pr=0.216866, rd=0.19646, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3469, "expected_gap": 0.401086, "family": "a", "name": "a280", "optimality_gap": 0.345095, "residual_gap": -0.055991}, {"best_known_cost": 7542, "cost": 9237, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.224741, "residual_gap": -0.011085}, {"best_known_cost": 629, "cost": 743, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.18124, "residual_gap": -0.082671}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Results

## Overview

- **Best overall condition** (held-out TSPLIB, synthetic holdout, and transfer):  
  `phase6_no_replay`  
  - Mean TSPLIB gap: 7.85%  
  - Mean transfer gap: 5.0%  
  - Mean synthetic gap: 0%  
  - No replay used (replay_mode: none)  
  - Archive size: 28 with moderate diversity (0.24) and medium hardness (0.17)  
  - Code novelty high (~0.80 mean)

- Nine total experimental conditions varying replay modes and selection modes.

---

## Transfer Performance (Hold-out TSPLIB & Synthetic Holdout gaps)

| Condition                           | TSPLIB Gap | Transfer Gap | Synthetic Gap | Replay Mode                  | Code Novelty (mean) | Notes              |
|-----------------------------------|------------|--------------|--------------|-----------------------------|---------------------|--------------------|
| phase6_no_replay                  | 0.0785     | 0.0500       | 0.0000       | none                        | 0.799               | Best transfer + optimality |
| phase6_random_replay              | 0.1048     | 0.0681       | 0.0039       | random                      | 0.850               | Worse than no replay in gaps |
| phase6_failure_replay             | 0.0992     | 0.0632       | 0.0000       | failure                     | 0.787               | Slightly better than random replay |
| phase6_random_replay_compression  | 0.1957     | 0.1283       | 0.0103       | random (compression aware)  | 0.000               | Significant drop in code novelty, worse gaps |
| phase6_stratified_random_replay  | 0.1319     | 0.0839       | 0.0000       | stratified_random           | 0.829               | Moderate performance |
| phase6_diversity_weighted_replay | 0.1338     | 0.0852       | 0.0000       | diversity_weighted          | 0.000               | Code novelty dropped, worse gaps than no replay |
| phase6_residual_failure_replay   | 0.2134     | 0.1594       | 0.0649       | residual_failure            | 0.851               | Worst gaps, failure concentration highest |
| phase6_diversity_failure_replay  | 0.1019     | 0.0648       | 0.0000       | diversity_failure           | 0.790               | Comparable to failure replay |
| phase6_diversity_failure_replay_compression | 0.1759 | 0.1119  | 0.0000       | diversity_failure (compression) | 0.724            | Moderate degradation compared to non-compression |

### Key points on transfer gaps:
- **No replay** is best on both synthetic and TSPLIB holdouts and transfer gaps.
- Replay conditions generally worsen transfer and TSPLIB gaps.
- Compression-aware replay conditions (random and diversity_failure) lead to poorer code novelty and worse transfer gaps.
- Residual_failure replay shows poorest transfer gaps and highest failure concentration.

---

## Replay Archive Analysis (Diversity, Hardness, Size Bias, Failure Concentration)

| Condition                          | Archive Diversity | Archive Hardness | Archive Size Bias | Final Replay Failure Concentration | Mean Replay Failure Concentration | Mean Replay Selection Diversity |
|----------------------------------|-------------------|------------------|-------------------|-----------------------------------|----------------------------------|---------------------------------|
| phase6_no_replay                 | 0.240             | 0.174            | 0.0               | 0.0                               | 0.0                              | 0.0                             |
| phase6_random_replay             | 0.240             | 0.185            | 0.0               | 0.16                              | 0.195                            | 0.262                           |
| phase6_failure_replay            | 0.175             | 0.310            | 0.125             | 0.31                              | 0.26                             | 0.212                           |
| phase6_random_replay_compression | 0.240             | 0.186            | 0.0               | 0.16                              | 0.195                            | 0.262                           |
| phase6_stratified_random_replay | 0.240             | 0.187            | 0.0               | 0.25                              | 0.22                             | 0.187                           |
| phase6_diversity_weighted_replay| 0.240             | 0.192            | 0.0               | 0.10                              | 0.16                             | 0.26                            |
| phase6_residual_failure_replay  | 0.150             | 0.339            | 0.094             | 0.33                              | 0.29                             | 0.177                           |
| phase6_diversity_failure_replay | 0.175             | 0.309            | 0.125             | 0.33                              | 0.17                             | 0.20                            |
| phase6_diversity_failure_replay_compression | 0.175 | 0.315  | 0.125             | 0.17                              | 0.17                             | 0.19                            |

### Observations:
- Failure replay modes (failure, residual_failure, diversity_failure) result in:
  - Higher archive hardness (0.31-0.34) vs no replay (~0.17-0.19)
  - Larger size bias (~0.12) vs none.
  - Higher failure concentration (final up to 0.33) indicating replay focuses on difficult failures.
- Random and stratified replay maintain archive diversity near baseline (0.24).
- Residual failure replay has the lowest archive diversity (0.15) and highest hardness.
- Compression pressure in replay archives leads to code novelty reduction.

---

## Code Novelty and Complexity

| Condition                          | Mean Code Novelty | Last Code Novelty | Mean Complexity | Notes                                 |
|----------------------------------|-------------------|-------------------|-----------------|-------------------------------------|
| phase6_no_replay                 | 0.80              | 0.73              | 0.76            | Highest code novelty, good complexity |
| phase6_random_replay             | 0.85              | 0.85              | 0.76            | High novelty, no code novelty drop  |
| phase6_failure_replay            | 0.79              | 0.79              | 0.76            | Moderate novelty                    |
| phase6_random_replay_compression | 0.00              | 0.00              | 0.76            | Significant novelty loss due to compression |
| phase6_stratified_random_replay | 0.83              | 0.83              | 0.76            | High novelty, no complexity penalty |
| phase6_diversity_weighted_replay| 0.00              | 0.00              | 0.76            | Zero novelty, no improvement in transfer |
| phase6_residual_failure_replay  | 0.85              | 0.86              | 0.56            | High novelty, lower complexity      |
| phase6_diversity_failure_replay | 0.79              | 0.80              | 0.76            | Moderate novelty                    |
| phase6_diversity_failure_replay_compression | 0.72   | 0.72              | 0.76            | Drop in novelty with compression    |

---

## Mechanism Analysis for Replay Modes

- **phase6_no_replay** (no replay) yields best transfer and held-out performance, maintaining high code novelty and moderate archive diversity/hardness.

- **Random replay** (phase6_random_replay and compression version):
  - Increases final archive hardness but leads to increased gaps on held-out and transfer datasets relative to no replay.
  - Compression significantly reduces code novelty and increases gaps, indicating a trade-off.

- **Failure replay** (phase6_failure_replay):
  - Produces archives with much higher hardness and some size bias.
  - Failure concentration is moderate-high (~0.3), indicating focus on failure cases.
  - Transfer and holdout gaps notably worse than no replay.
  - Code novelty somewhat lower but not absent.

- **Residual failure replay**:
  - Highest archive hardness and failure concentration.
  - Worst transfer and held-out gaps.
  - Code novelty remains high.
  - Complexity lower than others, possibly indicating overfitting or less diverse behaviors.

- **Diversity-weighted replay**:
  - Maintains archive diversity but results in zero code novelty and no transfer improvement.
  - Holds worse gaps on hold-out datasets.
  - Indicates lexical novelty without effective algorithmic transfer.

- **Diversity failure and its compression variant**:
  - Balanced archive diversity and hardness with moderate failure concentration.
  - Compression lowers code novelty and worsens transfer performance.
  - Non-compression version performs better than random or failure replay but worse than no replay.

- **Stratified random replay**:
  - Moderate improvements in replay selection diversity.
  - Transfer and held-out gaps better than random replay but still worse than no replay.
  - Code novelty remains high.

---

## Conclusions

- The **best transfer and optimality** are achieved by the no replay condition (`phase6_no_replay`).
- All replay methods increase the difficulty (hardness) and failure concentration of the training sets but lead to worse generalization (higher transfer and heldout gaps).
- Use of compression in archive management reduces code novelty and degrades transfer performance, especially in random and diversity failure replay.
- High **code novelty** does not guarantee better transfer; for example, failure and residual failure replay show high novelty but poor transfer.
- Lexical/code novelty decline with replay compression without corresponding transfer gain suggests lexical novelty measures may mislead regarding genuine algorithmic improvement.
- **Replay modes focusing on failures or residual failures create archives with size bias and increased hardness but not better transfer**.
- Diversity-weighted replay achieves archive diversity but fails to improve transfer or preserve code novelty.
- Replay selection diversity is higher in random and diversity-weighted replay but does not correlate with better transfer performance.

---

# Final Notes

- Prioritize `phase6_no_replay` for transfer and solution quality.
- Replay strategies induce more challenging but less generalizable training, increasing failure concentration and hardness.
- Compression reduces code novelty significantly, harming transfer.
- Lexical or archive diversity does not equate to algorithmic invention or improved generalization unless matched by transfer metrics.
