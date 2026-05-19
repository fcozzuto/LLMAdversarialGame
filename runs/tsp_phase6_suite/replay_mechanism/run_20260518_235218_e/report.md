# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_no_replay`.
- Best TSPLIB holdout gap: `phase6_no_replay`.
- Best synthetic holdout gap: `phase6_stratified_random_replay`.

## Run Metadata
- run_name: run_20260518_235218_e
- started_at_local: 2026-05-18 23:52:18
- finished_at_local: 2026-05-19 00:11:46
- duration_hhmm: 00:19
- duration_seconds: 1168.327
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.081748 | 0.002656 | 0.052987 | 0.236772 | 0.160079 | 0.0 | 0.788654 | 0.76 | 0.046072 |
| phase6_random_replay | random | score_only | False | 0.135463 | 0.001628 | 0.086796 | 0.236772 | 0.168557 | 0.19457 | 0.706409 | 0.76 | 0.062175 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.880734 | 0.56 | -0.028278 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.091054 | 0.0 | 0.057943 | 0.236772 | 0.15932 | 0.221162 | 0.625641 | 0.76 | 0.053 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.151349 | 0.001628 | 0.096905 | 0.236772 | 0.165767 | 0.130039 | 0.604411 | 0.76 | 0.052267 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.901432 | 0.56 | -0.027628 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.127487 | 0.0 | 0.081128 | 0.171206 | 0.265853 | 0.171783 | 0.836498 | 0.76 | 0.019349 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.20855 | 0.0 | 0.132714 | 0.171206 | 0.284075 | 0.173315 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.081748`, synthetic `0.002656`, combined `0.052987`.
- Accepted-epoch count `3`, mean accepted code novelty `0.788654`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.160079`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.046072` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.081748` across 7 instances; family means: ch=0.057102, kroD=0.074199, pcb=0.210741, pr=0.055816, rd=0.041719, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.002656` across 4 instances; family means: clustered_gaussian=0.010624, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3364, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.304382, "residual_gap": -0.099961}, {"best_known_cost": 14379, "cost": 17686, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.229988, "residual_gap": -0.09685}, {"best_known_cost": 629, "cost": 715, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.136725, "residual_gap": -0.120827}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.135463`, synthetic `0.001628`, combined `0.086796`.
- Accepted-epoch count `2`, mean accepted code novelty `0.706409`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.168557`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133995`, mean selected residual gap `0.007389`.
- Adaptation efficiency `0.062175` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.135463` across 7 instances; family means: ch=0.106939, kroD=0.071757, pcb=0.2365, pr=0.177683, rd=0.143236, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 9897, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.312251, "residual_gap": 0.067223}, {"best_known_cost": 14379, "cost": 18034, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.25419, "residual_gap": -0.072787}, {"best_known_cost": 2579, "cost": 3157, "expected_gap": 0.40442, "family": "a", "name": "a280", "optimality_gap": 0.224118, "residual_gap": -0.180302}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.880734`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.309513`, mean selected residual gap `0.066244`.
- Adaptation efficiency `-0.028278` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.406824, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.005506}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.003853}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132191`, mean selected residual gap `0.039175`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.404498, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.00318}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007052}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.091054`, synthetic `0.0`, combined `0.057943`.
- Accepted-epoch count `3`, mean accepted code novelty `0.625641`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.15932`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236082`, mean selected residual gap `-0.013045`.
- Adaptation efficiency `0.053` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.091054` across 7 instances; family means: ch=0.055346, kroD=0.069926, pcb=0.185671, pr=0.053782, rd=0.143236, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3572, "expected_gap": 0.405661, "family": "a", "name": "a280", "optimality_gap": 0.385033, "residual_gap": -0.020628}, {"best_known_cost": 629, "cost": 753, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.197138, "residual_gap": -0.059142}, {"best_known_cost": 14379, "cost": 16519, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.148828, "residual_gap": -0.172446}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.151349`, synthetic `0.001628`, combined `0.096905`.
- Accepted-epoch count `2`, mean accepted code novelty `0.604411`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.165767`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.263853`, mean selected expected gap `0.167628`, mean selected residual gap `-0.017093`.
- Adaptation efficiency `0.052267` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.151349` across 7 instances; family means: ch=0.135874, kroD=0.185029, pcb=0.226771, pr=0.14021, rd=0.142351, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.001628` across 4 instances; family means: clustered_gaussian=0.006511, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19809, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.377634, "residual_gap": 0.05444}, {"best_known_cost": 2579, "cost": 3336, "expected_gap": 0.404188, "family": "a", "name": "a280", "optimality_gap": 0.293525, "residual_gap": -0.110663}, {"best_known_cost": 629, "cost": 717, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.139905, "residual_gap": -0.114149}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.901432`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.264849`, mean selected residual gap `0.087544`.
- Adaptation efficiency `-0.027628` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.405196, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003878}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00644}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.127487`, synthetic `0.0`, combined `0.081128`.
- Accepted-epoch count `3`, mean accepted code novelty `0.836498`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.265853`, size bias `0.120322`, and failure concentration `0.171783`.
- Replay selection diversity `0.198691`, mean selected expected gap `0.299333`, mean selected residual gap `-0.032853`.
- Adaptation efficiency `0.019349` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.127487` across 7 instances; family means: ch=0.120487, kroD=0.142012, pcb=0.220568, pr=0.112048, rd=0.142731, st=0.034074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3117, "expected_gap": 0.403955, "family": "a", "name": "a280", "optimality_gap": 0.208608, "residual_gap": -0.195347}, {"best_known_cost": 629, "cost": 712, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.131955, "residual_gap": -0.135136}, {"best_known_cost": 14379, "cost": 16239, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.129355, "residual_gap": -0.192448}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.20855`, synthetic `0.0`, combined `0.132714`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.284075`, size bias `0.120322`, and failure concentration `0.173315`.
- Replay selection diversity `0.196315`, mean selected expected gap `0.309713`, mean selected residual gap `-0.023486`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.20855` across 7 instances; family means: ch=0.174542, kroD=0.343853, pcb=0.231006, pr=0.319779, rd=0.161315, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3539, "expected_gap": 0.407212, "family": "a", "name": "a280", "optimality_gap": 0.372237, "residual_gap": -0.034975}, {"best_known_cost": 7542, "cost": 10190, "expected_gap": 0.235826, "family": "berlin", "name": "berlin52", "optimality_gap": 0.351101, "residual_gap": 0.115275}, {"best_known_cost": 14379, "cost": 18028, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.253773, "residual_gap": -0.067738}]

## Judge Appendix
# Analysis of Phase 6 TSP Benchmark Suite

## Overview
- 9 conditions tested with various replay mechanisms.
- Main metrics: held-out TSPLIB gap and synthetic holdout gap (transfer evidence).
- Key replay mechanisms: no replay, random replay, failure replay, random replay with compression, stratified random replay, diversity-weighted replay, residual failure replay, diversity failure replay, diversity failure replay with compression.
- Focus on optimality gaps and transfer metrics.

---

## Summary Table of Key Metrics

| Condition                          | Replay Mode                | Selection Mode | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Replay Failure Concentration | Code Novelty (mean) |
|----------------------------------|----------------------------|----------------|------------------|---------------------|--------------------|-------------------|------------------|-----------------------------|---------------------|
| phase6_no_replay                 | none                       | score_only     | 0.0817           | 0.0027              | 0.0530             | 0.2368            | 0.1601           | 0.0                         | 0.789               |
| phase6_random_replay             | random                     | score_only     | 0.1355           | 0.0016              | 0.0868             | 0.2368            | 0.1686           | 0.1946                      | 0.706               |
| phase6_failure_replay            | failure                    | score_only     | 0.2134           | 0.0649              | 0.1594             | 0.1712            | 0.3480           | 0.262                       | 0.881               |
| phase6_random_replay_compression | random                    | novelty_gate   | 0.2134           | 0.0649              | 0.1594             | 0.2368            | 0.2148           | 0.195                       | 0.000               |
| phase6_stratified_random_replay | stratified_random          | score_only     | 0.0911           | 0.0000              | 0.0579             | 0.2368            | 0.1593           | 0.221                       | 0.626               |
| phase6_diversity_weighted_replay | diversity_weighted         | score_only     | 0.1513           | 0.0016              | 0.0969             | 0.2368            | 0.1658           | 0.130                       | 0.604               |
| phase6_residual_failure_replay   | residual_failure           | score_only     | 0.2134           | 0.0649              | 0.1594             | 0.1493            | 0.3389           | 0.292                       | 0.901               |
| phase6_diversity_failure_replay  | diversity_failure          | score_only     | 0.1275           | 0.0000              | 0.0811             | 0.1712            | 0.2659           | 0.172                       | 0.836               |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate   | 0.2086           | 0.0000              | 0.1327             | 0.1712            | 0.2841           | 0.173                       | 0.000               |

---

## Optimality and Transfer Performance

- **Best held-out TSPLIB gap and transfer gap:**
  - **phase6_no_replay (no replay):** TSPLIB gap 8.17%, transfer gap 5.30%
  - **phase6_stratified_random_replay:** synthetic gap is extremely low (0.0), TSPLIB gap improved (9.11%), transfer gap 5.79%

- **Worst transfer and TSPLIB gaps observed for:**
  - **phase6_failure_replay** and **phase6_random_replay_compression**: TSPLIB gap ~21%, transfer gap ~16%
    - Failure/concentration replay modes have higher gaps.

- **Random replay with score_only selection (phase6_random_replay) shows higher gaps than no replay.**

- **Stratified random replay yields a strong synthetic holdout gap (0.0), near-best TSPLIB and transfer gaps, consistent transfer improvement over baseline.**

- Code novelty is **zero** in compression-novelty-gated replay conditions but high in others.

---

## Replay Mechanism Insights

### 1. Replay Archive Diversity
- Diversity remains high (~0.23-0.24) for non-failure replay modes.
- Failure replay modes (failure, residual_failure, diversity_failure) show reduced final archive diversity (~0.15-0.17).
- Compression pressure reduces code novelty drastically but maintains archive descriptor diversity in some cases (~0.17-0.23).

### 2. Hardness and Size Bias
- Failure replay modes feature higher archive hardness (~0.26-0.35) and positive size bias (~0.09-0.12).
- Non-failure modes have moderate hardness (~0.16-0.17) and near-zero size bias.

### 3. Replay Failure Concentration
- Failure replay modes show increased failure concentration (~0.17-0.33).
- Random and stratified random replay have modest failure concentration (up to ~0.22).
- No replay has zero failure concentration, as expected.

### 4. Failure Concentration and Transfer
- Higher failure concentration in failure/replay modes correlates with worse transfer performance and higher optimality gaps.
- Best transfer coincides with moderate failure concentration and higher diversity (e.g., stratified random replay).

---

## Code Novelty vs Transfer

- Compression-novelty gating results in **zero code novelty**, yet transfer gaps increase (worsen).
- Conditions with **higher code novelty (0.6-0.9)** correspond to better or more consistent transfer gaps (~5-13%).
- This indicates that **code novelty decrease under compression leads to transfer degradation.**

---

## Specific Replay Mode Classes

| Replay Type                 | Observations                                                                                                   |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **No Replay**              | Best TSPLIB and transfer gaps, zero failure concentration, moderate archive diversity and hardness.            |
| **Random Replay (score_only)** | Increased TSPLIB and transfer gaps. Some replay failure concentration (~0.19). Moderate diversity.           |
| **Random Replay with Compression (novelty_gate)** | Identical worst-case gaps as failure replay modes, zero code novelty. Slight replay selection diversity.|
| **Stratified Random Replay** | Best synthetic gap (0.0), good transfer and TSPLIB gaps. Moderate failure concentration (~0.22).             |
| **Diversity-weighted Replay** | Higher TSPLIB and transfer gaps than stratified; moderate diversity and failure concentration.               |
| **Failure Replay**          | Highest gaps and failure concentration, lowest archive diversity, positive size bias.                         |
| **Residual Failure Replay** | Similar bad transfer/optimality performance as failure replay, with high failure concentration and low diversity.|
| **Diversity Failure Replay**| Moderate transfer/TSPLIB gaps, reduced diversity but better than failure replay.                              |
| **Diversity Failure Replay with Compression (novelty_gate)** | Zero code novelty, transfer gaps worsen compared to score_only.                          |

---

## Mechanism Study Summary

- Failure and residual-failure replay lead to concentrated replay on failures, reducing diversity and worsening transfer gaps.
- Diversity-weighted replay mediates this somewhat but still worse than stratified random or no replay.
- Stratified random replay balances selection diversity and failure concentration better, achieving good performance.
- Compression and novelty gating drastically reduce code novelty, which tracks with worse transfer gaps despite archive descriptor diversity.
- No replay achieves best transfer performance but no improvement in synthetic holdout gap beyond a baseline very close to zero.

---

# **Conservative Interpretation and Recommendations**

- The main evidence shows **"phase6_no_replay" and "phase6_stratified_random_replay" provide the best holdout transfer performance** based on TSPLIB gap (~8-9%) and synthetic holdout gap (near zero).
- Failure-based replay modes increase failure concentration and hardness but deteriorate transfer and optimality gaps significantly.
- Compression-driven reduction in code novelty coincides with impaired transfer, indicating **code novelty is correlated with transfer quality**.
- Stratified random replay improves synthetic holdout gap to zero without sacrificing archive diversity, implying balanced sampling aids transfer.
- Code novelty drops under compression/noulty-gate, but transfer improves only when code novelty is moderate/high; thus, **code novelty decline co-occurs with transfer degradation under compression**.
- Lexical or archive descriptor diversity alone is insufficient to ensure transfer; **mechanism design should consider failure concentration and code novelty explicitly.**

---

# Summary

| Insight                                         | Evidence Summary                                                                                                         |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Best transfer accuracy without replay           | phase6_no_replay: lowest TSPLIB(8.17%) & transfer gap(5.3%), zero failure concentration                                  |
| Best synthetic holdout gap with replay          | phase6_stratified_random_replay: synthetic gap 0%, TSPLIB gap ~9.1%, transfer gap 5.8%                                   |
| Failure replay worsens optimality & transfer    | Highest TSPLIB gap (~21%), transfer gap (~16%), and failure concentration (~0.26-0.33), reduced diversity                 |
| Diversity-weighted replay moderate performance  | TSPLIB gap ~15%, transfer gap ~9.7%, moderate failure concentration                                                      |
| Compression reduces code novelty, harms transfer| Compression with novelty gate results in zero code novelty & lower transfer quality despite archive descriptor diversity |
| Code novelty and transfer correlate              | Higher code novelty (~0.6-0.9) coincides with better transfer gaps                                                      |
| Replay failure concentration inversely affects transfer | Higher failure concentration correlates with worse transfer gaps                                                        |

---

# Final Note

- The best transfer and lowest optimality gaps arise *without failure-based replay* and with *stratified random replay*.
- Compression and novelty-gated replay reduce code novelty, which negatively aligns with transfer improvements.
- Therefore, replay schemes should balance failure coverage, archive diversity, and maintain code novelty to optimize transfer and algorithmic effectiveness.
