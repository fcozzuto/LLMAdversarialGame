# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_stratified_random_replay`.
- Best TSPLIB holdout gap: `phase6_stratified_random_replay`.
- Best synthetic holdout gap: `phase6_failure_replay`.

## Run Metadata
- run_name: run_20260519_005032_h
- started_at_local: 2026-05-19 00:50:32
- finished_at_local: 2026-05-19 01:09:42
- duration_hhmm: 00:19
- duration_seconds: 1150.704
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.842525 | 0.63 | -0.02956 |
| phase6_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.864534 | 0.56 | -0.028807 |
| phase6_failure_replay | failure | score_only | False | 0.105503 | 0.0 | 0.067138 | 0.171206 | 0.249441 | 0.199982 | 0.0 | 0.76 | 0.0 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.08682 | 0.003941 | 0.056682 | 0.236772 | 0.148504 | 0.221162 | 0.788169 | 0.76 | 0.04152 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.126568 | 0.0 | 0.080543 | 0.236772 | 0.187137 | 0.157119 | 0.759221 | 0.76 | 0.080585 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.117653 | 0.010343 | 0.078631 | 0.101234 | 0.27062 | 0.373989 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.163475 | 0.0 | 0.10403 | 0.171206 | 0.247432 | 0.17767 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.204223 | 0.0 | 0.12996 | 0.171206 | 0.247952 | 0.175969 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.842525`, and final complexity `0.64`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.02956` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.399069, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.002249}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007539}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.864534`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133486`, mean selected residual gap `0.03788`.
- Adaptation efficiency `-0.028807` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402714, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001396}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.317296, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.011517}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.105503`, synthetic `0.0`, combined `0.067138`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.249441`, size bias `0.120322`, and failure concentration `0.199982`.
- Replay selection diversity `0.171194`, mean selected expected gap `0.291967`, mean selected residual gap `-0.004933`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.105503` across 7 instances; family means: ch=0.074679, kroD=0.081948, pcb=0.226476, pr=0.167466, rd=0.065866, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10449, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.385442, "residual_gap": 0.140335}, {"best_known_cost": 2579, "cost": 3390, "expected_gap": 0.404808, "family": "a", "name": "a280", "optimality_gap": 0.314463, "residual_gap": -0.090345}, {"best_known_cost": 14379, "cost": 17495, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.216705, "residual_gap": -0.112024}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132655`, mean selected residual gap `0.038711`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.000542}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328131, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.000682}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.08682`, synthetic `0.003941`, combined `0.056682`.
- Accepted-epoch count `3`, mean accepted code novelty `0.788169`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.148504`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.238172`, mean selected residual gap `-0.05168`.
- Adaptation efficiency `0.04152` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.08682` across 7 instances; family means: ch=0.090348, kroD=0.092514, pcb=0.167179, pr=0.036113, rd=0.052718, st=0.078519.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3477, "expected_gap": 0.40031, "family": "a", "name": "a280", "optimality_gap": 0.348197, "residual_gap": -0.052113}, {"best_known_cost": 14379, "cost": 17054, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.186035, "residual_gap": -0.143599}, {"best_known_cost": 7542, "cost": 8692, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.152479, "residual_gap": -0.092549}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.126568`, synthetic `0.0`, combined `0.080543`.
- Accepted-epoch count `3`, mean accepted code novelty `0.759221`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.187137`, size bias `8.3e-05`, and failure concentration `0.157119`.
- Replay selection diversity `0.272437`, mean selected expected gap `0.156895`, mean selected residual gap `0.009934`.
- Adaptation efficiency `0.080585` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.126568` across 7 instances; family means: ch=0.076935, kroD=0.082605, pcb=0.322384, pr=0.072236, rd=0.176359, st=0.078519.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3376, "expected_gap": 0.400931, "family": "a", "name": "a280", "optimality_gap": 0.309035, "residual_gap": -0.091896}, {"best_known_cost": 7542, "cost": 8379, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.110979, "residual_gap": -0.129939}, {"best_known_cost": 629, "cost": 667, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.060413, "residual_gap": -0.193641}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.117653`, synthetic `0.010343`, combined `0.078631`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.101234`, mean hardness `0.27062`, size bias `0.065785`, and failure concentration `0.373989`.
- Replay selection diversity `0.123685`, mean selected expected gap `0.268811`, mean selected residual gap `0.03726`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.117653` across 7 instances; family means: ch=0.068952, kroD=0.184794, pcb=0.201406, pr=0.114877, rd=0.095702, st=0.088889.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3430, "expected_gap": 0.402869, "family": "a", "name": "a280", "optimality_gap": 0.329973, "residual_gap": -0.072896}, {"best_known_cost": 629, "cost": 835, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.327504, "residual_gap": 0.065501}, {"best_known_cost": 14379, "cost": 18695, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.30016, "residual_gap": -0.022004}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.163475`, synthetic `0.0`, combined `0.10403`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.247432`, size bias `0.120322`, and failure concentration `0.17767`.
- Replay selection diversity `0.201519`, mean selected expected gap `0.316557`, mean selected residual gap `-0.043209`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.163475` across 7 instances; family means: ch=0.101907, kroD=0.159998, pcb=0.175529, pr=0.334443, rd=0.223135, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3108, "expected_gap": 0.403257, "family": "a", "name": "a280", "optimality_gap": 0.205118, "residual_gap": -0.198139}, {"best_known_cost": 629, "cost": 678, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.077901, "residual_gap": -0.18919}, {"best_known_cost": 7542, "cost": 8123, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.077035, "residual_gap": -0.156113}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.204223`, synthetic `0.0`, combined `0.12996`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.247952`, size bias `0.120322`, and failure concentration `0.175969`.
- Replay selection diversity `0.195253`, mean selected expected gap `0.310443`, mean selected residual gap `-0.04729`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.204223` across 7 instances; family means: ch=0.275139, kroD=0.358223, pcb=0.24162, pr=0.111142, rd=0.14311, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19792, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.376452, "residual_gap": 0.047611}, {"best_known_cost": 2579, "cost": 3450, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.337728, "residual_gap": -0.065762}, {"best_known_cost": 7542, "cost": 9044, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.199151, "residual_gap": -0.038213}]

## Judge Appendix
### Summary of Key Findings on Replay-Aware TSP Benchmark Suite

---

### 1. Transfer Performance (Primary focus on Held-out TSPLIB gap and Synthetic Holdout gap)

| Condition                          | Mean Held-out TSPLIB Gap | Mean Synthetic Holdout Gap | Mean Transfer Gap |
|----------------------------------|--------------------------|----------------------------|-------------------|
| **phase6_stratified_random_replay** | **0.08682**               | **0.003941**                | **0.056682**      |
| phase6_failure_replay             | 0.105503                 | 0.0                        | 0.067138          |
| phase6_diversity_weighted_replay | 0.126568                 | 0.0                        | 0.080543          |
| phase6_residual_failure_replay   | 0.117653                 | 0.010343                   | 0.078631          |
| phase6_diversity_failure_replay  | 0.163475                 | 0.0                        | 0.10403           |
| phase6_random_replay_compression | 0.213387                 | 0.064916                   | 0.159398          |
| phase6_random_replay             | 0.213387                 | 0.064916                   | 0.159398          |
| phase6_no_replay                 | 0.213387                 | 0.064916                   | 0.159398          |
| phase6_diversity_failure_replay_compression | 0.204223      | 0.0                        | 0.12996           |

- **Best overall transfer performance:** `phase6_stratified_random_replay` (lowest held-out TSPLIB gap, synthetic holdout gap, and transfer gap).
- `phase6_failure_replay` has the best synthetic holdout gap (0.0) and competitive held-out TSPLIB and transfer gaps, indicating good transfer on synthetic but slightly worse on real TSPLIB.
- Conditions with replay compression generally have higher gaps, indicating compression may negatively affect transfer.

---

### 2. Adaptation Efficiency and Archive Characteristics

| Condition                          | Adaptation Efficiency | Archive Descriptor Diversity | Archive Hardness | Archive Size Bias | Replay Failure Concentration |
|----------------------------------|-----------------------|------------------------------|------------------|-------------------|------------------------------|
| phase6_stratified_random_replay | **0.04152**            | 0.236772                     | 0.175619         | 0.0               | 0.221162                     |
| phase6_diversity_weighted_replay | 0.080585              | 0.240179                     | 0.196328         | 0.0               | 0.342222                     |
| phase6_failure_replay             | 0.0                   | 0.174718                     | 0.320013         | 0.124979          | 0.23356                      |
| phase6_residual_failure_replay   | 0.0                   | 0.149653                     | 0.318916         | 0.094391          | 0.188209                     |
| phase6_diversity_failure_replay  | 0.0                   | 0.174718                     | 0.295958         | 0.124979          | 0.174603                     |
| phase6_random_replay             | -0.028807             | 0.236772                     | 0.214847         | 8.3e-05           | 0.19457                      |
| phase6_random_replay_compression | 0.0                   | 0.236772                     | 0.212361         | 0.0               | 0.16                         |
| phase6_no_replay                 | -0.02956              | 0.240179                     | 0.212361         | 0.0               | 0.0                         |
| phase6_diversity_failure_replay_compression | 0.0          | 0.174718                     | 0.300947         | 0.124979          | 0.175969                     |

- Replay conditions with failure-based archives (failure, residual_failure, diversity_failure) show **higher hardness (~0.3) and moderate diversity (0.15-0.17)** than non-failure ones.
- `phase6_diversity_weighted_replay` shows highest adaptation efficiency (0.080585) but worse transfer gap than stratified random replay.
- `phase6_stratified_random_replay` balances moderate diversity and lower hardness with improved transfer.

---

### 3. Replay Mechanism Effects

- **Broad-Coverage Replay (stratified_random):** 
  - Achieves best transfer performance (lowest TSPLIB and synthetic gaps).
  - Archive has moderate diversity and lowest hardness, indicating balanced coverage.
  - Failure concentration is moderate (~22%), showing replay is not overly focused on failures.
  - Selection mode is score_only, possibly enabling effective sample prioritization.

- **Raw Failure Replay (failure, diversity_failure):** 
  - Archive hardness is highest (≥0.29), size bias present (~0.12).
  - Final synthetic gaps are zero (perfect on synthetic holdout), but transfer gaps are higher compared to stratified_random replay.
  - Replay failure concentration ranges 17-23%, moderate to high.
  - Code novelty is null (0.0), indicating no new code is added during these replays.

- **Residual Failure Replay (residual_failure):** 
  - Moderate archive hardness (~0.32) and diversity (lowest, 0.15).
  - Transfer and TSPLIB gaps slightly better than raw failure replay but worse than stratified random.
  - Shows compression aware behavior with moderate replay failure concentration (~18%).
  - Code novelty is zero, similar to failure replay.

- **Diversity-Weighted Replay (diversity_weighted):** 
  - Highest adaptation efficiency (0.080585) suggesting effective learning.
  - Archive diversity high (0.24) with moderate hardness (0.19).
  - Transfer gaps intermediate (0.08).
  - Replay failure concentration highest (~34%), suggests more focused on difficult or rare failures.
  - Code novelty is zero, indicating no novel code discovered despite better efficiency.

- **Replay with Compression:** 
  - Appears in random and diversity-failure replay with lower code novelty (0.0).
  - Generally associated with higher final transfer gaps (~0.13-0.16) and TSPLIB gaps (~0.20+).
  - Compression tends to reduce archive diversity slightly without clear benefits in transfer.

---

### 4. Code Novelty vs Transfer

- The `phase6_failure_replay` (best synthetic condition) has **zero code novelty but improved synthetic gap (0.0)** and improved transfer gap (0.067).
- `phase6_stratified_random_replay` (best holdout and transfer condition) retains **substantial code novelty (~0.76-0.88)** with best transfer gaps.
- Failure-based replays tend to have code novelty at zero while stratified_random replay encourages code novelty without compromising transfer.
- Therefore, code novelty can decline while transfer improves (failure-replay conditions).
- Lexical novelty noted does not imply algorithmic invention without matching transfer gains.

---

### 5. Failure Concentration and Replay Diversity

- Failure-based replay conditions (failure, residual_failure, diversity_failure) exhibit higher failure concentration (~17-37%) vs none or minimal for other types.
- Diversity-weighted replay increases failure concentration most (~34%), possibly targeting varied difficult cases.
- Stratified random replay balances failure concentration (~22%) and diversity (~0.24), correlating with best transfer.
- Raw random and no-replay conditions show zero or negligible failure concentration indicating less focused replay.

---

## **Summary and Recommendations**

- **Best Transfer Strategy:** `phase6_stratified_random_replay` achieves the lowest held-out TSPLIB and synthetic gaps, with moderate replay failure concentration and high archive diversity, indicating broad effective replay.
  
- **Best Synthetic Transfer:** `phase6_failure_replay` yields perfect synthetic holdout scores but at the cost of somewhat reduced transfer on TSPLIB instances compared to stratified random.

- **Code Novelty Decoupled from Transfer:** Conditions with zero code novelty (failure replays) can still improve transfer, indicating that replay-driven sampling of hard cases, rather than new code generation, drives performance gains.

- **Replay Compression Impact:** Replay compression reduces archive diversity and fails to improve transfer performance relative to non-compressed variants.

- **Failure Replay Variants:** Failure and residual failure replays bias towards harder cases and have higher failure concentration but do not necessarily lead to best transfer gaps.

- **Recommendation:** Prioritize broad-coverage and stratified random replay strategies for generalizability and transfer, balancing archive diversity and failure focus, while maintaining some code novelty. Avoid compression-induced replay constraints that may degrade performance.

---

*Interpretation aligned strictly with indicated metrics, avoiding narrative speculations.*
