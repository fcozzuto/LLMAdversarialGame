# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_195514_r
- started_at_local: 2026-05-13 19:55:14
- finished_at_local: 2026-05-13 19:58:09
- duration_hhmm: 00:03
- duration_seconds: 175.401
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.247848 | 0.012431 | 0.143218 | 0.834087 | 0.58 | 0.039893 |
| cvrp_random_replay | random | score_only | False | 0.244749 | 0.005376 | 0.138361 | 0.820371 | 0.58 | 0.035545 |
| cvrp_failure_replay | failure | score_only | False | 0.241217 | 0.005376 | 0.136399 | 0.8 | 0.78 | 0.022805 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.247998 | 0.005376 | 0.140166 | 0.842052 | 0.58 | 0.049725 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.247848`, synthetic `0.012431`, combined `0.143218`.
- Accepted-epoch count `2`, mean accepted code novelty `0.834087`, and final complexity `0.58`.
- Adaptation efficiency `0.039893` and archive sizes `{'worst_cases': 5, 'failure_cases': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.247848` across 5 instances; family means: A=0.143979, B=0.254873, E=0.284069, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.012431` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.028221.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.244749`, synthetic `0.005376`, combined `0.138361`.
- Accepted-epoch count `2`, mean accepted code novelty `0.820371`, and final complexity `0.58`.
- Adaptation efficiency `0.035545` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.244749` across 5 instances; family means: A=0.115183, B=0.259605, E=0.287908, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.241217`, synthetic `0.005376`, combined `0.136399`.
- Accepted-epoch count `2`, mean accepted code novelty `0.8`, and final complexity `0.78`.
- Adaptation efficiency `0.022805` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.241217` across 5 instances; family means: A=0.094241, B=0.241391, E=0.287908, P=0.341155.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 602, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.31441}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.247998`, synthetic `0.005376`, combined `0.140166`.
- Accepted-epoch count `2`, mean accepted code novelty `0.842052`, and final complexity `0.58`.
- Adaptation efficiency `0.049725` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.247998` across 5 instances; family means: A=0.115183, B=0.259605, E=0.287908, P=0.31769.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 602, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.31441}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Replay-Aware CVRP Benchmark Results

| Condition                      | Replay Mode    | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Complexity | Code Novelty (mean) | Notes on Replay Mode                    |
|-------------------------------|----------------|-------------------|---------------------|--------------------|------------|---------------------|----------------------------------------|
| **cvrp_no_replay**             | none           | 0.2478            | 0.0124              | 0.1432             | 0.58       | 0.8341              | Baseline without replay                |
| **cvrp_random_replay**         | random         | 0.2447            | **0.0054**          | 0.1384             | 0.58       | 0.8204              | Improved transfer on synthetic holdout|
| **cvrp_failure_replay**        | failure        | **0.2412**        | 0.0054              | **0.1364**         | 0.78       | 0.8000              | Best transfer on CVRPLIB & overall    |
| **cvrp_failure_replay_compression** | failure + compression | 0.2480       | 0.0054              | 0.1402             | 0.58       | 0.8421              | Compression pressure reduces transfer |

---

### Interpretations

- **Optimality gaps on held-out CVRPLIB**:  
  - Best gap: *cvrp_failure_replay* (0.2412), followed closely by *cvrp_random_replay* (0.2447), both better than *no_replay* (0.2478).  
  - *Failure_replay_compression* is slightly worse (0.2480), likely due to compression pressure.

- **Synthetic holdout gaps**:  
  - All replay conditions achieve lower synthetic gaps (0.0054–0.0124) compared to no replay (0.0124).  
  - *cvrp_random_replay* and *cvrp_failure_replay* tie with the best synthetic gaps (0.0054).  
  - Indicates improved generalization on synthetic instances by replay conditions.

- **Transfer gap (combined measure)**:  
  - Lowest gap in *cvrp_failure_replay* (0.1364), then *cvrp_random_replay* (0.1384), both better than no replay (0.1432).  
  - Compression-aware replay (*failure_replay_compression*) again underperforms slightly (0.1402).

- **Complexity and Behavior**:  
  - *cvrp_failure_replay* has higher complexity (0.78) than others (0.58), potentially reflecting more refined behavior profiles (clustered_constructor).  
  - Others maintain balanced behaviors with lower complexity.

- **Code novelty**:  
  - Slightly decreases from *no_replay* (0.8341) to *failure_replay* (0.8000), despite improved transfer and optimality.  
  - Compression replay condition recovers novelty (0.8421) but at cost of transfer performance.  
  - Indicates reduced code novelty can coincide with increased transfer effectiveness.

- **Replay modes distinguished**:  
  - *No replay* baseline performs worst on transfer metrics.  
  - *Random replay* improves synthetic transfer gap best but not held-out CVRPLIB gap.  
  - *Failure replay* (focused on failure cases) yields best overall transfer, balancing held-out CVRPLIB and synthetic improvements.  
  - *Failure replay with compression* degrades transfer somewhat despite improved code novelty, showing compression pressure may limit beneficial adaptation.

---

### Conservative Conclusions

- The **failure replay** condition clearly achieves the best transfer performance on held-out CVRPLIB instances and combined transfer metrics, despite having slightly lower code novelty and higher complexity. This suggests targeted replay of failures is beneficial for transfer.

- **Random replay** achieves the smallest synthetic holdout gaps but slightly underperforms on CVRPLIB held-out gaps, indicating that coverage of failure cases, not replay diversity alone, may be more critical for real benchmark transfer.

- Compression-aware replay reduces the effectiveness of transfer, indicating that replay compression pressure might inhibit adaptation useful for improving CVRP benchmarks.

- Higher code novelty does not necessarily translate to improved transfer; in fact, the best transfer result coincides with a moderate drop in code novelty.

- **No replay** lags behind all replay-based conditions on transfer metrics, confirming some form of replay helps generalization.

---

### Recommendations

- Prioritize **failure replay** for improving transfer on realistic CVRP benchmarks.

- Avoid compression pressure in replay if transfer performance is paramount.

- Monitor complexity increase under failure replay but accept it given transfer gains.

- Interpret code novelty numbers cautiously; decreased novelty with improved transfer suggests novelty alone is insufficient to claim algorithmic invention.

---

This assessment relies primarily on optimality gaps on held-out CVRPLIB instances and synthetic holdout benchmarks to evaluate transfer quality, aligning with established evaluation criteria.
