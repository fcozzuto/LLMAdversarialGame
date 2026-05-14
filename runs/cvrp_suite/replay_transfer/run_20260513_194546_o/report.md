# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_194546_o
- started_at_local: 2026-05-13 19:45:46
- finished_at_local: 2026-05-13 19:48:51
- duration_hhmm: 00:03
- duration_seconds: 185.594
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.226355 | 0.0 | 0.125753 | 0.866496 | 0.78 | 0.032626 |
| cvrp_random_replay | random | score_only | False | 0.260006 | 0.005376 | 0.146837 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay | failure | score_only | False | 0.237267 | 0.05147 | 0.154691 | 0.0 | 0.78 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.280918 | 0.047765 | 0.177294 | 0.867268 | 0.78 | -0.024957 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.226355`, synthetic `0.0`, combined `0.125753`.
- Accepted-epoch count `2`, mean accepted code novelty `0.866496`, and final complexity `0.78`.
- Adaptation efficiency `0.032626` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.226355` across 5 instances; family means: A=0.085515, B=0.258238, E=0.287908, P=0.241877.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: alternating_belt=0.0, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.260006`, synthetic `0.005376`, combined `0.146837`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.260006` across 5 instances; family means: A=0.128272, B=0.262983, E=0.326296, P=0.319495.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.237267`, synthetic `0.05147`, combined `0.154691`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.237267` across 5 instances; family means: A=0.206806, B=0.200949, E=0.303263, P=0.274368.
- Panel `synthetic_holdout` mean gap `0.05147` across 4 instances; family means: alternating_belt=0.049043, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.156836.
- Worst recent training cases: [{"best_known_cost": 784, "cost": 1094, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.395408}, {"best_known_cost": 458, "cost": 596, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.30131}, {"best_known_cost": 937, "cost": 1203, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.283885}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.280918`, synthetic `0.047765`, combined `0.177294`.
- Accepted-epoch count `2`, mean accepted code novelty `0.867268`, and final complexity `0.78`.
- Adaptation efficiency `-0.024957` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.280918` across 5 instances; family means: A=0.171902, B=0.36757, E=0.322457, P=0.17509.
- Panel `synthetic_holdout` mean gap `0.047765` across 4 instances; family means: alternating_belt=0.082088, clustered_demand=0.043468, corridor_split=0.065504, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 595, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.299127}, {"best_known_cost": 937, "cost": 1203, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.283885}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

## Judge Appendix
# CVRP Benchmark Suite Summary and Interpretation

| Condition                      | Replay Mode               | Final CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Final Code Novelty | Complexity | Notes                                                   |
|-------------------------------|--------------------------|-------------------|----------------------|--------------|--------------------|------------|---------------------------------------------------------|
| **cvrp_no_replay** (best)      | None                     | **0.226355**      | **0.0**              | **0.125753** | 0.8665             | 0.78       | Best transfer and holdout gaps; high code novelty       |
| cvrp_random_replay             | Random replay            | 0.260006          | 0.005376             | 0.146837     | 0.0                | 0.58       | Lower code novelty; worse CVRPLIB gap but better transfer gap than failure replays |
| cvrp_failure_replay            | Failure replay           | 0.237267          | 0.05147              | 0.154691     | 0.0                | 0.78       | Higher transfer and synthetic gaps; zero code novelty    |
| cvrp_failure_replay_compression| Failure replay + compress| 0.280918          | 0.047765             | 0.177294     | 0.8673             | 0.78       | Worst CVRPLIB gap and transfer; high code novelty but negative adaptation efficiency |

---

## Key Points

- **Transfer and Optimality Gaps**  
  The **no replay** condition achieves the lowest optimality gaps on both CVRPLIB held-out and synthetic benchmarks and the best transfer gap (0.125753). This indicates superior generalization and transfer capabilities compared to all replay modes.

- **Impact of Replay Modes**  
  - **Random replay** and **failure replay** reduce code novelty to zero, suggesting stagnation in code evolution despite some varying transfer gaps (~0.15).  
  - **Failure replay with compression-aware replay** maintains high code novelty similar to no replay (~0.87) but yields the worst gaps and negative adaptation efficiency, indicating degraded solution quality despite novelty.

- **Code Novelty vs Transfer Tradeoff**  
  High code novelty alone does not guarantee improved transfer performance:  
  - No replay and compression-aware failure replay have high novelty, but only no replay delivers optimal transfer and holdout gaps.  
  - Replay (random or failure) reduces novelty and results in generally worse gaps than no replay.

- **Complexity**  
  Complexity is consistently higher (~0.78) except for random replay (0.58). Lower complexity under random replay does not translate to better transfer or optimality outcomes.

- **Adaptation Efficiency**  
  Only no replay shows positive adaptation efficiency (~0.033), implying more effective adaptation during training; other replay conditions show zero or negative efficiency.

---

## Conclusion

- The **no replay** condition outperforms all replay variants on the main transfer metrics (held-out CVRPLIB and synthetic holdout gaps), demonstrating better transfer and generalization despite high complexity.  
- Replay conditions reduce code novelty and do not offer improved transfer; compression-aware failure replay maintains novelty but is detrimental in solution quality and transfer metrics.  
- Code novelty metrics confirm no replay maintains algorithmic innovation effectively aligned with improved performance.  
- Lexical/code novelty without supporting transfer/optimality gains (as in compression-aware replay) should not be considered algorithmic invention.

---

# Summary

The evidence conservatively supports **no replay** as the preferred adaptation mode in this CVRP benchmark suite based on optimality gaps and transfer metrics. Replay methods, including random or failure replays with or without compression, do not improve transfer and often degrade performance, even when code novelty is high.
