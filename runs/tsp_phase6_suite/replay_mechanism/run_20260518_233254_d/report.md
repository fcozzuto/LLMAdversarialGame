# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_random_replay`.
- Best TSPLIB holdout gap: `phase6_random_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260518_233254_d
- started_at_local: 2026-05-18 23:32:54
- finished_at_local: 2026-05-18 23:52:17
- duration_hhmm: 00:19
- duration_seconds: 1163.002
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.09339 | 0.0 | 0.05943 | 0.236772 | 0.115659 | 0.0 | 0.721692 | 0.76 | 0.029334 |
| phase6_random_replay | random | score_only | False | 0.083754 | 0.001628 | 0.05389 | 0.236772 | 0.135548 | 0.19457 | 0.749694 | 0.76 | 0.047462 |
| phase6_failure_replay | failure | score_only | False | 0.128074 | 0.0 | 0.081502 | 0.171206 | 0.288318 | 0.228311 | 0.704278 | 0.76 | 0.063433 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.108492 | 0.0 | 0.06904 | 0.236772 | 0.155909 | 0.19457 | 0.824501 | 0.76 | 0.035763 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.221162 | 0.803495 | 0.56 | -0.030996 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.130039 | 0.854129 | 0.56 | -0.029158 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.194753 | 0.0 | 0.123934 | 0.118662 | 0.278293 | 0.323448 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.08809 | 0.0 | 0.056057 | 0.171206 | 0.303258 | 0.172748 | 0.716584 | 0.76 | 0.049298 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.09339`, synthetic `0.0`, combined `0.05943`.
- Accepted-epoch count `2`, mean accepted code novelty `0.721692`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.115659`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.029334` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.09339` across 7 instances; family means: ch=0.063484, kroD=0.077158, pcb=0.322502, pr=0.036113, rd=0.031732, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 947, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.505564, "residual_gap": 0.248012}, {"best_known_cost": 2579, "cost": 3778, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.464909, "residual_gap": 0.064133}, {"best_known_cost": 7542, "cost": 8832, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.171042, "residual_gap": -0.073986}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.083754`, synthetic `0.001628`, combined `0.05389`.
- Accepted-epoch count `3`, mean accepted code novelty `0.749694`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.135548`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133496`, mean selected residual gap `-0.033587`.
- Adaptation efficiency `0.047462` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.083754` across 7 instances; family means: ch=0.071883, kroD=0.030149, pcb=0.180137, pr=0.036113, rd=0.102781, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10037, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.330814, "residual_gap": 0.089896}, {"best_known_cost": 2579, "cost": 3416, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.324544, "residual_gap": -0.076232}, {"best_known_cost": 629, "cost": 774, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.230525, "residual_gap": -0.025755}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.128074`, synthetic `0.0`, combined `0.081502`.
- Accepted-epoch count `3`, mean accepted code novelty `0.704278`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.288318`, size bias `0.120322`, and failure concentration `0.228311`.
- Replay selection diversity `0.169313`, mean selected expected gap `0.318675`, mean selected residual gap `-0.010989`.
- Adaptation efficiency `0.063433` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.128074` across 7 instances; family means: ch=0.088632, kroD=0.084907, pcb=0.272579, pr=0.304949, rd=0.043489, st=0.013333.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10015, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.327897, "residual_gap": 0.091275}, {"best_known_cost": 2579, "cost": 3388, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.313687, "residual_gap": -0.088252}, {"best_known_cost": 14379, "cost": 18452, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.28326, "residual_gap": -0.038904}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.108492`, synthetic `0.0`, combined `0.06904`.
- Accepted-epoch count `3`, mean accepted code novelty `0.824501`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.155909`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132323`, mean selected residual gap `-0.014481`.
- Adaptation efficiency `0.035763` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.108492` across 7 instances; family means: ch=0.100579, kroD=0.071898, pcb=0.26734, pr=0.103255, rd=0.041719, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3468, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.344707, "residual_gap": -0.058938}, {"best_known_cost": 7542, "cost": 7990, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.059401, "residual_gap": -0.173747}, {"best_known_cost": 629, "cost": 663, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.054054, "residual_gap": -0.199364}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.803495`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237974`, mean selected residual gap `0.052751`.
- Adaptation efficiency `-0.030996` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.005196}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": -2.8e-05}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.854129`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.266358`, mean selected expected gap `0.168262`, mean selected residual gap `0.025427`.
- Adaptation efficiency `-0.029158` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.406049, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.004731}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137043}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.000807}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.194753`, synthetic `0.0`, combined `0.123934`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.118662`, mean hardness `0.278293`, size bias `0.08672`, and failure concentration `0.323448`.
- Replay selection diversity `0.149216`, mean selected expected gap `0.273635`, mean selected residual gap `0.04886`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.194753` across 7 instances; family means: ch=0.103708, kroD=0.360618, pcb=0.22362, pr=0.340869, rd=0.205563, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19964, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.388414, "residual_gap": 0.061757}, {"best_known_cost": 629, "cost": 815, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.295707, "residual_gap": 0.033704}, {"best_known_cost": 7542, "cost": 9666, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.281623, "residual_gap": 0.048555}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.08809`, synthetic `0.0`, combined `0.056057`.
- Accepted-epoch count `3`, mean accepted code novelty `0.716584`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.303258`, size bias `0.120322`, and failure concentration `0.172748`.
- Replay selection diversity `0.194842`, mean selected expected gap `0.300271`, mean selected residual gap `0.006324`.
- Adaptation efficiency `0.049298` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.08809` across 7 instances; family means: ch=0.055342, kroD=0.080915, pcb=0.180866, pr=0.088028, rd=0.135398, st=0.020741.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3466, "expected_gap": 0.402482, "family": "a", "name": "a280", "optimality_gap": 0.343932, "residual_gap": -0.05855}, {"best_known_cost": 14379, "cost": 17624, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.225676, "residual_gap": -0.100981}, {"best_known_cost": 7542, "cost": 9128, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.210289, "residual_gap": -0.025537}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301021`, mean selected residual gap `0.048968`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.401086, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.000232}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.003825}]

## Judge Appendix
# TSP Benchmark Suite Evaluation Summary

## Overview
- **Best Conditions:**
  - Held-out TSPLIB gap: `phase6_random_replay` (0.08375)
  - Synthetic holdout gap: `phase6_no_replay` (0.0)
  - Best transfer (combined evidence from TSPLIB and synthetic): `phase6_random_replay` (TSPLIB gap 0.08375, Transfer gap 0.05389)

- Total conditions: 9  
- Replay Modes: none, random, failure, stratified_random, diversity_weighted, residual_failure, diversity_failure  
- Selection Modes: score_only, novelty_gate

---

## Transfer Performance (Held-out TSPLIB and Synthetic Holdouts)

| Condition                          | TSPLIB Gap | Synthetic Gap | Transfer Gap | Replay Mode            | Selection Mode | Code Novelty (mean) | Archive Diversity | Archive Hardness | Replay Failure Concentration |
|----------------------------------|------------|--------------|--------------|------------------------|----------------|---------------------|-------------------|------------------|------------------------------|
| phase6_random_replay             | 0.08375    | 0.001628     | 0.05389      | random                 | score_only     | 0.7497              | 0.2368            | 0.1355           | 0.195                        |
| phase6_no_replay                 | 0.09339    | 0.0          | 0.05943      | none                   | score_only     | 0.7217              | 0.2368            | 0.1157           | 0.0                          |
| phase6_failure_replay            | 0.12807    | 0.0          | 0.08150      | failure                | score_only     | 0.7043              | 0.1712            | 0.2883           | 0.228                        |
| phase6_random_replay_compression | 0.10849    | 0.0          | 0.06904      | random                 | novelty_gate   | 0.8245              | 0.2368            | 0.1559           | 0.195                        |
| phase6_stratified_random_replay | 0.21339    | 0.06492      | 0.15940      | stratified_random      | score_only     | 0.8035              | 0.2368            | 0.2148           | 0.221                        |
| phase6_diversity_weighted_replay | 0.21339    | 0.06492      | 0.15940      | diversity_weighted     | score_only     | 0.8541              | 0.2368            | 0.2148           | 0.130                        |
| phase6_residual_failure_replay  | 0.19475    | 0.0          | 0.12393      | residual_failure       | score_only     | 0.0                 | 0.1187            | 0.2783           | 0.323                        |
| phase6_diversity_failure_replay | 0.08809    | 0.0          | 0.05606      | diversity_failure      | score_only     | 0.7166              | 0.1712            | 0.3033           | 0.173                        |
| phase6_diversity_failure_replay_compression | 0.21339 | 0.06492     | 0.15940      | diversity_failure      | novelty_gate   | 0.0                 | 0.1712            | 0.3480           | 0.170                        |

---

## Interpretation

### Transfer Metrics:
- The `phase6_random_replay` condition achieves the lowest (best) TSPLIB held-out gap (0.08375) and the best overall transfer gap (0.05389), making it the best performer for generalization to real-world instances.
- `phase6_no_replay` has perfect synthetic holdout performance but slightly worse TSPLIB gap; it is the best on synthetic probed instances but lacks replay.
- Conditions using failure-based or diversity-aware replay generally show higher TSPLIB gaps, indicating reduced transfer compared to random replay.
- Stratified random and diversity-weighted replay show poor transfer performance (TSPLIB gaps over 0.21 and transfer gaps ~0.16), indicating limited benefit to transfer.
- Residual failure replay conditions have moderate to poor transfer performance with failure concentration and archive hardness relatively high, but associated gaps are higher than the best random replay condition.

### Replay Archive and Mechanism Metrics:
- **Archive Diversity:**  
  Highest diversity (~0.24) is with random and no-replay conditions; diversity failure and failure replay conditions show lower archive diversity (~0.17 or less), indicating less diverse failure cases are replayed.
  
- **Archive Hardness:**  
  Failure-based replay conditions (failure, residual failure, diversity failure) tend to have higher hardness (>0.28), suggesting that these archives contain harder failure cases.
  
- **Replay Failure Concentration:**  
  - Failure replay conditions exhibit moderate failure concentration (0.17 - 0.32), indicating replay focused on concentrated difficult cases.  
  - Random replay has lower concentration (~0.19 - 0.20).  
  - No replay condition naturally shows 0 failure concentration (0.0).
  
- **Selection Diversity:**  
  Random and diversity-weighted replay conditions have non-zero replay selection diversity (~0.19 - 0.26), while residual failure has lower diversity (~0.15).

### Adaptation Efficiency:
- Highest positive adaptation efficiency is observed with `phase6_failure_replay` (0.0634) and `phase6_diversity_failure_replay` (0.0493), indicating better training adaptation.
- Random replay with score-only selection also adapts reasonably well (0.0475).
- Negative or zero adaptation efficiency observed in certain diversity-based replay modes with mixed transfer performance.

### Code Novelty vs Transfer:
- Code novelty is generally high (0.7 - 0.85) across conditions using replay with random or diversity-based modes.
- Notably, `phase6_residual_failure_replay` and compression replay variations have zero mean code novelty.
- However, transfer performance does not always correlate positively with code novelty:
  - E.g., `phase6_residual_failure_replay` has zero novelty but high transfer gap (~0.12 to 0.16).
  - `phase6_diversity_failure_replay_compression` has zero novelty but high transfer gap (~0.16).
- This confirms that code novelty (lexical diversity) alone does not imply algorithmic improvement unless transfer metrics improve accordingly.

---

## Detailed Notes on Key Conditions

### phase6_random_replay
- Among the best in transfer metrics (lowest TSPLIB gap 0.08375; transfer gap 0.05389).
- Replay focused on random failure sampling, moderate failure concentration (0.19), good selection diversity (0.26), moderate archive hardness (0.1355).
- High code novelty (~0.75) but adaptation efficiency moderate (0.0475).
- Indicates replay diversity balanced with transfer generalization.

### phase6_no_replay
- No replay; achieves best synthetic holdout gap (0.0).
- Slightly worse TSPLIB heldout gap (0.09339) vs random replay.
- Zero replay failure concentration and no replay selection diversity.
- Code novelty ~0.72, similar to random replay.
- Suggests that replay is not strictly required for synthetic holdout optimality, but random replay aids cross-domain transfer.

### phase6_failure_replay
- Best adaptation efficiency (0.0634) but poorer transfer performance (TSPLIB gap ~0.128; transfer gap 0.0815).
- High archive hardness (0.29) and failure concentration (0.23).
- Replay focused on failure cases leads to more concentrated replay but generalizes less well.
- Code novelty lower (~0.70), with size bias in archive.

### phase6_stratified_random_replay & diversity_weighted_replay
- High TSPLIB gaps (0.21+) and transfer gaps (~0.16), poor transfer.
- Replay failure concentration moderate (0.13-0.22).
- High archive descriptor diversity (~0.24) but lower adaptation efficiency (negative or near zero).
- Code novelty high (0.80+).
- Suggests complexity or selection mode may negatively impact transfer despite high novelty.

### phase6_residual_failure_replay
- Zero code novelty, highest replay failure concentration (~0.32).
- Worse TSPLIB gap (0.19), moderate transfer gap (0.12).
- High archive hardness (~0.32) and size bias.
- Replay focuses on residual failures, highly concentrated but with limited adaptation and transfer.

### phase6_diversity_failure_replay
- Moderate TSPLIB gap (0.08809) and transfer gap (0.056), among better transfer results.
- Good adaptation efficiency (0.0493), high archive hardness (0.31), moderate failure concentration (0.17-0.19).
- Code novelty moderate (0.72).
- Replay balances failure diversity and archive hardness better than failure replay alone.

### phase6_diversity_failure_replay_compression
- Zero code novelty, high archive hardness (0.35), and failure concentration (~0.17).
- Poor transfer gaps (TSPLIB gap 0.21, transfer gap 0.16).
- Compression pressure reduces code novelty but transfer does not improve.

---

## Failures and Size Bias

- Failure replay modes show increased archive size bias (>0.1) with more failures and residual failures.
- Random replay modes have negligible size bias (~0).
- Failure concentration is lowest with no replay (0.0), moderate in random replay (~0.19), and highest in residual failure replay (~0.32).
- Diversity-weighted replay shows moderate failure concentration and high complexity.

---

## Summary

- **Best transfer performance is achieved by random replay (`phase6_random_replay`), combining a relatively low TSPLIB optimality gap (8.3%) and transfer gap (5.4%).**  
- **No replay matches synthetic holdout but slightly underperforms random replay on TSPLIB transfer, indicating replay aids generalization beyond synthetic settings.**  
- **Failure-based replay modes deliver higher adaptation efficiency but worse transfer and greater failure concentration, indicating overfitting to replayed failure cases may limit generalization.**  
- **Archival diversity and size bias analyses show failure replay concentrates more on hard/difficult cases at the cost of replay diversity; random replay preserves a more diverse archive.**  
- **Code novelty is high in random and diversity-based replay except in compression and residual failure modes where novelty drops to zero; however, increased code novelty does not always correspond to better transfer.**  
- **Selection mode ('score_only' vs 'novelty_gate') impacts adaptation and code novelty but improvements in code novelty do not uniformly correspond to better transfer metrics.**

---

# Recommendations

- Prioritize **phase6_random_replay** for transfer-based tasks where held-out TSPLIB optimality gap and transfer gap are critical.  
- Employ replay strategies preserving **archive diversity** and avoiding excessive failure concentration **to favor generalization**.  
- Avoid over-concentration on failure cases alone (residual_failure or failure replay) that hurt transfer despite good adaptation and high hardness.  
- Code novelty metrics should be interpreted cautiously; algorithmic improvement must be backed by reduced optimality and transfer gaps, not lexical novelty alone.  
- Compression strategies reduce code novelty but do not improve transfer; use with caution.  

---

This conservative interpretation bases conclusions primarily on transfer (held-out TSPLIB and synthetic), with explicit attention to replay archive diversity, hardness, size bias, and failure concentration.
