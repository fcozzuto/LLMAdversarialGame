# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_failure_replay`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260519_003151_g
- started_at_local: 2026-05-19 00:31:51
- finished_at_local: 2026-05-19 00:50:30
- duration_hhmm: 00:19
- duration_seconds: 1119.379
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.866887 | 0.56 | -0.028729 |
| phase6_random_replay | random | score_only | False | 0.103557 | 0.0 | 0.0659 | 0.236772 | 0.158178 | 0.19457 | 0.86061 | 0.76 | 0.037658 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.800308 | 0.56 | -0.031119 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.16387 | 0.0 | 0.104281 | 0.236772 | 0.171161 | 0.19457 | 0.894085 | 0.76 | 0.011623 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.076723 | 0.0 | 0.048824 | 0.236772 | 0.160327 | 0.221162 | 0.836401 | 0.76 | 0.02066 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.130039 | 0.872351 | 0.56 | -0.028549 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.291666 | 0.910568 | 0.56 | -0.027351 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.068884 | 0.0 | 0.043835 | 0.171206 | 0.303473 | 0.17767 | 0.792391 | 0.76 | 0.034862 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.866887`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.028729` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.401318, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.0}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.004952}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.103557`, synthetic `0.0`, combined `0.0659`.
- Accepted-epoch count `3`, mean accepted code novelty `0.86061`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.158178`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133693`, mean selected residual gap `-0.016452`.
- Adaptation efficiency `0.037658` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.103557` across 7 instances; family means: ch=0.098996, kroD=0.111017, pcb=0.228111, pr=0.036252, rd=0.096713, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3517, "expected_gap": 0.402559, "family": "a", "name": "a280", "optimality_gap": 0.363707, "residual_gap": -0.038852}, {"best_known_cost": 7542, "cost": 10190, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.351101, "residual_gap": 0.105994}, {"best_known_cost": 629, "cost": 774, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.230525, "residual_gap": -0.025755}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.800308`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.308405`, mean selected residual gap `0.067352`.
- Adaptation efficiency `-0.031119` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402249, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.000931}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.001975}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.16387`, synthetic `0.0`, combined `0.104281`.
- Accepted-epoch count `2`, mean accepted code novelty `0.894085`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.171161`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132668`, mean selected residual gap `0.000355`.
- Adaptation efficiency `0.011623` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.16387` across 7 instances; family means: ch=0.171058, kroD=0.048605, pcb=0.207393, pr=0.292468, rd=0.172061, st=0.084444.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3241, "expected_gap": 0.402327, "family": "a", "name": "a280", "optimality_gap": 0.256689, "residual_gap": -0.145638}, {"best_known_cost": 14379, "cost": 15722, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.0934, "residual_gap": -0.233577}, {"best_known_cost": 7542, "cost": 8197, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.086847, "residual_gap": -0.158181}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.076723`, synthetic `0.0`, combined `0.048824`.
- Accepted-epoch count `2`, mean accepted code novelty `0.836401`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.160327`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237004`, mean selected residual gap `-0.034308`.
- Adaptation efficiency `0.02066` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.076723` across 7 instances; family means: ch=0.089891, kroD=0.045741, pcb=0.193155, pr=0.036113, rd=0.023009, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3058, "expected_gap": 0.398294, "family": "a", "name": "a280", "optimality_gap": 0.185731, "residual_gap": -0.212563}, {"best_known_cost": 14379, "cost": 16009, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.11336, "residual_gap": -0.2116}, {"best_known_cost": 629, "cost": 683, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.085851, "residual_gap": -0.170429}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.872351`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.266358`, mean selected expected gap `0.166982`, mean selected residual gap `0.026708`.
- Adaptation efficiency `-0.028549` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.400465, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.000853}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137043}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007052}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.910568`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.263443`, mean selected residual gap `0.088949`.
- Adaptation efficiency `-0.027351` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.399612, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.001706}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007539}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.068884`, synthetic `0.0`, combined `0.043835`.
- Accepted-epoch count `4`, mean accepted code novelty `0.792391`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.303473`, size bias `0.120322`, and failure concentration `0.17767`.
- Replay selection diversity `0.202085`, mean selected expected gap `0.314544`, mean selected residual gap `-0.003032`.
- Adaptation efficiency `0.034862` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.068884` across 7 instances; family means: ch=0.063105, kroD=0.041514, pcb=0.166864, pr=0.056121, rd=0.036662, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3302, "expected_gap": 0.398139, "family": "a", "name": "a280", "optimality_gap": 0.280341, "residual_gap": -0.117798}, {"best_known_cost": 7542, "cost": 9644, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706, "residual_gap": 0.041342}, {"best_known_cost": 14379, "cost": 17216, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.197302, "residual_gap": -0.125892}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.299346`, mean selected residual gap `0.050643`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.000542}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00644}]

## Judge Appendix
# Replay-Aware TSP Benchmark Suite Evaluation

## Summary of Main Transfer Metrics (Held-out TSPLIB & Synthetic Holdout Gaps)

| Condition Name                   | Replay Mode            | Final Synthetic Gap | Final Transfer Gap | Final TSPLIB Gap | Adaptation Efficiency | Archive Size | Archive Diversity | Archive Hardness | Failure Concentration |
|--------------------------------|-----------------------|---------------------|--------------------|------------------|-----------------------|--------------|-------------------|------------------|-----------------------|
| phase6_no_replay               | none                  | 0.0649              | 0.1594             | 0.2134           | -0.0287               | 31           | 0.240             | 0.212            | 0.0                   |
| phase6_random_replay           | random                | 0.0                 | 0.0659             | 0.1036           | 0.0377                | 28           | 0.240             | 0.159            | 0.16                  |
| phase6_failure_replay          | failure               | 0.0649              | 0.1594             | 0.2134           | -0.0311               | 31           | 0.175             | 0.349            | 0.31                  |
| phase6_random_replay_compression | random + compression | 0.0                 | 0.1043             | 0.1639           | 0.0116                | 30           | 0.240             | 0.184            | 0.16                  |
| phase6_stratified_random_replay | stratified_random    | 0.0                 | 0.0488             | 0.0767           | 0.0207                | 29           | 0.240             | 0.182            | 0.25                  |
| phase6_diversity_weighted_replay | diversity_weighted  | 0.0649              | 0.1594             | 0.2134           | -0.0285               | 32           | 0.240             | 0.212            | 0.33                  |
| phase6_residual_failure_replay | residual_failure      | 0.0649              | 0.1594             | 0.2134           | -0.0274               | 32           | 0.175             | 0.349            | 0.29                  |
| phase6_diversity_failure_replay | diversity_failure    | 0.0                 | 0.0438             | 0.0689           | 0.0349                | 30           | 0.175             | 0.320            | 0.17                  |
| phase6_diversity_failure_replay_compression | diversity_failure + compression | 0.0649 | 0.1594         | 0.2134           | 0.0                   | 32           | 0.175             | 0.349            | 0.17                  |

**Notes:**

- **Best Holdout & Transfer:** `phase6_diversity_failure_replay` shows the best held-out TSPLIB gap (6.89%) and best transfer gap (4.38%).
- **Best Synthetic Holdout:** `phase6_random_replay` achieves zero synthetic holdout gap.
- Conditions with "diversity_failure" replay modes (with or without compression) and "random" replay generally perform better on held-out and synthetic instances.
- Non-replay (`phase6_no_replay`) and "failure_replay" variants show higher final TSPLIB gaps (~21%) and transfer gaps (~16%), indicating lower generalization.

---

## Analysis of Replay Archive Characteristics

| Condition Name                    | Replay Mode           | Archive Size | Descriptor Diversity | Archive Hardness | Size Bias | Failure Concentration |
|---------------------------------|----------------------|--------------|----------------------|------------------|-----------|-----------------------|
| phase6_no_replay                | none                 | 31           | 0.240                | 0.212            | 0.0       | 0.0                   |
| phase6_random_replay            | random               | 28           | 0.240                | 0.159            | 0.0       | 0.16                  |
| phase6_failure_replay           | failure              | 31           | 0.175                | 0.349            | 0.125     | 0.31                  |
| phase6_random_replay_compression| random + compression  | 30           | 0.240                | 0.184            | 0.0       | 0.16                  |
| phase6_stratified_random_replay | stratified_random    | 29           | 0.240                | 0.182            | 0.0       | 0.25                  |
| phase6_diversity_weighted_replay| diversity_weighted  | 32           | 0.240                | 0.212            | 0.0       | 0.33                  |
| phase6_residual_failure_replay  | residual_failure      | 32           | 0.175                | 0.349            | 0.125     | 0.29                  |
| phase6_diversity_failure_replay | diversity_failure    | 30           | 0.175                | 0.320            | 0.125     | 0.17                  |
| phase6_diversity_failure_replay_compression | diversity_failure + compression | 32 | 0.175           | 0.349            | 0.125     | 0.17                  |

**Insights:**

- Failure-oriented replay modes ("failure", "residual_failure", "diversity_failure") exhibit **higher archive hardness** (~0.32-0.35) and **higher failure concentration** (up to 0.33).
- Diversity or random replay maintains **higher archive descriptor diversity** (0.24) and **lower failure concentration** (0.16-0.25).
- Compression pressure does not drastically change these metrics but slightly reduces adaptation efficiency in some cases.
- Size bias is notable (~0.12) only in failure replay modes, indicating replay favoring larger or more complex cases.

---

## Performance vs. Replay Strategy

- **Diversity Failure Replay (`phase6_diversity_failure_replay`)** achieves the best trade-off:
  - Lowest transfer gap on held-out TSPLIB (6.9%) and synthetic holdout (0%).
  - Moderate replay failure concentration (~0.17).
  - Higher elite archive size (4), indicating substantial elite diversity.
  - Moderate archive hardness and diversity balance.
  - Adaptation efficiency positive (0.0349), unlike failure replays which are negative.
- **Random Replay (`phase6_random_replay`)** shows:
  - Best synthetic holdout gap (0%).
  - Good TSPLIB and transfer gaps (~10.4% and ~6.6%).
  - Higher replay failure concentration (0.16) than no replay (0).
  - Good archive diversity (0.24), lower archive hardness.
  - Positive adaptation efficiency (0.0377).
- **Failure Replay (`phase6_failure_replay` and `phase6_residual_failure_replay`)**:
  - Worse transfer and TSPLIB gaps (~16%+).
  - Highest replay failure concentration (0.29-0.33).
  - Large size bias (0.12).
  - Negative adaptation efficiency (~-0.03).
  - Lower archive descriptor diversity (~0.17).
- **Compression-aware variants** do not improve transfer gaps relative to their base counterparts, indicating compression reduces code novelty without proportional transfer improvement.
- **Stratified Random Replay** improves held-out gaps moderately but with no synthetic advantage, indicating selective sampling helps slightly.

---

## Code Novelty vs. Transfer

- The condition `phase6_diversity_failure_replay_compression` shows **zero** last and mean code novelty but does **not** improve transfer beyond failure replay baselines.
- Other conditions with high mean code novelty (~0.8-0.9) do not necessarily translate to better transfer (e.g., failure replay with high novelty but worse transfer).
- Hence, **code novelty falls when transfer improves is not observed in this dataset**. Instead, high novelty alone does not guarantee better transfer.
- No clear lexical novelty to algorithmic invention mapping; improvement linked more to replay strategy and archive properties.

---

## Detailed Replay Modes

- **Broad-Coverage Replay**: Not explicitly named, possibly akin to random replay; supported by higher archive diversity and lower failure concentration.
- **Raw-Failure Replay**: `phase6_failure_replay` and `phase6_residual_failure_replay` replicate failure cases, leading to high failure concentration, larger archive size bias, and poorer transfer.
- **Residual-Failure Replay**: Focus on remaining failure cases after prior handling; shows no transfer improvement over raw failure replay.
- **Diversity-Weighted Replay**: Emphasizes diverse failure cases with weights; yields strong archive diversity preserved but shows poor transfer similar to failure replays, possibly due to size bias.
- **Compression-Aware Replay**: Incorporates compression pressure; reduces code novelty significantly without transfer gains.

---

## Failure Concentration and Transfer

- Conditions with **lower failure concentration** (random, diversity_failure) have superior transfer metrics.
- High failure concentration correlates with worse transfer and TSPLIB gaps.
- Selection diversity is higher in random replay (~0.26) and diversity_failure (~0.20), lower in failure replay (~0.17).
- Residual and failure replays show failure concentration ~0.3 with negative adaptation efficiency.

---

## Training Gap and Worst Instances

- Training gaps mostly higher (~25-36%), no condition drastically reduces training gap to match synthetic holdout.
- Worst training instances remain consistent in difficulty across conditions.
- This supports that replay conditions improve generalization on held-out but not fully on training hard cases.

---

# Conclusion

- **Phase6 diversity_failure_replay** is the best overall condition in terms of **transfer to TSPLIB and synthetic holdout sets**, with lowest optimality gaps in transfer metrics.
- **Random replay** yields best synthetic holdout zero gaps and solid transfer results.
- **Failure-based replay strategies**, including residual failure and diversity weighted replays with failure concentration and size bias, show **worse transfer and adaptation efficiency**.
- **Compression-aware replay reduces code novelty without transfer improvement**, suggesting compression should be used cautiously.
- Code novelty does not strongly correlate with transfer improvements; algorithmic gains are better identified by replay strategy effectiveness rather than lexical novelty alone.
- Replay archive properties (diversity, hardness, failure concentration, size bias) strongly influence transfer outcomes; low failure concentration and balanced archive hardness/diversity are favorable.
- Prioritize replay modes emphasizing diversity with failure cases but controlling failure concentration for improved TSP performance generalization.

---

*Interpretation is restricted to objective metrics; no narrative speculation provided.*
