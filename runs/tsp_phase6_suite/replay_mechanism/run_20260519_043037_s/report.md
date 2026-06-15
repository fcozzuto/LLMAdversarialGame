# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_random_replay_compression`.
- Best TSPLIB holdout gap: `phase6_random_replay_compression`.
- Best synthetic holdout gap: `phase6_failure_replay`.

## Run Metadata
- run_name: run_20260519_043037_s
- started_at_local: 2026-05-19 04:30:37
- finished_at_local: 2026-05-19 04:50:54
- duration_hhmm: 00:20
- duration_seconds: 1217.138
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.0 | 0.840932 | 0.56 | -0.029616 |
| phase6_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.901541 | 0.56 | -0.027625 |
| phase6_failure_replay | failure | score_only | False | 0.109966 | 0.0 | 0.069978 | 0.171206 | 0.273059 | 0.214199 | 0.815934 | 0.76 | 0.061169 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.109154 | 0.0 | 0.069462 | 0.236772 | 0.15889 | 0.19457 | 0.690544 | 0.76 | 0.043613 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.185243 | 0.001628 | 0.118474 | 0.236772 | 0.193893 | 0.221162 | 0.654646 | 0.76 | 0.054327 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.16851 | 0.0 | 0.107234 | 0.236772 | 0.165675 | 0.130039 | 0.756331 | 0.76 | 0.019698 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.192759 | 0.0 | 0.122665 | 0.113626 | 0.251656 | 0.256191 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.842788 | 0.56 | -0.029551 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.136485 | 0.015447 | 0.092471 | 0.171206 | 0.244383 | 0.171578 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.840932`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.029616` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003025}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.133545}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 8.4e-05}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.901541`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.134046`, mean selected residual gap `0.03732`.
- Adaptation efficiency `-0.027625` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.40442, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003102}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328131, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.000682}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.109966`, synthetic `0.0`, combined `0.069978`.
- Accepted-epoch count `2`, mean accepted code novelty `0.815934`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.273059`, size bias `0.120322`, and failure concentration `0.214199`.
- Replay selection diversity `0.192353`, mean selected expected gap `0.321931`, mean selected residual gap `-0.012243`.
- Adaptation efficiency `0.061169` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.109966` across 7 instances; family means: ch=0.126975, kroD=0.072697, pcb=0.242388, pr=0.099955, rd=0.02225, st=0.078519.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3648, "expected_gap": 0.406824, "family": "a", "name": "a280", "optimality_gap": 0.414502, "residual_gap": 0.007678}, {"best_known_cost": 629, "cost": 858, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.36407, "residual_gap": 0.10938}, {"best_known_cost": 14379, "cost": 17626, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.225815, "residual_gap": -0.103819}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.109154`, synthetic `0.0`, combined `0.069462`.
- Accepted-epoch count `3`, mean accepted code novelty `0.690544`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.15889`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132412`, mean selected residual gap `-0.017766`.
- Adaptation efficiency `0.043613` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.109154` across 7 instances; family means: ch=0.126737, kroD=0.112943, pcb=0.226062, pr=0.091976, rd=0.036662, st=0.042963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3179, "expected_gap": 0.404498, "family": "a", "name": "a280", "optimality_gap": 0.232648, "residual_gap": -0.17185}, {"best_known_cost": 14379, "cost": 16217, "expected_gap": 0.322762, "family": "lin", "name": "lin105", "optimality_gap": 0.127825, "residual_gap": -0.194937}, {"best_known_cost": 7542, "cost": 8217, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.089499, "residual_gap": -0.151419}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.185243`, synthetic `0.001628`, combined `0.118474`.
- Accepted-epoch count `2`, mean accepted code novelty `0.654646`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.193893`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236305`, mean selected residual gap `-0.000366`.
- Adaptation efficiency `0.054327` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.185243` across 7 instances; family means: ch=0.135823, kroD=0.245093, pcb=0.259798, pr=0.226833, rd=0.2, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3475, "expected_gap": 0.405661, "family": "a", "name": "a280", "optimality_gap": 0.347421, "residual_gap": -0.05824}, {"best_known_cost": 7542, "cost": 10022, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.328825, "residual_gap": 0.092203}, {"best_known_cost": 629, "cost": 741, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.17806, "residual_gap": -0.07822}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.16851`, synthetic `0.0`, combined `0.107234`.
- Accepted-epoch count `2`, mean accepted code novelty `0.756331`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.165675`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.270615`, mean selected expected gap `0.151903`, mean selected residual gap `-0.015067`.
- Adaptation efficiency `0.019698` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.16851` across 7 instances; family means: ch=0.159265, kroD=0.150606, pcb=0.213675, pr=0.318633, rd=0.130721, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3295, "expected_gap": 0.404188, "family": "a", "name": "a280", "optimality_gap": 0.277627, "residual_gap": -0.126561}, {"best_known_cost": 14379, "cost": 18091, "expected_gap": 0.329244, "family": "lin", "name": "lin105", "optimality_gap": 0.258154, "residual_gap": -0.07109}, {"best_known_cost": 629, "cost": 675, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.073132, "residual_gap": -0.180922}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.192759`, synthetic `0.0`, combined `0.122665`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.113626`, mean hardness `0.251656`, size bias `0.072026`, and failure concentration `0.256191`.
- Replay selection diversity `0.151242`, mean selected expected gap `0.284426`, mean selected residual gap `0.051316`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192759` across 7 instances; family means: ch=0.191087, kroD=0.341035, pcb=0.195144, pr=0.235736, rd=0.170038, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3544, "expected_gap": 0.405196, "family": "a", "name": "a280", "optimality_gap": 0.374176, "residual_gap": -0.03102}, {"best_known_cost": 629, "cost": 848, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.348172, "residual_gap": 0.086169}, {"best_known_cost": 14379, "cost": 18820, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.308853, "residual_gap": -0.019988}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.842788`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301037`, mean selected residual gap `0.048952`.
- Adaptation efficiency `-0.029551` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.002637}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.124006}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.000807}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.136485`, synthetic `0.015447`, combined `0.092471`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.244383`, size bias `0.120322`, and failure concentration `0.171578`.
- Replay selection diversity `0.197858`, mean selected expected gap `0.3103`, mean selected residual gap `-0.054684`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.136485` across 7 instances; family means: ch=0.136816, kroD=0.200855, pcb=0.192918, pr=0.133378, rd=0.107206, st=0.047407.
- Panel `synthetic_holdout` mean gap `0.015447` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.061786, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3450, "expected_gap": 0.407212, "family": "a", "name": "a280", "optimality_gap": 0.337728, "residual_gap": -0.069484}, {"best_known_cost": 7542, "cost": 9644, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706, "residual_gap": 0.045638}, {"best_known_cost": 14379, "cost": 17366, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.207734, "residual_gap": -0.118923}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Suite Results

## Overview

- **Best holdout condition:** `phase6_random_replay_compression`
- **Best synthetic condition:** `phase6_failure_replay`
- **Best transfer condition:** `phase6_random_replay_compression`
- **Total conditions analyzed:** 9

---

## Transfer Performance (Key Metrics)

| Condition                          | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap |
|----------------------------------|-----------------|--------------------|-------------------|
| phase6_no_replay                 | 0.213387        | 0.064916           | 0.159398          |
| phase6_random_replay             | 0.213387        | 0.064916           | 0.159398          |
| phase6_failure_replay            | **0.109966**    | **0.000000**       | **0.069978**      |
| phase6_random_replay_compression | **0.109154**    | **0.000000**       | **0.069462**      |
| phase6_stratified_random_replay  | 0.185243        | 0.001628           | 0.118474          |
| phase6_diversity_weighted_replay | 0.168510        | 0.000000           | 0.107234          |
| phase6_residual_failure_replay   | 0.192759        | 0.000000           | 0.122665          |
| phase6_diversity_failure_replay  | 0.213387        | 0.064916           | 0.159398          |
| phase6_diversity_failure_replay_compression | 0.136485 | 0.015447           | 0.092471          |

- **Inference:**  
  - `phase6_failure_replay` and `phase6_random_replay_compression` achieve the lowest TSPLIB and synthetic holdout gaps, indicating superior transfer performance.  
  - The no replay baseline and simple random replay achieve higher gaps, showing less transfer effectiveness.  
  - Stratified random, diversity-weighted, and residual failure replays show intermediate transfer gaps.  
  - Diversity failure replays show weaker transfer despite some replay.  
  - Compression in replay can improve transfer gap significantly (`phase6_random_replay_compression` vs `phase6_random_replay`), even with some cost to code novelty.

---

## Replay Archive Characteristics and Mechanism Insights

| Condition                          | Replay Mode               | Compression | Archive Diversity | Archive Hardness | Archive Size Bias | Failure Concentration | Selection Diversity | Code Novelty Mean | Complexity Mean |
|----------------------------------|--------------------------|-------------|-------------------|------------------|-------------------|-----------------------|---------------------|-------------------|----------------|
| phase6_no_replay                 | none                     | No          | 0.240179          | 0.212361         | ~0.0              | 0.0                   | 0.0                 | 0.840932          | 0.56           |
| phase6_random_replay             | random                   | No          | 0.240179          | 0.212361         | ~0.0              | 0.19457               | 0.262174            | 0.901541          | 0.56           |
| phase6_failure_replay            | failure                  | No          | 0.174718          | 0.334281         | 0.124979          | 0.214199              | 0.192353            | 0.815934          | 0.76           |
| phase6_random_replay_compression | random                   | Yes         | 0.240179          | 0.166844         | ~0.0              | 0.19457               | 0.262174            | 0.690544          | 0.76           |
| phase6_stratified_random_replay  | stratified_random        | No          | 0.240179          | 0.204653         | ~0.0              | 0.221162              | 0.187367            | 0.654646          | 0.76           |
| phase6_diversity_weighted_replay | diversity_weighted        | No          | 0.240179          | 0.184688         | ~0.0              | 0.130039              | 0.270615            | 0.756331          | 0.76           |
| phase6_residual_failure_replay   | residual_failure          | No          | 0.167691          | 0.348023         | 0.089671          | 0.256191              | 0.151242            | 0.0               | 0.76           |
| phase6_diversity_failure_replay  | diversity_failure         | No          | 0.174718          | 0.34902          | 0.124979          | 0.17024               | 0.199284            | 0.842788          | 0.56           |
| phase6_diversity_failure_replay_compression | diversity_failure | Yes        | 0.174718          | 0.319545         | 0.124979          | 0.171578              | 0.197858            | 0.0               | 0.76           |

- **Observations:**
  - Replay diversification mechanisms (random, stratified random, diversity-weighted) maintain higher archive descriptor diversity and balanced hardness.
  - Failure replays (failure, residual_failure, diversity_failure) result in higher archive hardness and some positive archive size bias.
  - Compression pressures decrease average code novelty but can improve transfer gaps (see phase6_random_replay_compression).
  - Residual failure replays exhibit highest failure concentration and lowest code novelty, with zero mean code novelty in residual and diversity failure with compression.
  - Selection diversity highest in random and diversity-weighted replays, lowest when replay mode is none or residual failure.
  - Elite archive sizes are larger with replay than no replay, possibly indicating more robust elite selection.

---

## Optimality Gap and Failure Concentration Summary

- **Best TSPLIB gaps (~0.11) and transfer gaps (~0.07):** Seen in `phase6_failure_replay` and `phase6_random_replay_compression`.  
- **Baseline (no replay):** TSPLIB gap ~0.21 with no replay failure concentration and no replay selection diversity.  
- Failure replay modes help reduce gaps but tend to concentrate failures more (0.21-0.26 failure concentration).  
- Compression-aware replay (`phase6_random_replay_compression`) achieves low transfer and TSPLIB gaps with moderate failure concentration (0.19 to 0.25) and balanced diversity.

---

## Code Novelty and Transfer Relation

- `phase6_random_replay_compression` reduces code novelty mean (~0.69) compared to random replay (~0.90) but improves transfer metrics, indicating **code novelty decrease concurrent with transfer improvement**. This suggests replay compression drives more general transfer with less code diversity.  
- Residual failure and diversity failure replays with compression show zero mean code novelty, suggesting replay pressure impacts code novelty.  
- High code novelty alone (e.g., random replay) does not guarantee best transfer.

---

## Replay Mode Distinctions

- **No replay**: No replay, no failure concentration, zero selection diversity, high code novelty but poor transfer gaps.  
- **Random replay**: Broad, random replays increase selection diversity with moderate failure concentration and no compression pressure, similar transfer to no replay.  
- **Failure replay**: Replay conditioned on failure cases increases archive hardness and transfer, reduces synthetic gap to 0.0, but concentrates failures moderately (~0.21).  
- **Random replay compression**: Broad coverage replay with compression pressure reduces archive hardness, reduces transfer gap most significantly, with moderate failure concentration and reduced code novelty.  
- **Stratified random replay**: More structured replay slightly improves over random replay, but not as good as failure-based or compression replay.  
- **Diversity-weighted replay**: Maintains high archive diversity and selection diversity with moderate hardness, resulting in intermediate transfer gains.  
- **Residual failure replay**: Replay samples residual failures only, with highest failure concentration (~0.25), zero mean code novelty, and moderate TSPLIB gap (worse than failure replay).  
- **Diversity failure replay**: Combines failure replay with diversity weighting, but results in no transfer improvement over baseline, likely due to complexity or failure concentration effects.  
- **Diversity failure replay compression**: Adds compression to diversity failure replay, slightly better than diversity failure alone but still worse than failure replay.

---

## Summary Conclusions

- Failure-based replay (`phase6_failure_replay`) and random replay with compression (`phase6_random_replay_compression`) achieve **best overall transfer to holdout TSPLIB and synthetic instances**, halving mean gaps compared to no-replay baseline.  
- Compression-aware replay reduces code novelty but enhances transfer, indicating code novelty decrease co-occurs with transfer improvement here.  
- Random and diversity-weighted replays increase code novelty and selection diversity but do not improve transfer as effectively as failure replay.  
- Residual failure replay has concentrated failures in archive, zero code novelty, limiting transfer benefits.  
- Diversity failure replay conditions produce poor transfer performance, suggesting failure concentration and replay complexity hinder benefit.  
- Archive diversity tracks with replay mode designed for broad coverage and diversity weighting, while failure replay trades off diversity for hardness and transfer gains.

---

# Key Recommendation

**Employ failure replay and compression-aware broad coverage replay protocols for most effective transfer with balanced archive diversity, moderate failure concentration, and good final complexity.** Avoid residual-only failure and diversity failure replays as they show weak transfer despite potential replay mechanism sophistication.

---

# End of Analysis
