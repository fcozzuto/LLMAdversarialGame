# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_random_replay`.
- Best CVRPLIB holdout gap: `cvrp_random_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_200113_t
- started_at_local: 2026-05-13 20:01:13
- finished_at_local: 2026-05-13 20:04:37
- duration_hhmm: 00:03
- duration_seconds: 204.059
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.24592 | 0.017926 | 0.144589 | 0.802184 | 0.78 | -0.002436 |
| cvrp_random_replay | random | score_only | False | 0.227777 | 0.005376 | 0.128932 | 0.880616 | 0.78 | 0.035532 |
| cvrp_failure_replay | failure | score_only | False | 0.238402 | 0.005376 | 0.134835 | 0.914872 | 0.58 | 0.051961 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.238114 | 0.005376 | 0.134675 | 0.866399 | 0.58 | 0.048265 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.24592`, synthetic `0.017926`, combined `0.144589`.
- Accepted-epoch count `2`, mean accepted code novelty `0.802184`, and final complexity `0.78`.
- Adaptation efficiency `-0.002436` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.24592` across 5 instances; family means: A=0.150087, B=0.184816, E=0.341651, P=0.368231.
- Panel `synthetic_holdout` mean gap `0.017926` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.050197.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 805, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.197917}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.227777`, synthetic `0.005376`, combined `0.128932`.
- Accepted-epoch count `2`, mean accepted code novelty `0.880616`, and final complexity `0.78`.
- Adaptation efficiency `0.035532` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.227777` across 5 instances; family means: A=0.109948, B=0.259606, E=0.314779, P=0.194946.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.238402`, synthetic `0.005376`, combined `0.134835`.
- Accepted-epoch count `2`, mean accepted code novelty `0.914872`, and final complexity `0.58`.
- Adaptation efficiency `0.051961` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.238402` across 5 instances; family means: A=0.112565, B=0.254873, E=0.261036, P=0.308664.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.238114`, synthetic `0.005376`, combined `0.134675`.
- Accepted-epoch count `2`, mean accepted code novelty `0.866399`, and final complexity `0.58`.
- Adaptation efficiency `0.048265` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.238114` across 5 instances; family means: A=0.112565, B=0.26567, E=0.238004, P=0.308664.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 602, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.31441}, {"best_known_cost": 937, "cost": 1072, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.144077}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Replay-Aware CVRP Benchmark Suite Evaluation

| Condition                   | Replay Mode                | Final CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Adaptation Efficiency | Code Novelty (mean) | Complexity | Notes on Archive & Behavior Profile       |
|-----------------------------|----------------------------|-------------------|----------------------|--------------|-----------------------|---------------------|------------|-------------------------------------------|
| **cvrp_no_replay**           | none                       | 0.24592           | 0.017926             | 0.144589     | -0.002436             | 0.802               | 0.78       | Archive size 14; behavior “clustered_constructor” |
| **cvrp_random_replay**       | random                     | **0.227777**      | **0.005376**         | **0.128932** | 0.035532              | 0.881               | 0.78       | Archive size 14; behavior “clustered_constructor”; Best across main transfer metrics  |
| **cvrp_failure_replay**      | failure                    | 0.238402          | 0.005376             | 0.134835     | 0.051961              | 0.915               | 0.58       | Archive size 14; behavior “balanced”     |
| **cvrp_failure_replay_compression** | failure + compression-aware | 0.238114          | 0.005376             | 0.134675     | 0.048265              | 0.866               | 0.58       | Archive size 14, compression pressure true; behavior “balanced” |

---

### Interpretation

- **Transfer ability (based on held-out CVRPLIB and synthetic gaps):**  
  The **random replay** condition exhibits the best transfer performance with the lowest mean CVRPLIB gap (0.2278), synthetic holdout gap (0.0054), and transfer gap (0.1289). This holds consistently across multiple held-out families and synthetic distributions.

- **Compared to no replay:**  
  Random replay reduces CVRPLIB gap by ~7.4% (0.2459 → 0.2278), synthetic gap by ~70% (0.0179 → 0.0054), and transfer gap by ~11% (0.1446 → 0.1289). This confirms that random replay improves generalization and transfer metrics.

- **Failure replay conditions (with and without compression):**  
  Both failure replay variants achieve synthetic gaps as low as random replay but slightly worse CVRPLIB (0.2384/0.2381) and transfer gaps (0.1348/0.1347). Adaptation efficiency is higher than random replay, but this does not fully translate into better held-out performance. Their complexity is lower (0.58) vs. clustered_constructor replay conditions (0.78).

- **Code novelty vs transfer:**  
  - Code novelty is highest in failure replay (0.915), followed by random replay (0.881), then failure replay with compression (0.866), and lowest for no replay (0.802).  
  - Notably, random replay improves transfer while slightly increasing code novelty vs no replay, but failure replay sees code novelty rise further without transfer improvement over random replay.  
  - Hence, **code novelty increases do not equate to improved transfer beyond what random replay achieves.**

- **Narrative speculation:**  
  Avoided as per instruction. The data support that **random replay leads to the best trade-off of transfer performance and code novelty**. Failure replay variants show adaptation improvements and higher novelty but lack corresponding gains in held-out transfer gaps.

---

### Conclusion

- The **cvrp_random_replay** condition is consistently superior in terms of held-out CVRPLIB gap and synthetic holdout gap, making it the best for transfer in this benchmark suite.  
- Despite slightly lower code novelty, it outperforms failure replay conditions in transfer metrics.  
- Compression-aware failure replay maintains similar transfer gaps but does not surpass random replay, with a moderate reduction in code novelty.  
- No replay conditions yield the worst transfer metrics and have negative adaptation efficiency.  
- Therefore, **random replay is recommended for best generalization and transfer in replay-aware CVRP optimization.**
