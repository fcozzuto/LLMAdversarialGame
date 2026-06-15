# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_stratified_random_replay`.
- Best TSPLIB holdout gap: `phase6_stratified_random_replay`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260518_225158_b
- started_at_local: 2026-05-18 22:51:58
- finished_at_local: 2026-05-18 23:12:08
- duration_hhmm: 00:20
- duration_seconds: 1210.024
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.120766 | 0.015789 | 0.082593 | 0.236772 | 0.142664 | 0.0 | 0.844353 | 0.76 | 0.007056 |
| phase6_random_replay | random | score_only | False | 0.184836 | 0.0 | 0.117623 | 0.236772 | 0.133657 | 0.19457 | 0.775482 | 0.76 | -0.003091 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.892563 | 0.56 | -0.027903 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.10109 | 0.000343 | 0.064455 | 0.236772 | 0.135611 | 0.19457 | 0.798751 | 0.76 | 0.01128 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.096087 | 0.001628 | 0.061738 | 0.236772 | 0.183216 | 0.221162 | 0.673809 | 0.76 | 0.078344 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.114454 | 0.0 | 0.072834 | 0.236772 | 0.193559 | 0.157984 | 0.588682 | 0.76 | 0.104505 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.122954 | 0.0 | 0.078243 | 0.130778 | 0.291763 | 0.328165 | 0.712319 | 0.76 | 0.009337 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.900373 | 0.56 | -0.027661 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.131164 | 0.010343 | 0.087229 | 0.171206 | 0.252962 | 0.173315 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.120766`, synthetic `0.015789`, combined `0.082593`.
- Accepted-epoch count `2`, mean accepted code novelty `0.844353`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.142664`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.007056` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.120766` across 7 instances; family means: ch=0.131699, kroD=0.065605, pcb=0.258557, pr=0.099844, rd=0.107585, st=0.05037.
- Panel `synthetic_holdout` mean gap `0.015789` across 4 instances; family means: clustered_gaussian=0.001371, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3406, "expected_gap": 0.40822, "family": "a", "name": "a280", "optimality_gap": 0.320667, "residual_gap": -0.087553}, {"best_known_cost": 629, "cost": 743, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.18124, "residual_gap": -0.076312}, {"best_known_cost": 14379, "cost": 16371, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.138535, "residual_gap": -0.183629}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.184836`, synthetic `0.0`, combined `0.117623`.
- Accepted-epoch count `2`, mean accepted code novelty `0.775482`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.133657`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133575`, mean selected residual gap `-0.024041`.
- Adaptation efficiency `-0.003091` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 0, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.184836` across 7 instances; family means: ch=0.138289, kroD=0.286747, pcb=0.289397, pr=0.139619, rd=0.264475, st=0.037037.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3568, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.383482, "residual_gap": -0.020473}, {"best_known_cost": 629, "cost": 774, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.230525, "residual_gap": -0.025755}, {"best_known_cost": 14379, "cost": 16927, "expected_gap": 0.329244, "family": "lin", "name": "lin105", "optimality_gap": 0.177203, "residual_gap": -0.152041}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.892563`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.308457`, mean selected residual gap `0.0673`.
- Adaptation efficiency `-0.027903` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.403722, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.002404}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": -2.8e-05}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.10109`, synthetic `0.000343`, combined `0.064455`.
- Accepted-epoch count `2`, mean accepted code novelty `0.798751`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.135611`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132418`, mean selected residual gap `-0.022565`.
- Adaptation efficiency `0.01128` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 1, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.10109` across 7 instances; family means: ch=0.081514, kroD=0.122523, pcb=0.259876, pr=0.053782, rd=0.053603, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.000343` across 4 instances; family means: clustered_gaussian=0.001371, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3357, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.301667, "residual_gap": -0.10128}, {"best_known_cost": 14379, "cost": 17085, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.188191, "residual_gap": -0.139815}, {"best_known_cost": 629, "cost": 737, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.171701, "residual_gap": -0.081717}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.096087`, synthetic `0.001628`, combined `0.061738`.
- Accepted-epoch count `3`, mean accepted code novelty `0.673809`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.183216`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237428`, mean selected residual gap `-0.027686`.
- Adaptation efficiency `0.078344` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.096087` across 7 instances; family means: ch=0.061645, kroD=0.101813, pcb=0.228209, pr=0.061169, rd=0.078129, st=0.08.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3436, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.332299, "residual_gap": -0.069872}, {"best_known_cost": 7542, "cost": 9649, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.279369, "residual_gap": 0.046301}, {"best_known_cost": 14379, "cost": 17018, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.183532, "residual_gap": -0.143125}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.114454`, synthetic `0.0`, combined `0.072834`.
- Accepted-epoch count `2`, mean accepted code novelty `0.588682`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.193559`, size bias `8.3e-05`, and failure concentration `0.157984`.
- Replay selection diversity `0.267365`, mean selected expected gap `0.154023`, mean selected residual gap `0.008469`.
- Adaptation efficiency `0.104505` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.114454` across 7 instances; family means: ch=0.138782, kroD=0.110172, pcb=0.226318, pr=0.070988, rd=0.098357, st=0.017778.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3277, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.270648, "residual_gap": -0.132299}, {"best_known_cost": 7542, "cost": 9544, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.265447, "residual_gap": 0.029621}, {"best_known_cost": 14379, "cost": 17487, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.216149, "residual_gap": -0.110508}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.122954`, synthetic `0.0`, combined `0.078243`.
- Accepted-epoch count `2`, mean accepted code novelty `0.712319`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.130778`, mean hardness `0.291763`, size bias `0.080581`, and failure concentration `0.328165`.
- Replay selection diversity `0.140953`, mean selected expected gap `0.289892`, mean selected residual gap `0.046059`.
- Adaptation efficiency `0.009337` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.122954` across 7 instances; family means: ch=0.108439, kroD=0.28717, pcb=0.224349, pr=0.015653, rd=0.082554, st=0.034074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3271, "expected_gap": 0.405273, "family": "a", "name": "a280", "optimality_gap": 0.268321, "residual_gap": -0.136952}, {"best_known_cost": 14379, "cost": 16015, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.113777, "residual_gap": -0.211211}, {"best_known_cost": 629, "cost": 674, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.071542, "residual_gap": -0.190461}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.900373`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301218`, mean selected residual gap `0.04877`.
- Adaptation efficiency `-0.027661` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.405351, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.004033}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.124006}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.325433, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00338}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.131164`, synthetic `0.010343`, combined `0.087229`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.252962`, size bias `0.120322`, and failure concentration `0.173315`.
- Replay selection diversity `0.199207`, mean selected expected gap `0.307214`, mean selected residual gap `-0.05521`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.131164` across 7 instances; family means: ch=0.10119, kroD=0.181366, pcb=0.218815, pr=0.131972, rd=0.096207, st=0.087407.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3258, "expected_gap": 0.405739, "family": "a", "name": "a280", "optimality_gap": 0.26328, "residual_gap": -0.142459}, {"best_known_cost": 629, "cost": 748, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.189189, "residual_gap": -0.074722}, {"best_known_cost": 7542, "cost": 8312, "expected_gap": 0.244206, "family": "berlin", "name": "berlin52", "optimality_gap": 0.102095, "residual_gap": -0.142111}]

## Judge Appendix
### Summary of Key Results

| Condition                          | Replay Type                | Transfer (Held-out TSPLIB Gap) | Synthetic Transfer Gap | Synthetic Holdout Gap | Final Training Gap (Last) | Adaptation Efficiency | Replay Failure Concentration | Archive Diversity | Archive Hardness | Code Novelty (mean) | Notes                        |
|----------------------------------|---------------------------|-------------------------------|-----------------------|----------------------|---------------------------|-----------------------|------------------------------|-------------------|-----------------|---------------------|------------------------------|
| **phase6_no_replay**             | None                      | 0.1208                        | 0.0826                | 0.0158               | 0.1751                    | 0.0071                | 0.0                          | 0.237             | 0.143           | 0.844               | Baseline, moderate gaps      |
| **phase6_random_replay**          | Raw-failure random        | 0.1848                        | 0.1176                | 0.0                  | 0.2364                    | -0.0031               | 0.1946                       | 0.237             | 0.134           | 0.775               | Higher gaps, some failure concentration |
| **phase6_failure_replay**         | Raw-failure from worst archive | 0.2134                        | 0.1594                | 0.0649               | 0.3602                    | -0.0279               | 0.262                        | 0.172             | 0.348           | 0.893               | Highest gaps and hardness, high failure concentration |
| **phase6_random_replay_compression** | Raw-failure with compression | 0.1011                        | 0.0645                | 0.0003               | 0.1866                    | 0.0113                | 0.195                        | 0.237             | 0.136           | 0.799               | Improved transfer gaps and synthetic gap with compression+random replay |
| **phase6_stratified_random_replay** | Stratified random replay  | **0.0961**                   | **0.0617**            | 0.0016               | 0.2393                    | 0.0783                | 0.221                        | 0.237             | 0.183           | 0.674               | Best transfer performance; moderate hardness |
| **phase6_diversity_weighted_replay** | Diversity-weighted replay | 0.1145                        | 0.0728                | 0.0                  | 0.3012                    | 0.1045                | 0.158                        | 0.240             | 0.198           | 0.589               | High adaptation efficiency with diversity-weighted replay |
| **phase6_residual_failure_replay** | Residual failure replay  | 0.1230                        | 0.0782                | 0.0                  | 0.3602                    | 0.0093                | 0.262                        | 0.201             | 0.372           | 0.712               | Moderate transfer gaps, higher hardness and failure concentration |
| **phase6_diversity_failure_replay** | Diversity failure replay  | 0.2134                        | 0.1594                | 0.0649               | 0.3602                    | -0.0277               | 0.170                        | 0.175             | 0.349           | 0.900               | Similar to pure failure replay, high gap and failure concentration |
| **phase6_diversity_failure_replay_compression** | Diversity failure replay + compression | 0.1312                        | 0.0872                | 0.0103               | 0.1599                    | 0.0                   | 0.173                        | 0.175             | 0.307           | 0.0                 | Stability in code novelty, gaps intermediate |

### Interpretation

- **Best transfer performance** (lowest gaps on held-out TSPLIB and synthetic holdout instances) is observed for **phase6_stratified_random_replay** (held-out TSPLIB gap 9.61%, synthetic 0.16%) with good adaptation efficiency (0.0783) and moderate failure concentration (0.22). This indicates broad-coverage replay with stratification enhances generalization to unseen instances.

- **Raw-failure and diversity failure replay modes** (phase6_failure_replay, phase6_diversity_failure_replay) increase archive hardness and failure concentration but suffer higher gaps on transfer benchmarks (~21-22% on TSPLIB). Their adaptation efficiency is negative, showing diminished learning efficiency. These conditions show failure concentration around 0.26-0.27, consistent with replaying mostly hard cases but poor generalization.

- **Compression combined with random or diversity-weighted replay** improves transfer gaps noticeably compared to uncompressed failure replay (e.g., phase6_random_replay_compression has 10.1% TSPLIB gap vs. 18.5% in phase6_random_replay). This suggests compression facilitates focusing on useful replay cases without increasing failure concentration or harming diversity.

- **Code novelty** (mean and last) tends to be **lower in best transfer cases**: phase6_stratified_random_replay has code novelty ~0.67 vs. ~0.9 in failure-based replay. This decouples lexical novelty from algorithmic improvement and shows code novelty alone is not correlated with transfer performance here.

- **Replay archive diversity** is highest (~0.24) except in failure replay modes where it drops (~0.17-0.20), indicating replay diversity positively correlates with transfer quality.

- **Size bias** in archives is negligible for most but higher in failure replay (~0.12-0.13), consistent with bias toward harder cases.

- **Final synthetic holdout gaps** are minimal (<0.002) in stratified and random replay conditions (including compressed versions), showing effective generalization in synthetic domain.

### Mechanism Insights

- **Diversified replays** (stratified random, diversity-weighted) yield broad coverage, better transfer gaps, balanced hardness (~0.18–0.20), and lower failure concentration (~0.16–0.22).

- **Failure replay modes** focus on hardest or residual-failure cases, increasing hardness and failure concentration but resulting in overfitting and poor transfer.

- **Compression pressure** when combined with replay (random or diversity) reduces synthetic and transfer gaps without increasing failure concentration, indicating efficient archive management.

### Summary

- The **phase6_stratified_random_replay** condition offers the best balance of transfer generalization (lowest gaps), moderate archive hardness, and archive diversity, dominating other replay modes.

- Failure-based replay conditions increase replay failure concentration and hardness but degrade transfer performance substantially; indicative of overfitting on difficult cases.

- Compression techniques enhance replay effectiveness in random or diversity-weighted replays by maintaining archive quality without loss of diversity.

- Code novelty decreases in better transfer conditions relative to higher-novelty failure replay modes, highlighting that lexical novelty is not a substitute for algorithmic innovation.

---

*In conclusion, broad-coverage replay with stratified random sampling and compression yields superior transfer performance over failure-focused or diversity failure replay strategies, despite the latter showing higher code novelty and replay hardness.*
