# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay`.
- Best TSPLIB holdout gap: `phase6_failure_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_012905_j
- started_at_local: 2026-05-19 01:29:05
- finished_at_local: 2026-05-19 01:48:51
- duration_hhmm: 00:20
- duration_seconds: 1185.681
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.160766 | 0.0 | 0.102306 | 0.236772 | 0.185883 | 0.0 | 0.760766 | 0.76 | 0.050113 |
| phase6_random_replay | random | score_only | False | 0.083902 | 0.0 | 0.053392 | 0.236772 | 0.178507 | 0.19457 | 0.820652 | 0.76 | 0.136695 |
| phase6_failure_replay | failure | score_only | False | 0.078198 | 0.015447 | 0.055379 | 0.171206 | 0.294015 | 0.274247 | 0.719608 | 0.76 | 0.053724 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.131834 | 0.010343 | 0.087655 | 0.236772 | 0.150143 | 0.221162 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.190499 | 0.033002 | 0.133227 | 0.236772 | 0.172063 | 0.157119 | 0.0 | 0.76 | 0.0 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.145882 | 0.0 | 0.092834 | 0.077942 | 0.242231 | 0.285362 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.080999 | 0.0 | 0.051545 | 0.171206 | 0.209742 | 0.172748 | 0.859193 | 0.76 | 0.04023 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.130448 | 0.001628 | 0.083604 | 0.171206 | 0.234072 | 0.174426 | 0.671538 | 0.76 | 0.017196 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.160766`, synthetic `0.0`, combined `0.102306`.
- Accepted-epoch count `2`, mean accepted code novelty `0.760766`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.185883`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.050113` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.160766` across 7 instances; family means: ch=0.122254, kroD=0.144736, pcb=0.215073, pr=0.313464, rd=0.160177, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19165, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.332847, "residual_gap": 0.011336}, {"best_known_cost": 629, "cost": 791, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.257552, "residual_gap": 0.0}, {"best_known_cost": 2579, "cost": 3126, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.212098, "residual_gap": -0.191392}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.083902`, synthetic `0.0`, combined `0.053392`.
- Accepted-epoch count `2`, mean accepted code novelty `0.820652`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.178507`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133681`, mean selected residual gap `-0.004349`.
- Adaptation efficiency `0.136695` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.083902` across 7 instances; family means: ch=0.039798, kroD=0.03602, pcb=0.189688, pr=0.114295, rd=0.102528, st=0.065185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 882, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.402226, "residual_gap": 0.145946}, {"best_known_cost": 2579, "cost": 3364, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.304382, "residual_gap": -0.099108}, {"best_known_cost": 7542, "cost": 9469, "expected_gap": 0.243888, "family": "berlin", "name": "berlin52", "optimality_gap": 0.255503, "residual_gap": 0.011615}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.078198`, synthetic `0.015447`, combined `0.055379`.
- Accepted-epoch count `3`, mean accepted code novelty `0.719608`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.294015`, size bias `0.120322`, and failure concentration `0.274247`.
- Replay selection diversity `0.128153`, mean selected expected gap `0.273212`, mean selected residual gap `0.064074`.
- Adaptation efficiency `0.053724` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.078198` across 7 instances; family means: ch=0.052096, kroD=0.088382, pcb=0.144511, pr=0.087769, rd=0.049937, st=0.072593.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 2959, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.147344, "residual_gap": -0.256301}, {"best_known_cost": 629, "cost": 671, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.066773, "residual_gap": -0.187917}, {"best_known_cost": 14379, "cost": 14660, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.019542, "residual_gap": -0.301732}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132227`, mean selected residual gap `0.039138`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402249, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.000931}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.317296, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.011517}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.131834`, synthetic `0.010343`, combined `0.087655`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.150143`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237946`, mean selected residual gap `-0.055009`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.131834` across 7 instances; family means: ch=0.092641, kroD=0.184653, pcb=0.238942, pr=0.116615, rd=0.102528, st=0.094815.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18613, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.294457, "residual_gap": -0.034272}, {"best_known_cost": 2579, "cost": 3209, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.244281, "residual_gap": -0.157658}, {"best_known_cost": 7542, "cost": 8338, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.105542, "residual_gap": -0.139565}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.190499`, synthetic `0.033002`, combined `0.133227`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.172063`, size bias `8.3e-05`, and failure concentration `0.157119`.
- Replay selection diversity `0.274872`, mean selected expected gap `0.15729`, mean selected residual gap `-0.00731`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190499` across 7 instances; family means: ch=0.171058, kroD=0.218465, pcb=0.242625, pr=0.289241, rd=0.144753, st=0.096296.
- Panel `synthetic_holdout` mean gap `0.033002` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.132009, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3565, "expected_gap": 0.400853, "family": "a", "name": "a280", "optimality_gap": 0.382319, "residual_gap": -0.018534}, {"best_known_cost": 7542, "cost": 9318, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.235481, "residual_gap": -0.009626}, {"best_known_cost": 14379, "cost": 16827, "expected_gap": 0.328131, "family": "lin", "name": "lin105", "optimality_gap": 0.170248, "residual_gap": -0.157883}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.145882`, synthetic `0.0`, combined `0.092834`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.077942`, mean hardness `0.242231`, size bias `0.068632`, and failure concentration `0.285362`.
- Replay selection diversity `0.111482`, mean selected expected gap `0.274076`, mean selected residual gap `0.050022`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.145882` across 7 instances; family means: ch=0.134096, kroD=0.201747, pcb=0.234038, pr=0.227184, rd=0.042604, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3548, "expected_gap": 0.399923, "family": "a", "name": "a280", "optimality_gap": 0.375727, "residual_gap": -0.024196}, {"best_known_cost": 14379, "cost": 18519, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.28792, "residual_gap": -0.041714}, {"best_known_cost": 7542, "cost": 9202, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.220101, "residual_gap": -0.024927}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.080999`, synthetic `0.0`, combined `0.051545`.
- Accepted-epoch count `2`, mean accepted code novelty `0.859193`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.209742`, size bias `0.120322`, and failure concentration `0.172748`.
- Replay selection diversity `0.192793`, mean selected expected gap `0.298621`, mean selected residual gap `-0.088238`.
- Adaptation efficiency `0.04023` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.080999` across 7 instances; family means: ch=0.092737, kroD=0.045788, pcb=0.17799, pr=0.036113, rd=0.04311, st=0.078519.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 848, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.348172, "residual_gap": 0.081081}, {"best_known_cost": 2579, "cost": 3409, "expected_gap": 0.398294, "family": "a", "name": "a280", "optimality_gap": 0.32183, "residual_gap": -0.076464}, {"best_known_cost": 14379, "cost": 18879, "expected_gap": 0.322762, "family": "lin", "name": "lin105", "optimality_gap": 0.312956, "residual_gap": -0.009806}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.130448`, synthetic `0.001628`, combined `0.083604`.
- Accepted-epoch count `2`, mean accepted code novelty `0.671538`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.234072`, size bias `0.120322`, and failure concentration `0.174426`.
- Replay selection diversity `0.200297`, mean selected expected gap `0.304087`, mean selected residual gap `-0.066205`.
- Adaptation efficiency `0.017196` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.130448` across 7 instances; family means: ch=0.113073, kroD=0.073307, pcb=0.193607, pr=0.250418, rd=0.064475, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18909, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.315043, "residual_gap": -0.007121}, {"best_known_cost": 2579, "cost": 3388, "expected_gap": 0.39969, "family": "a", "name": "a280", "optimality_gap": 0.313687, "residual_gap": -0.086003}, {"best_known_cost": 7542, "cost": 9604, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.273402, "residual_gap": 0.03678}]

## Judge Appendix
# Analysis of Replay-Aware TSP Benchmark Suite

## Summary of Key Conditions
- **Best held-out TSPLIB gap:** `phase6_failure_replay` (0.078198)
- **Best synthetic holdout gap:** `phase6_no_replay` (0.0)
- **Best transfer gap (aggregate):** `phase6_diversity_failure_replay` (0.051545)
- Total conditions evaluated: 9

---

## Transfer Performance (Primary Evidence)

| Condition                         | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Replay Mode             | Selection Mode |
|----------------------------------|-----------------|--------------------|-------------------|------------------------|----------------|
| phase6_no_replay                 | 0.1608          | 0.0                | 0.1023            | none                   | score_only     |
| phase6_random_replay             | 0.0839          | 0.0                | 0.0534            | random                 | score_only     |
| phase6_failure_replay            | **0.0782**      | 0.0154             | 0.0554            | failure                | score_only     |
| phase6_random_replay_compression | 0.2134          | 0.0649             | 0.1594            | random                 | novelty_gate   |
| phase6_stratified_random_replay | 0.1318          | 0.0103             | 0.0877            | stratified_random      | score_only     |
| phase6_diversity_weighted_replay | 0.1905          | 0.0330             | 0.1332            | diversity_weighted     | score_only     |
| phase6_residual_failure_replay   | 0.1459          | 0.0                | 0.0928            | residual_failure       | score_only     |
| phase6_diversity_failure_replay  | 0.0810          | 0.0                | **0.0515**        | diversity_failure      | score_only     |
| phase6_diversity_failure_replay_compression | 0.1304  | 0.0016             | 0.0836            | diversity_failure      | novelty_gate   |

- **Interpretation:**
  - The *lowest* TSPLIB held-out gap is with **phase6_failure_replay** (0.0782), closely followed by **phase6_diversity_failure_replay** (0.0810).
  - The *lowest* mean transfer gap is with **phase6_diversity_failure_replay** (0.0515), indicating strongest generalization on transfer tasks.
  - The *best* synthetic holdout gap is 0 or near-zero for several conditions, particularly **phase6_no_replay**, indicating synthetic data is easier or well-covered.
  - Conditions with compression pressure (**phase6_random_replay_compression**) show deteriorated transfer and held-out gaps.

## Replay Archive Characteristics and Mechanism Insights

| Condition                        | Replay Failure Concentration (Mean) | Archive Descriptor Diversity | Archive Hardness | Archive Size Bias | Replay Selection Diversity | Adaptation Efficiency |
|---------------------------------|------------------------------------|------------------------------|------------------|-------------------|----------------------------|-----------------------|
| phase6_no_replay                | 0.0                                | 0.2368                       | 0.1859           | ~0                | 0.0                        | 0.05                  |
| phase6_random_replay            | 0.1946                             | 0.2368                       | 0.1785           | ~0                | 0.262                      | 0.1367                |
| phase6_failure_replay           | 0.2742                             | 0.1712                       | 0.2940           | 0.1203            | 0.128                      | 0.0537                |
| phase6_random_replay_compression| 0.1946                             | 0.2368                       | 0.2124           | ~0                | 0.262                      | 0.0                   |
| phase6_stratified_random_replay | 0.2212                             | 0.2368                       | 0.1501           | ~0                | 0.187                      | 0.0                   |
| phase6_diversity_weighted_replay| 0.1571                             | 0.2368                       | 0.1721           | ~0                | 0.275                      | 0.0                   |
| phase6_residual_failure_replay  | 0.2854                             | 0.0779                       | 0.2422           | 0.0686            | 0.111                      | 0.0                   |
| phase6_diversity_failure_replay | 0.1727                             | 0.1712                       | 0.2341           | 0.1203            | 0.200                      | 0.0402                |
| phase6_diversity_failure_replay_compression | 0.1744                 | 0.1712                       | 0.2341           | 0.1203            | 0.200                      | 0.0172                |

- **Interpretation:**
  - Failure replay conditions (**phase6_failure_replay**, **phase6_diversity_failure_replay**) have higher **archive hardness** and **replay failure concentration**, suggesting focused replay on challenging instances.
  - Non-replay or random replay have higher **descriptor diversity** but lower hardness.
  - Compression pressure reduces **complexity** (e.g., phase6_random_replay_compression complexity 0.56 vs 0.76 others) and increases **transfer gap**.
  - Diversity-weighted replay conditions maintain moderate diversity and hardness.
  - Replay selection diversity is highest in **phase6_diversity_weighted_replay** and **phase6_random_replay**.

## Code Novelty vs. Transfer

| Condition                         | Last Code Novelty | Mean Code Novelty | Transfer Performance (Mean Transfer Gap) |
|----------------------------------|-------------------|-------------------|------------------------------------------|
| phase6_no_replay                 | 0.7608            | 0.7608            | 0.1023                                   |
| phase6_random_replay             | 0.8207            | 0.8207            | 0.0534                                   |
| phase6_failure_replay            | 0.7466            | 0.7196            | 0.0554                                   |
| phase6_random_replay_compression | 0.0               | 0.0               | 0.1594                                   |
| phase6_stratified_random_replay | 0.0               | 0.0               | 0.0877                                   |
| phase6_diversity_weighted_replay | 0.0               | 0.0               | 0.1332                                   |
| phase6_residual_failure_replay   | 0.0               | 0.0               | 0.0928                                   |
| phase6_diversity_failure_replay  | 0.8592            | 0.8592            | 0.0515                                   |
| phase6_diversity_failure_replay_compression | 0.6715   | 0.6715            | 0.0836                                   |

- **Interpretation:**
  - Conditions with highest code novelty (no replay, random replay, failure replay) do not consistently yield best transfer.
  - **phase6_diversity_failure_replay** achieves the best transfer with also high code novelty.
  - Some conditions (e.g., compression based replay, stratified, diversity-weighted without code novelty) have lower novelty but varying transfer, suggesting novelty alone is not sufficient for transfer improvements.

---

## Summary and Recommendations

1. **Best transfer and generalization:**
   - **phase6_diversity_failure_replay** achieves the best transfer gap (0.0515) and near-best heldout TSPLIB gap (0.0810) with moderate archive hardness (0.234) and replay selection diversity.
   - **phase6_failure_replay** has the best heldout TSPLIB gap (0.0782) and moderate transfer (0.0554) but lower code novelty compared to diversity_failure_replay.

2. **Replay archive characteristics:**
   - Failure-based replay strategies focus on harder instances and concentrate on replay failures, correlating with better generalization.
   - Diversity-weighted methods increase replay selection variety but sometimes at cost of higher residual gaps or transfer gap.

3. **Compression pressure:**
   - Compression degrades both transfer and heldout performance despite reducing complexity, seen in **phase6_random_replay_compression**.

4. **Code novelty vs. transfer:**
   - High code novelty alone does not guarantee better transfer; focused replay on hard failures with diversity balancing appears more effective.

---

# Conclusions

- Prioritize **phase6_diversity_failure_replay** for best overall transfer.
- Failure replay targeting hardest instances enhances generality, especially with diversity-aware selection.
- Compression-aware replay currently harms transfer and optimality.
- Code novelty trends do not strongly correlate with transfer; replay mechanism and archive content quality are more informative.

---

# Additional Notes

- Mean training gaps are generally higher than test/transfer gaps due to difficulty.
- Residual gaps (difference between expected and actual optimality gaps) show that failure replay concentrates on challenging yet learnable instances.
- Synthetic holdouts tend to be easier, showing near-zero gaps across conditions.

---

*End of analysis.*
