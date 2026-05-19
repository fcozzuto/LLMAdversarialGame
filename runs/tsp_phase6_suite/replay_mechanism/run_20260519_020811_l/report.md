# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_weighted_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_weighted_replay`.
- Best synthetic holdout gap: `phase6_failure_replay`.

## Run Metadata
- run_name: run_20260519_020811_l
- started_at_local: 2026-05-19 02:08:11
- finished_at_local: 2026-05-19 02:31:36
- duration_hhmm: 00:23
- duration_seconds: 1404.804
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.772439 | 0.56 | -0.032242 |
| phase6_random_replay | random | score_only | False | 0.114822 | 0.003941 | 0.074502 | 0.236772 | 0.193042 | 0.19457 | 0.804341 | 0.76 | 0.032453 |
| phase6_failure_replay | failure | score_only | False | 0.155899 | 0.0 | 0.099208 | 0.171206 | 0.269686 | 0.212826 | 0.0 | 0.76 | 0.0 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.148009 | 0.0 | 0.094188 | 0.236772 | 0.188451 | 0.19457 | 0.745793 | 0.76 | 0.013215 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.146551 | 0.0 | 0.09326 | 0.236772 | 0.146727 | 0.221162 | 0.841642 | 0.76 | 0.010515 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.100221 | 0.0 | 0.063777 | 0.236772 | 0.170475 | 0.130606 | 0.787962 | 0.76 | -0.001085 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.191306 | 0.001628 | 0.122332 | 0.121572 | 0.268644 | 0.449508 | 0.775017 | 0.76 | -0.002285 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.186646 | 0.010343 | 0.122536 | 0.171206 | 0.267501 | 0.171578 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.772439`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.032242` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003025}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00644}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.114822`, synthetic `0.003941`, combined `0.074502`.
- Accepted-epoch count `3`, mean accepted code novelty `0.804341`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.193042`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133281`, mean selected residual gap `0.023178`.
- Adaptation efficiency `0.032453` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.114822` across 7 instances; family means: ch=0.141003, kroD=0.104067, pcb=0.185454, pr=0.036113, rd=0.102781, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3474, "expected_gap": 0.40442, "family": "a", "name": "a280", "optimality_gap": 0.347034, "residual_gap": -0.057386}, {"best_known_cost": 7542, "cost": 9644, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706, "residual_gap": 0.045638}, {"best_known_cost": 14379, "cost": 17603, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.224216, "residual_gap": -0.097587}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.155899`, synthetic `0.0`, combined `0.099208`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.269686`, size bias `0.120322`, and failure concentration `0.212826`.
- Replay selection diversity `0.196656`, mean selected expected gap `0.322557`, mean selected residual gap `-0.013127`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.155899` across 7 instances; family means: ch=0.131091, kroD=0.144736, pcb=0.2172, pr=0.18495, rd=0.18445, st=0.097778.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3011, "expected_gap": 0.406824, "family": "a", "name": "a280", "optimality_gap": 0.167507, "residual_gap": -0.239317}, {"best_known_cost": 7542, "cost": 8593, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.139353, "residual_gap": -0.096473}, {"best_known_cost": 14379, "cost": 16167, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.124348, "residual_gap": -0.197163}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.148009`, synthetic `0.0`, combined `0.094188`.
- Accepted-epoch count `3`, mean accepted code novelty `0.745793`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.188451`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132484`, mean selected residual gap `0.003609`.
- Adaptation efficiency `0.013215` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.148009` across 7 instances; family means: ch=0.112974, kroD=0.224617, pcb=0.199772, pr=0.195934, rd=0.154235, st=0.035556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3094, "expected_gap": 0.404498, "family": "a", "name": "a280", "optimality_gap": 0.19969, "residual_gap": -0.204808}, {"best_known_cost": 14379, "cost": 16228, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.12859, "residual_gap": -0.192921}, {"best_known_cost": 7542, "cost": 8338, "expected_gap": 0.243888, "family": "berlin", "name": "berlin52", "optimality_gap": 0.105542, "residual_gap": -0.138346}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.146551`, synthetic `0.0`, combined `0.09326`.
- Accepted-epoch count `3`, mean accepted code novelty `0.841642`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.146727`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236082`, mean selected residual gap `-0.035819`.
- Adaptation efficiency `0.010515` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.146551` across 7 instances; family means: ch=0.133548, kroD=0.171832, pcb=0.231006, pr=0.224817, rd=0.110367, st=0.020741.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3572, "expected_gap": 0.405661, "family": "a", "name": "a280", "optimality_gap": 0.385033, "residual_gap": -0.020628}, {"best_known_cost": 629, "cost": 805, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.279809, "residual_gap": 0.023529}, {"best_known_cost": 14379, "cost": 17409, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.210724, "residual_gap": -0.11055}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.100221`, synthetic `0.0`, combined `0.063777`.
- Accepted-epoch count `2`, mean accepted code novelty `0.787962`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.170475`, size bias `8.3e-05`, and failure concentration `0.130606`.
- Replay selection diversity `0.263228`, mean selected expected gap `0.180927`, mean selected residual gap `0.000344`.
- Adaptation efficiency `-0.001085` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.100221` across 7 instances; family means: ch=0.114427, kroD=0.111064, pcb=0.214424, pr=0.036113, rd=0.051833, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3273, "expected_gap": 0.404188, "family": "a", "name": "a280", "optimality_gap": 0.269097, "residual_gap": -0.135091}, {"best_known_cost": 629, "cost": 684, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.08744, "residual_gap": -0.166614}, {"best_known_cost": 14379, "cost": 15352, "expected_gap": 0.317296, "family": "lin", "name": "lin105", "optimality_gap": 0.067668, "residual_gap": -0.249628}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.191306`, synthetic `0.001628`, combined `0.122332`.
- Accepted-epoch count `2`, mean accepted code novelty `0.775017`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.121572`, mean hardness `0.268644`, size bias `0.055669`, and failure concentration `0.449508`.
- Replay selection diversity `0.129326`, mean selected expected gap `0.252916`, mean selected residual gap `0.049495`.
- Adaptation efficiency `-0.002285` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.191306` across 7 instances; family means: ch=0.174453, kroD=0.309336, pcb=0.253003, pr=0.228497, rd=0.106068, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3657, "expected_gap": 0.405196, "family": "a", "name": "a280", "optimality_gap": 0.417991, "residual_gap": 0.012795}, {"best_known_cost": 629, "cost": 830, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.319555, "residual_gap": 0.057552}, {"best_known_cost": 14379, "cost": 18335, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.275123, "residual_gap": -0.053606}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.186646`, synthetic `0.010343`, combined `0.122536`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.267501`, size bias `0.120322`, and failure concentration `0.171578`.
- Replay selection diversity `0.201543`, mean selected expected gap `0.307782`, mean selected residual gap `-0.036014`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.186646` across 7 instances; family means: ch=0.099378, kroD=0.24251, pcb=0.273662, pr=0.340869, rd=0.225537, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3463, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.342769, "residual_gap": -0.061186}, {"best_known_cost": 7542, "cost": 9442, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.251923, "residual_gap": 0.006816}, {"best_known_cost": 14379, "cost": 17366, "expected_gap": 0.328131, "family": "lin", "name": "lin105", "optimality_gap": 0.207734, "residual_gap": -0.120397}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.303068`, mean selected residual gap `0.04692`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.407212, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.005894}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": -0.000821}]

## Judge Appendix
# TSP Benchmark Suite Replay-Aware Condition Analysis

## Summary of Best Conditions
- **Best Holdout (TSPLIB) Condition:** `phase6_diversity_weighted_replay`  
  - Final TSPLIB gap: 0.100221 (lowest across conditions)
- **Best Synthetic Holdout Condition:** `phase6_failure_replay`  
  - Synthetic gap: 0.0 (best possible)
- **Best Transfer Condition:** `phase6_diversity_weighted_replay`  
  - Transfer gap: 0.063777 (lowest transfer gap)
  
---

## Comparative Performance Overview

| Condition Name                    | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Replay Mode           | Selection Mode  |
|---------------------------------|------------------|---------------------|--------------------|-----------------------|-----------------|
| `phase6_no_replay`               | 0.213387         | 0.064916            | 0.159398           | none                  | score_only      |
| `phase6_random_replay`           | 0.114822         | 0.003941            | 0.074502           | random                | score_only      |
| `phase6_failure_replay`          | 0.155899         | 0.0                 | 0.099208           | failure               | score_only      |
| `phase6_random_replay_compression` | 0.148009      | 0.0                 | 0.094188           | random (compression)  | novelty_gate    |
| `phase6_stratified_random_replay` | 0.146551        | 0.0                 | 0.093260           | stratified_random     | score_only      |
| `phase6_diversity_weighted_replay` | **0.100221**    | 0.0                 | **0.063777**       | diversity_weighted    | score_only      |
| `phase6_residual_failure_replay` | 0.191306         | 0.001628            | 0.122332           | residual_failure      | score_only      |
| `phase6_diversity_failure_replay` | 0.186646        | 0.010343            | 0.122536           | diversity_failure     | score_only      |
| `phase6_diversity_failure_replay_compression` | 0.213387 | 0.064916       | 0.159398           | diversity_failure (compression) | novelty_gate |

- **Note:** Lower gaps represent better performance (closer to optimal).

---

## In-Depth Analysis

### 1. Optimality Gaps & Transfer Performance

- **Held-out TSPLIB Gap (main transfer metric):**
  - Best achieved by `phase6_diversity_weighted_replay` (0.100221), which is a substantial improvement over no replay (0.213387).
  - Other replay strategies yield moderate improvements but do not match the diversity-weighted replay's performance.
  
- **Synthetic Holdout Gap:**
  - Failure replay and variants (including stratified random) achieve zero or near-zero synthetic gap, signaling strong adaptation.
  - Raw random replay also has very low synthetic gap (0.003941), indicating good fitting on synthetic challenges.
  
- **Transfer Gap:**
  - Lowest transfer gap observed for `phase6_diversity_weighted_replay` at 0.063777.
  - Others, like failure replay and random replay, have moderate transfer gaps (~0.07-0.1).
  - No replay and diversity failure replay conditions have larger transfer gaps nearing 0.15-0.16.

### 2. Replay Archive Diversity & Hardness

| Condition                       | Archive Diversity | Archive Hardness | Archive Size Bias |
|--------------------------------|-------------------|------------------|-------------------|
| phase6_no_replay               | 0.240179          | 0.212361         | 0.0               |
| phase6_random_replay           | 0.240179          | 0.205529         | 0.0               |
| phase6_failure_replay          | 0.174718          | 0.333292         | 0.124979          |
| phase6_random_replay_compression | 0.240179        | 0.194479         | 0.0               |
| phase6_stratified_random_replay | 0.240179         | 0.159287         | 0.0               |
| phase6_diversity_weighted_replay | 0.240179        | 0.194959         | 0.0               |
| phase6_residual_failure_replay | 0.19662           | 0.334688         | 0.12889           |
| phase6_diversity_failure_replay | 0.174718          | 0.303871         | 0.124979          |
| phase6_diversity_failure_replay_compression | 0.174718 | 0.34902       | 0.124979          |

- Diversity-weighted replay maintains **high archive diversity (0.24)** with **moderate hardness (~0.20)** and no size bias.
- Failure-based replays tend to have **lower diversity (~0.17-0.20), higher hardness (~0.3-0.35)**, and notable positive size bias (~0.12).
- Random replay preserves diversity better than failure replays but with lower hardness.
- Compression pressure reduces archive size in some conditions but does not strongly affect diversity in diversity-weighted replay.

### 3. Replay Failure Concentration & Selection Diversity

| Condition                     | Mean Replay Failure Concentration | Mean Replay Selection Diversity | Mean Selected Expected Gap | Mean Selected Residual Gap |
|------------------------------|----------------------------------|-------------------------------|----------------------------|----------------------------|
| phase6_no_replay             | 0.0                              | 0.0                           | 0.0                        | 0.0                        |
| phase6_random_replay         | 0.19457                          | 0.262174                      | 0.133281                   | 0.023178                   |
| phase6_failure_replay        | 0.212826                         | 0.196656                      | 0.322557                   | -0.013127                  |
| phase6_random_replay_compression | 0.19457                      | 0.262174                      | 0.132484                   | 0.003609                   |
| phase6_stratified_random_replay | 0.221162                      | 0.187367                      | 0.236082                   | -0.035819                  |
| phase6_diversity_weighted_replay | 0.130606                     | 0.263228                      | 0.180927                   | 0.000344                   |
| phase6_residual_failure_replay | 0.449508                      | 0.129326                      | 0.252916                   | 0.000344                   |
| phase6_diversity_failure_replay | 0.171578                     | 0.201543                      | 0.307782                   | -0.036014                  |
| phase6_diversity_failure_replay_compression | 0.17024           | 0.199284                      | 0.303068                   | 0.04692                    |

- Diversity-weighted replay achieves **lower failure concentration (~0.13)** and **higher selection diversity (~0.26)**.
- Residual failure replay exhibits **high failure concentration (~0.45)** and low selection diversity (~0.13), likely leading to overfitting narrow failure modes.
- Failure replay has moderate to high failure concentration (~0.21), intermediate diversity.
- Random and stratified replay show moderate failure concentration (~0.19-0.22) and higher diversity (~0.18-0.26).

### 4. Code Novelty vs Transfer

- `phase6_diversity_weighted_replay` has **mean code novelty ~0.79** with best transfer.
- `phase6_failure_replay` has **zero code novelty** but excellent synthetic holdout and moderate transfer gains.
- Some diversity or compression modes exhibit **higher code novelty (~0.8-0.84)** with corresponding transfer benefits.
- Conditions with zero code novelty generally have lower transfer performance.

Indicates **transfer improvements can be achieved both with and without high code novelty** depending on replay strategy.

### 5. Replay Modes Summary

| Replay Type                  | Archive Behavior & Transfer Highlights                                |
|-----------------------------|----------------------------------------------------------------------|
| **No Replay**                | High TSPLIB gap, moderate synthetic gap, no replay dynamics          |
| **Random Replay**            | Maintains high archive diversity, lower hardness, improved transfer vs no replay |
| **Failure Replay**           | Lower diversity, higher hardness and size bias, 0 synthetic gap, moderate transfer |
| **Random Replay with Compression** | Maintains archive diversity with compression, similar transfer as failure replay |
| **Stratified Random Replay**| Slightly lower archive hardness, maintains diversity, good transfer |
| **Diversity-Weighted Replay**| Highest diversity, moderate hardness, best TSPLIB and transfer gaps |
| **Residual Failure Replay** | High hardness and failure concentration, higher TSPLIB gaps, less efficient adaptation |
| **Diversity Failure Replay**| Moderate diversity, higher failure concentration, intermediate transfer |
| **Diversity Failure Replay with Compression** | Similar to Diversity Failure Replay but with compression |

---

## Conservative Interpretation & Recommendations

- **Best transfer and holdout TSPLIB performance come from `phase6_diversity_weighted_replay`, which balances archive diversity and hardness, while maintaining low failure concentration and high replay selection diversity.**
- **Failure replay (raw or residual) can achieve zero synthetic gap but tends to have higher failure concentration and lower archive diversity, potentially causing overfitting and worse TSPLIB transfer performance.**
- **Compression-aware replay maintains diversity with slightly lower hardness, offering competitive transfer.**
- **Random-based replay types improve transfer moderately over no replay, benefiting from broad coverage and selection diversity.**
- **Notably, failure replay shows zero code novelty but improved synthetic and transfer gaps, indicating transfer gains can be realized without increased code novelty.**
- **Thus, code novelty metrics alone are insufficient indicators of algorithmic improvement; transfer gaps provide stronger evidence.**
- **Residual failure replay shows signs of failure concentration and over-specialization, leading to weaker adaptation despite hardness.**
- **Diversity-weighted replay carefully manages replay instances to focus on hard but diverse cases, enabling robust transfer.**

---

## Summary

| Aspect              | Conclusion                                                         |
|---------------------|-------------------------------------------------------------------|
| Transfer Efficacy   | Highest under diversity-weighted replay, followed by random and stratified replay. Failure-based replays are mixed. |
| Replay Diversity    | Diversity-weighted and random replay maintain higher archive and selection diversity, linked to better generalization. |
| Failure Concentration| Lower in diversity-weighted replay; high in residual failure replay correlates with lower transfer. |
| Code Novelty        | Not strongly correlated with transfer gains; failure replay shows no novelty but some transfer improves. |
| Compression Effects | Compression-aware random replay sustains diversity and transfer; compression impact depends on replay strategy. |

---

# Final Note

**Prioritize `phase6_diversity_weighted_replay` for best transfer and generalization with balanced archive diversity and failure concentration. Failure replay provides excellent synthetic fitting but risks over-concentration and reduced generalization. Code novelty alone does not explain transfer improvements.**
