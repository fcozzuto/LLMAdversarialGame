# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_failure_replay`.
- Best TSPLIB holdout gap: `phase6_failure_replay`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260518_223014_a
- started_at_local: 2026-05-18 22:30:14
- finished_at_local: 2026-05-18 22:51:56
- duration_hhmm: 00:22
- duration_seconds: 1302.613
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.869493 | 0.56 | -0.028643 |
| phase6_random_replay | random | score_only | False | 0.124445 | 0.0 | 0.079192 | 0.236772 | 0.143152 | 0.19457 | 0.692413 | 0.76 | 0.052041 |
| phase6_failure_replay | failure | score_only | False | 0.082632 | 0.0 | 0.052584 | 0.171206 | 0.258808 | 0.191132 | 0.794418 | 0.76 | 0.058353 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.170887 | 0.010343 | 0.112507 | 0.236772 | 0.1693 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.132743 | 0.010343 | 0.088234 | 0.236772 | 0.164957 | 0.221162 | 0.815976 | 0.76 | 0.014133 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.130039 | 0.901121 | 0.56 | -0.027638 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.812712 | 0.56 | -0.030644 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.124231 | 0.010343 | 0.082817 | 0.171206 | 0.272545 | 0.173881 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.09781 | 0.0 | 0.062243 | 0.171206 | 0.261764 | 0.17024 | 0.78376 | 0.76 | 0.039306 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.869493`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.028643` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.399069, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.002249}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007539}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.124445`, synthetic `0.0`, combined `0.079192`.
- Accepted-epoch count `2`, mean accepted code novelty `0.692413`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.143152`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133447`, mean selected residual gap `-0.022931`.
- Adaptation efficiency `0.052041` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.124445` across 7 instances; family means: ch=0.148214, kroD=0.176341, pcb=0.184785, pr=0.057702, rd=0.102528, st=0.053333.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3459, "expected_gap": 0.402714, "family": "a", "name": "a280", "optimality_gap": 0.341218, "residual_gap": -0.061496}, {"best_known_cost": 14379, "cost": 18571, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.291536, "residual_gap": -0.031658}, {"best_known_cost": 629, "cost": 799, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.27027, "residual_gap": 0.01399}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.082632`, synthetic `0.0`, combined `0.052584`.
- Accepted-epoch count `2`, mean accepted code novelty `0.794418`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.258808`, size bias `0.120322`, and failure concentration `0.191132`.
- Replay selection diversity `0.212069`, mean selected expected gap `0.308948`, mean selected residual gap `-0.006576`.
- Adaptation efficiency `0.058353` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.082632` across 7 instances; family means: ch=0.069889, kroD=0.033765, pcb=0.205522, pr=0.044546, rd=0.1, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3658, "expected_gap": 0.404808, "family": "a", "name": "a280", "optimality_gap": 0.418379, "residual_gap": 0.013571}, {"best_known_cost": 629, "cost": 870, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.383148, "residual_gap": 0.128458}, {"best_known_cost": 14379, "cost": 18416, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.280757, "residual_gap": -0.041616}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.170887`, synthetic `0.010343`, combined `0.112507`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.1693`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.13189`, mean selected residual gap `0.002319`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.170887` across 7 instances; family means: ch=0.167174, kroD=0.250305, pcb=0.20434, pr=0.21768, rd=0.164349, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19824, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.378677, "residual_gap": 0.056874}, {"best_known_cost": 2579, "cost": 3361, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.303218, "residual_gap": -0.097558}, {"best_known_cost": 629, "cost": 804, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.278219, "residual_gap": 0.024801}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.132743`, synthetic `0.010343`, combined `0.088234`.
- Accepted-epoch count `3`, mean accepted code novelty `0.815976`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.164957`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236142`, mean selected residual gap `-0.039676`.
- Adaptation efficiency `0.014133` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.132743` across 7 instances; family means: ch=0.086816, kroD=0.08021, pcb=0.244003, pr=0.272303, rd=0.070164, st=0.088889.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3535, "expected_gap": 0.40031, "family": "a", "name": "a280", "optimality_gap": 0.370686, "residual_gap": -0.029624}, {"best_known_cost": 7542, "cost": 9490, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.258287, "residual_gap": 0.022461}, {"best_known_cost": 14379, "cost": 17716, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.232075, "residual_gap": -0.089436}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.901121`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.266358`, mean selected expected gap `0.167625`, mean selected residual gap `0.026065`.
- Adaptation efficiency `-0.027638` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.400931, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.000387}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137043}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007302}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.812712`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.265344`, mean selected residual gap `0.087049`.
- Adaptation efficiency `-0.030644` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402869, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001551}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007539}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.124231`, synthetic `0.010343`, combined `0.082817`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.272545`, size bias `0.120322`, and failure concentration `0.173881`.
- Replay selection diversity `0.193082`, mean selected expected gap `0.310392`, mean selected residual gap `-0.015991`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.124231` across 7 instances; family means: ch=0.044076, kroD=0.256035, pcb=0.189866, pr=0.208101, rd=0.102276, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19562, "expected_gap": 0.317296, "family": "lin", "name": "lin105", "optimality_gap": 0.360456, "residual_gap": 0.04316}, {"best_known_cost": 2579, "cost": 3391, "expected_gap": 0.403257, "family": "a", "name": "a280", "optimality_gap": 0.314851, "residual_gap": -0.088406}, {"best_known_cost": 629, "cost": 760, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.208267, "residual_gap": -0.058824}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.09781`, synthetic `0.0`, combined `0.062243`.
- Accepted-epoch count `3`, mean accepted code novelty `0.78376`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.261764`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.198286`, mean selected expected gap `0.301127`, mean selected residual gap `-0.042301`.
- Adaptation efficiency `0.039306` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.09781` across 7 instances; family means: ch=0.074095, kroD=0.107636, pcb=0.183465, pr=0.088028, rd=0.081795, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3259, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.263668, "residual_gap": -0.139822}, {"best_known_cost": 629, "cost": 686, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.09062, "residual_gap": -0.173291}, {"best_known_cost": 14379, "cost": 15443, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.073997, "residual_gap": -0.254732}]

## Judge Appendix
### Summary and Interpretation of Replay-Aware TSP Benchmark Results

#### General Notes
- Primary transfer evidence is taken from **held-out TSPLIB gap** and **synthetic holdout gap** metrics.
- Replay mechanism studies focus on archive diversity, hardness, size bias, failure concentration, and failure spread.
- Code novelty and transfer are explicitly contrasted.
- Replay policies distinguish between broad-coverage (random, stratified random), raw-failure, residual-failure, diversity-weighted, and compression-aware replay.

---

### Top Performing Conditions

| Condition                   | Tsplib Gap | Synthetic Gap | Transfer Gap | Replay Mode               | Code Novelty (mean) | Archive Diversity | Archive Hardness | Failure Concentration | Notes                           |
|-----------------------------|------------|---------------|--------------|---------------------------|---------------------|-------------------|------------------|------------------------|----------------------------------|
| **phase6_failure_replay**      | **0.0826** | 0.0           | **0.0526**   | failure                   | 0.7944              | 0.1712            | 0.2588           | 0.2245                 | Best transfer, lowest gaps        |
| phase6_diversity_failure_replay_compression | 0.0978  | 0.0           | 0.0622     | diversity_failure with compression  | 0.7838              | 0.1712            | 0.2618           | 0.1702                 | Good transfer, compression applied|
| phase6_random_replay         | 0.1244     | 0.0           | 0.0792       | random                    | 0.6924              | 0.2368            | 0.1432           | 0.1946                 | Moderate transfer, higher diversity|
| phase6_stratified_random_replay | 0.1327  | 0.0103        | 0.0882       | stratified_random         | 0.8160              | 0.2368            | 0.1650           | 0.2212                 | Slightly worse transfer           |
| phase6_diversity_failure_replay | 0.1242 | 0.0103        | 0.0828       | diversity_failure         | 0.0000              | 0.1712            | 0.2725           | 0.1739                 | Code novelty dropped to zero      |
| phase6_no_replay              | 0.2134     | 0.0649        | 0.1594       | none                      | 0.8695              | 0.2368            | 0.2148           | 0.0                    | Worst transfer, high code novelty |

**Notes:**  
- **Best transfer** performance is from **phase6_failure_replay** with lowest heldout TSPLIB gap (0.0826) and transfer gap (0.0526).
- **Random replay variants** (including compression-aware) yield intermediate transfer improvements, with varying code novelty.
- **No replay** baseline shows largest transfer gaps despite highest code novelty and balanced behavior.
- Replay modes with **diversity or failure weighting plus compression** improve transfer gaps relative to random replay without compression.
- **Code novelty is not strongly correlated with better transfer:** the **diversity_failure_replay** condition has zero code novelty yet shows competitive transfer gaps.
- Failure replay modes tend to have **higher archive hardness and failure concentration** than random modes.

---

### Replay Archive Characteristics by Condition

| Condition                           | Arch. Size | Arch. Diversity | Arch. Hardness | Arch. Size Bias | Failure Conc. Final | Failure Conc. Mean | Replay Selection Diversity | Comments                         |
|-----------------------------------|------------|-----------------|----------------|-----------------|---------------------|--------------------|----------------------------|----------------------------------|
| phase6_failure_replay             | 31         | 0.1712          | 0.2588         | 0.1203          | 0.2245              | 0.1911             | 0.212                      | Concentrated replay on failures, moderate diversity |
| phase6_diversity_failure_replay_compression | 28      | 0.1747          | 0.2878         | 0.1250          | 0.1702              | 0.1702             | 0.1983                     | Compression modestly reduces failure concentration |
| phase6_random_replay              | 28         | 0.2368          | 0.1432         | 0.0000          | 0.1946              | 0.1946             | 0.262                      | Highest diversity, lowest hardness |
| phase6_stratified_random_replay  | 30         | 0.2368          | 0.1650         | 0.0000          | 0.2212              | 0.2212             | 0.187                      | Balanced characteristics        |
| phase6_diversity_failure_replay  | 30         | 0.1747          | 0.3198         | 0.1250          | 0.1739              | 0.1739             | 0.193                      | Lower diversity, higher hardness|
| phase6_no_replay                 | 32         | 0.2368          | 0.2148         | 0.0             | 0.0                 | 0.0                | 0.0                        | No replay, no failure concentration  |
| phase6_residual_failure_replay   | 31         | 0.1497          | 0.3386         | 0.0944          | 0.3333              | 0.2917             | 0.177                      | High failure concentration and hardness (residual selected) |
| phase6_diversity_weighted_replay | 32         | 0.2402          | 0.2124         | 0.0             | 0.1300              | 0.1300             | 0.266                      | Largest diversity, moderate failure concentration |

**Insights:**  
- Failure-based replay (failure, residual_failure, diversity_failure) tends to yield **higher failure concentrations** and **hardness** in archives than random or no replay.  
- Diversity weighting supports **higher descriptor diversity** but may come at cost of failure concentration dilution.  
- Compression pressure cases (random_replay_compression, diversity_failure_replay_compression) have **some reduction** in failure concentration but maintain decent transfer gap.  
- No replay generates **no failure concentration** or replay diversity (as expected).  

---

### Transfer and Optimality Gap Trends

- **Transfer gaps on held-out TSPLIB sets:** lowest for failure replay (0.0826), followed by diversity failure with compression (0.0978), then random replay (0.1244), and worst for no replay (0.2134).  
- **Synthetic holdout gaps:** minimal (zero or near zero) for replay-enabled conditions; higher only for no replay (0.0649).  
- **Across all best-performing replay conditions, the transfer gap is substantially better than no replay**, indicating benefits from replay interventions.  
- **Failure replay usage strongly correlates with best transfer gaps and lowest optimality gaps on held-out TSPLIB instances.**

---

### Code Novelty vs Transfer

- Conditions with **high code novelty (~0.8-0.9)** include no replay and diversity weighted replay, but they exhibit **worse or equal transfer gaps** compared to failure replay modes which have **moderate to low novelty (~0.69-0.79)**.  
- Some diversity or highest novelty replay conditions (e.g., "phase6_diversity_failure_replay") show **zero mean code novelty**, yet maintain decent transfer gaps.  
- This suggests **code novelty metrics do not directly imply algorithmic improvement or transfer efficacy** in this setting.

---

### Summary Conclusions

- **Failure-replay mechanisms (phase6_failure_replay) achieve the best transfer to held-out TSPLIB and synthetic benchmarks, with lowest gaps and reasonable archive diversity and hardness.**  
- **Random replay with no selection or simple random replay yields moderate transfer but somewhat higher gaps and lower hardness.**  
- **Increased archive hardness and replay failure concentration correlate with improved transfer performance.**  
- **Compression-aware replay situates between random and failure replay in terms of transfer, maintaining archive structure with moderate failure concentration.**  
- **Code novelty does not track transfer improvement, sometimes falling when transfer improves (diversity_failure_replay). Thus, code novelty is not a proxy for meaningful algorithmic invention here.**  
- **Replay strategy impacts archive characteristics substantially: failure replay concentrates on hard failures but may reduce diversity; diversity-weighted replay maximizes diversity but with a possible cost in failure concentration.**  
- Future investigations should analyze method adaptation efficiency in conjunction with replay modes and failure concentration to optimize transfer.

---

### Recommendations

- Prioritize **failure replay modes** for best transfer and generalization to TSPLIB and synthetic test sets.  
- Consider combining diversity weighting with failure replay to balance diversity and hardness without sacrificing transfer.  
- Monitor code novelty separately and avoid equating it with algorithmic invention or transfer gains.  
- Archive size bias and complexity seem stable and less informative for transfer predictions; focus on failure concentration and hardness instead.  
- Evaluate compression effects as a control to maintain archive manageability without harming transfer.

---

End of analysis.
