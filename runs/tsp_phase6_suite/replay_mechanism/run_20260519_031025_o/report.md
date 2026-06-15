# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay_compression`.
- Best TSPLIB holdout gap: `phase6_diversity_failure_replay_compression`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260519_031025_o
- started_at_local: 2026-05-19 03:10:25
- finished_at_local: 2026-05-19 03:30:26
- duration_hhmm: 00:20
- duration_seconds: 1201.324
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.905838 | 0.56 | -0.027494 |
| phase6_random_replay | random | score_only | False | 0.120553 | 0.0 | 0.076716 | 0.236772 | 0.158996 | 0.19457 | 0.840491 | 0.76 | 0.035159 |
| phase6_failure_replay | failure | score_only | False | 0.107837 | 0.0 | 0.068624 | 0.171206 | 0.267406 | 0.223419 | 0.817241 | 0.76 | 0.03749 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.12724 | 0.0 | 0.080971 | 0.236772 | 0.161067 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.105101 | 0.001628 | 0.067474 | 0.236772 | 0.185993 | 0.221162 | 0.837354 | 0.76 | 0.067865 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.149767 | 0.015447 | 0.100923 | 0.236772 | 0.16823 | 0.130039 | 0.871585 | 0.76 | 0.024334 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.108561 | 0.0 | 0.069084 | 0.0 | 0.068305 | 0.125 | 0.834977 | 0.76 | 0.028083 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.144815 | 0.010343 | 0.095916 | 0.171206 | 0.250257 | 0.172748 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.066881 | 0.0 | 0.042561 | 0.171206 | 0.228672 | 0.171012 | 0.597217 | 0.76 | 0.064947 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.905838`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.027494` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.399069, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.002249}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.006649}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.120553`, synthetic `0.0`, combined `0.076716`.
- Accepted-epoch count `2`, mean accepted code novelty `0.840491`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.158996`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133523`, mean selected residual gap `-0.00846`.
- Adaptation efficiency `0.035159` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.120553` across 7 instances; family means: ch=0.115412, kroD=0.214286, pcb=0.245441, pr=0.050805, rd=0.038812, st=0.063704.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19919, "expected_gap": 0.329244, "family": "lin", "name": "lin105", "optimality_gap": 0.385284, "residual_gap": 0.05604}, {"best_known_cost": 2579, "cost": 3355, "expected_gap": 0.402714, "family": "a", "name": "a280", "optimality_gap": 0.300892, "residual_gap": -0.101822}, {"best_known_cost": 7542, "cost": 9075, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.203262, "residual_gap": -0.029886}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.107837`, synthetic `0.0`, combined `0.068624`.
- Accepted-epoch count `3`, mean accepted code novelty `0.817241`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.267406`, size bias `0.120322`, and failure concentration `0.223419`.
- Replay selection diversity `0.191069`, mean selected expected gap `0.317017`, mean selected residual gap `-0.014486`.
- Adaptation efficiency `0.03749` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.107837` across 7 instances; family means: ch=0.095189, kroD=0.07697, pcb=0.183071, pr=0.130558, rd=0.086473, st=0.087407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3555, "expected_gap": 0.404808, "family": "a", "name": "a280", "optimality_gap": 0.378441, "residual_gap": -0.026367}, {"best_known_cost": 14379, "cost": 18422, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.281174, "residual_gap": -0.047667}, {"best_known_cost": 7542, "cost": 9536, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.264386, "residual_gap": 0.027022}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.12724`, synthetic `0.0`, combined `0.080971`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.161067`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132327`, mean selected residual gap `-0.000759`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.12724` across 7 instances; family means: ch=0.133763, kroD=0.15718, pcb=0.188093, pr=0.152978, rd=0.077497, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19018, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.322623, "residual_gap": -0.005383}, {"best_known_cost": 2579, "cost": 3389, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.314075, "residual_gap": -0.086701}, {"best_known_cost": 7542, "cost": 9644, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706, "residual_gap": 0.041342}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.105101`, synthetic `0.001628`, combined `0.067474`.
- Accepted-epoch count `2`, mean accepted code novelty `0.837354`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.185993`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237428`, mean selected residual gap `-0.001095`.
- Adaptation efficiency `0.067865` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.105101` across 7 instances; family means: ch=0.071031, kroD=0.124073, pcb=0.275021, pr=0.036113, rd=0.065107, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 9939, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.31782, "residual_gap": 0.084752}, {"best_known_cost": 2579, "cost": 3383, "expected_gap": 0.40031, "family": "a", "name": "a280", "optimality_gap": 0.311749, "residual_gap": -0.088561}, {"best_known_cost": 629, "cost": 777, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.235294, "residual_gap": -0.020986}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.149767`, synthetic `0.015447`, combined `0.100923`.
- Accepted-epoch count `2`, mean accepted code novelty `0.871585`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.16823`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.266361`, mean selected expected gap `0.167381`, mean selected residual gap `-0.019572`.
- Adaptation efficiency `0.024334` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.149767` across 7 instances; family means: ch=0.172957, kroD=0.235231, pcb=0.175036, pr=0.091865, rd=0.155879, st=0.044444.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3602, "expected_gap": 0.400931, "family": "a", "name": "a280", "optimality_gap": 0.396665, "residual_gap": -0.004266}, {"best_known_cost": 14379, "cost": 18384, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.278531, "residual_gap": -0.048126}, {"best_known_cost": 629, "cost": 796, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.265501, "residual_gap": 0.011447}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.108561`, synthetic `0.0`, combined `0.069084`.
- Accepted-epoch count `3`, mean accepted code novelty `0.834977`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.0`, mean hardness `0.068305`, size bias `0.028318`, and failure concentration `0.125`.
- Replay selection diversity `0.0`, mean selected expected gap `0.263849`, mean selected residual gap `0.009369`.
- Adaptation efficiency `0.028083` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 1, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.108561` across 7 instances; family means: ch=0.089905, kroD=0.065605, pcb=0.248828, pr=0.132019, rd=0.087737, st=0.045926.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3395, "expected_gap": 0.402869, "family": "a", "name": "a280", "optimality_gap": 0.316402, "residual_gap": -0.086467}, {"best_known_cost": 14379, "cost": 16970, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.180193, "residual_gap": -0.144795}, {"best_known_cost": 629, "cost": 670, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.065183, "residual_gap": -0.19682}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.144815`, synthetic `0.010343`, combined `0.095916`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.250257`, size bias `0.120322`, and failure concentration `0.172748`.
- Replay selection diversity `0.195273`, mean selected expected gap `0.303603`, mean selected residual gap `-0.04395`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.144815` across 7 instances; family means: ch=0.115101, kroD=0.211797, pcb=0.226003, pr=0.146876, rd=0.102528, st=0.096296.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3263, "expected_gap": 0.403257, "family": "a", "name": "a280", "optimality_gap": 0.265219, "residual_gap": -0.138038}, {"best_known_cost": 14379, "cost": 16132, "expected_gap": 0.325433, "family": "lin", "name": "lin105", "optimality_gap": 0.121914, "residual_gap": -0.203519}, {"best_known_cost": 7542, "cost": 8416, "expected_gap": 0.238849, "family": "berlin", "name": "berlin52", "optimality_gap": 0.115884, "residual_gap": -0.122965}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.066881`, synthetic `0.0`, combined `0.042561`.
- Accepted-epoch count `3`, mean accepted code novelty `0.597217`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.228672`, size bias `0.120322`, and failure concentration `0.171012`.
- Replay selection diversity `0.194758`, mean selected expected gap `0.304054`, mean selected residual gap `-0.070713`.
- Adaptation efficiency `0.064947` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 1, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.066881` across 7 instances; family means: ch=0.041555, kroD=0.103832, pcb=0.149868, pr=0.028477, rd=0.080657, st=0.022222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3435, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.331912, "residual_gap": -0.071578}, {"best_known_cost": 629, "cost": 766, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.217806, "residual_gap": -0.046105}, {"best_known_cost": 14379, "cost": 17442, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.213019, "residual_gap": -0.110842}]

## Judge Appendix
# Analysis of Replay-Aware TSP Benchmark Suite

## Summary of Main Metrics for Best Conditions

| Cond. Name                           | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Replay Mode              | Selection Mode   | Archive Diversity | Archive Hardness | Archive Size Bias | Failure Concentration | Code Novelty Mean | Code Novelty Last |
|------------------------------------|-----------------|--------------------|-------------------|-------------------------|------------------|-------------------|------------------|-------------------|-----------------------|-------------------|-------------------|
| phase6_no_replay                   | 0.213387        | 0.064916           | 0.159398          | none                    | score_only       | 0.237             | 0.215            | ~0                | 0                     | 0.906             | 0.885             |
| phase6_random_replay               | 0.120553        | 0.0                | 0.076716          | random                  | score_only       | 0.237             | 0.185            | ~0                | 0.194                 | 0.840             | 0.840             |
| phase6_failure_replay              | 0.107837        | 0.0                | 0.068624          | failure                 | score_only       | 0.172             | 0.267            | 0.125             | 0.223                 | 0.817             | 0.756             |
| phase6_random_replay_compression  | 0.127240        | 0.0                | 0.080971          | random                  | novelty_gate     | 0.237             | 0.214            | ~0                | 0.195                 | 0.0               | 0.0               |
| phase6_stratified_random_replay   | 0.105101        | 0.001628           | 0.067474          | stratified_random       | score_only       | 0.237             | 0.198            | ~0                | 0.221                 | 0.837             | 0.837             |
| phase6_diversity_weighted_replay  | 0.149767        | 0.015447           | 0.100923          | diversity_weighted      | score_only       | 0.237             | 0.192            | ~0                | 0.130                 | 0.872             | 0.872             |
| phase6_residual_failure_replay    | 0.108561        | 0.0                | 0.069084          | residual_failure        | score_only       | 0.0               | 0.273            | 0.113             | 0.125                 | 0.835             | 0.822             |
| phase6_diversity_failure_replay   | 0.144815        | 0.010343           | 0.095916          | diversity_failure       | score_only       | 0.172             | 0.309            | 0.125             | 0.170                 | 0.0               | 0.0               |
| phase6_diversity_failure_replay_compression | 0.066881 | 0.0     | 0.042561          | diversity_failure       | novelty_gate     | 0.172             | 0.257            | 0.125             | 0.171                 | 0.597             | 0.474             |

Best holdout TSPLIB gap and synthetic holdout gap correspond to **phase6_diversity_failure_replay_compression** (TSPLIB gap 0.0669) and **phase6_random_replay** (synthetic gap 0.0). The best transfer gap is also from **phase6_diversity_failure_replay_compression** (0.0426).

---

## Transfer Performance and Optimality-Gap Interpretation

- **Optimality gaps on held-out TSPLIB**:  
  The lowest mean gaps are observed for conditions with failure replay and diversity failure replay with compression (best ~6.7-10.8%), followed by random and stratified random replay conditions (~10.5-12%), and worst for no replay (~21%).  

- **Synthetic holdout gaps** (reflecting transfer to synthetic instances):  
  Best (zero or near zero) gaps occur under random replay and failure replay variants. Some small gaps exist in diversity-weighted replay conditions. Compression-aware replay combined with diversity_failure achieves zero synthetic holdout gap.  

- **Transfer gaps** (held-out TSPLIB mean gaps are generally higher than transfer gaps due to problem complexity):  
  Phase6_diversity_failure_replay_compression achieves the lowest transfer gap (0.043), indicating best transfer to unseen real TSPLIB problems. Random and failure replay conditions follow (~0.068-0.077).

- There is overall a consistent improvement from no replay to various replay-based conditions on generalization performance (lower gaps), with **phase6_diversity_failure_replay_compression** dominating.

---

## Replay Archive Diversity, Hardness, Size Bias, and Failure Concentration

- **Archive Descriptor Diversity**:  
  Highest diversity (~0.24) occurs in conditions using experience archives with broad coverage (no replay, random replay, stratified random, diversity weighted).  
  Replay focused on worst archive (failure, diversity_failure, residual_failure) has lower descriptor diversity (~0.0 to 0.17).

- **Archive Hardness**:  
  Tends to be higher (~0.25-0.34) in failure replay conditions focusing on worst archive, indicating replayed cases are harder than the broad experience archives (~0.15-0.2).

- **Archive Size Bias**:  
  Size bias is near zero for experience archive conditions, but noticeable (around 0.12) for worst archive-focused replay modes, indicating biased replay towards larger or harder instances.

- **Failure Concentration**:  
  Mean replay failure concentration is 0 for no replay (expected), around 0.1-0.2 in random and diversity weighted replay, and elevated (up to 1.0) in residual failure replay. High failure concentration aligns with failure replay modes but can negatively affect diversity.

---

## Failure Concentration and Failure Replay Types

- **Broad-Coverage Replay (random, stratified_random, diversity_weighted)**:  
  Archive diversity is high, failure concentration moderate (~0.13-0.22).  

- **Raw-Failure Replay (failure mode)**:  
  Higher hardness and size bias, and failure concentration (~0.22).  

- **Residual-Failure Replay (residual_failure)**:  
  Very high failure concentration (~0.125 mean, 0.17 final), zero diversity in archive descriptors (archive_0 diversity), moderate hardness.  

- **Diversity-Weighted Replay**:  
  Balances diversity and hardness, moderate failure concentration (~0.13).  

- **Compression-Aware Replay (compression == true)**:  
  Seen in random_replay_compression and diversity_failure_replay_compression conditions. Corresponds to stable or improved transfer (tested below).

---

## Effect of Compression-Aware Replay

- Compression-aware replay improves transfer gap for diversity_failure (from 0.0959 to 0.0426) and reduces heldout TSPLIB mean gap notably (from ~0.145 to 0.067).  
- However, code novelty mean drops (from ~0.82 to 0.60) and last code novelty drops significantly (0.75 to 0.47), indicating less lexical novelty in code generation despite better transfer.  
- Compression reduces archive size bias slightly and maintains failure concentration similar to diversity_failure replay without compression.

---

## Code Novelty vs Transfer

- **No Replay** condition achieves high code novelty but poorer transfer (TSPLIB gap ~0.21, transfer gap 0.16).  
- Replay conditions generally have lower code novelty but better transfer gaps.  
- Notably, random_replay_compression has 0 code novelty mean and last code novelty but still good synthetic holdout gap (0) and decent transfer gap (~0.08).  
- This divergence suggests that lexical novelty does not equate to better transfer or algorithmic invention without corresponding gains in transfer gap.

---

## Concentration of Failures and Replay Selection Diversity

- Failure replay modes (failure, residual_failure) have higher failure concentration (~0.22-1.0), indicating replay focuses on a small set of hard instances/failures.  
- Residual_failure replay shows archive descriptor diversity = 0 but still reasonable hardness. This may suggest concentrated replay on very similar residual failures.  
- Diversity-weighted replays balance replay selection diversity (~0.26) and reduce failure concentration (~0.13), promoting more varied replay and potentially better generalization.

---

# Summary Conclusions

- **Best transfer performance** (lowest heldout TSPLIB gaps and transfer gaps) is achieved by **phase6_diversity_failure_replay_compression**, followed by failure and random replay variants.  
- Compression-aware replay reduces code novelty but improves transfer, indicating lexical novelty is not required for improved transfer here.  
- Replay focused on failures alone (failure and residual_failure) yields harder and somewhat smaller archives with concentrated replay failure cases; this can reduce diversity and increase size bias.  
- Broad-coverage replay modes retain higher archive diversity and lower failure concentration but generally have slightly worse transfer gaps than best failure-driven replay with compression.  
- Code novelty is not predictive of transfer improvements; several conditions with reduced or zero code novelty outperform high novelty baselines.  
- Therefore, transfer metrics (held-out TSPLIB and synthetic gaps) and replay archive characteristics (diversity, hardness, failure concentration) provide more reliable evidence of replay benefit than code novelty or lexical speculation.

---

# Recommended Priorities for Future Mechanism Studies

1. Investigate failure concentration effects on replay effectiveness and whether moderate failure concentration with diversity weighting is optimal.  
2. Examine the impact of compression-aware replay on balancing effective replay archive size and transfer gain despite reduced novelty.  
3. Explore the role of archive size bias in failure replay and its interaction with instance difficulty and solver adaptation.  
4. Avoid equating code novelty with algorithmic invention unless transfer and success metrics also support.  
5. Prioritize heldout TSPLIB and synthetic holdout gaps as primary evidence for transfer success across replay conditions.

---

# Overall:  
Phase6_diversity_failure_replay_compression condition is the strongest performer in transfer metrics despite lowered lexical novelty, highlighting the superiority of focused, compressed, diversity-aware failure replay over other replay modes for generalizable TSP performance improvement.
