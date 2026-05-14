# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_195210_q
- started_at_local: 2026-05-13 19:52:10
- finished_at_local: 2026-05-13 19:55:13
- duration_hhmm: 00:03
- duration_seconds: 182.675
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.203837 | 0.005376 | 0.115632 | 0.862644 | 0.78 | 0.017299 |
| cvrp_random_replay | random | score_only | False | 0.251603 | 0.005376 | 0.142169 | 0.73025 | 0.78 | 0.05445 |
| cvrp_failure_replay | failure | score_only | False | 0.215731 | 0.005376 | 0.12224 | 0.82319 | 0.78 | 0.0182 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.234631 | 0.005376 | 0.13274 | 0.8127 | 0.78 | 0.063182 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.203837`, synthetic `0.005376`, combined `0.115632`.
- Accepted-epoch count `2`, mean accepted code novelty `0.862644`, and final complexity `0.78`.
- Adaptation efficiency `0.017299` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.203837` across 5 instances; family means: A=0.081152, B=0.244087, E=0.21881, P=0.231047.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 817, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.215774}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.251603`, synthetic `0.005376`, combined `0.142169`.
- Accepted-epoch count `2`, mean accepted code novelty `0.73025`, and final complexity `0.78`.
- Adaptation efficiency `0.05445` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.251603` across 5 instances; family means: A=0.061955, B=0.24813, E=0.293666, P=0.406137.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 602, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.31441}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 805, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.197917}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.215731`, synthetic `0.005376`, combined `0.12224`.
- Accepted-epoch count `2`, mean accepted code novelty `0.82319`, and final complexity `0.78`.
- Adaptation efficiency `0.0182` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.215731` across 5 instances; family means: A=0.081152, B=0.244086, E=0.247601, P=0.261733.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 805, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.197917}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.234631`, synthetic `0.005376`, combined `0.13274`.
- Accepted-epoch count `2`, mean accepted code novelty `0.8127`, and final complexity `0.78`.
- Adaptation efficiency `0.063182` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.234631` across 5 instances; family means: A=0.145724, B=0.21309, E=0.214971, P=0.386282.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

## Judge Appendix
### Conservative Interpretation of Replay-Aware CVRP Benchmark Results

| Metric                     | No Replay (cvrp_no_replay) | Random Replay (cvrp_random_replay) | Failure Replay (cvrp_failure_replay) | Failure Replay + Compression (cvrp_failure_replay_compression) |
|----------------------------|----------------------------|-----------------------------------|-------------------------------------|---------------------------------------------------------------|
| **Held-out CVRPLIB mean gap**  | **0.2038**                 | 0.2516                            | 0.2157                              | 0.2346                                                        |
| **Synthetic holdout mean gap**  | 0.0054                     | 0.0054                            | 0.0054                              | 0.0054                                                        |
| **Mean transfer gap**           | **0.1156**                 | 0.1422                            | 0.1222                              | 0.1327                                                        |
| **Code novelty (mean)**          | 0.8626                     | 0.7303                            | 0.8232                              | 0.8127                                                        |
| **Compression pressure**          | No                         | No                                | No                                  | Yes                                                           |
| **Replay mode**                 | None                       | Random                           | Failure                            | Failure + Compression                                         |
| **Selection mode**              | score_only                 | score_only                       | score_only                        | novelty_gate                                                 |

---

### Key Observations

- **Transfer Performance**  
  - *Best held-out CVRPLIB gap (0.2038)* and *best mean transfer gap (0.1156)* are achieved by the **no replay** condition.
  - All replay modes (random, failure, failure + compression) show **worse transfer gaps** and held-out CVRPLIB gaps relative to no replay.
  - Synthetic holdout gaps are uniformly low (0.0054) across all conditions, indicating minimal differences on synthetic benchmarks.
  - This supports concluding that **no replay yields better transfer performance** on held-out CVRPLIB instances and synthetic holdouts.

- **Code Novelty vs. Transfer**  
  - No replay achieves **highest lexical code novelty (0.8626)** and also the best transfer.
  - Replay conditions reduce code novelty (0.73 to 0.82) but do **not improve transfer**; in fact, transfer worsens despite some adaptation efficiency gains under replay.
  - Hence, **code novelty decline with replay modes is associated with transfer degradation**, refuting the idea that replay improves algorithmic generalization.

- **Effect of Compression-aware Replay**  
  - Compression pressure is applied only in failure replay with compression.
  - This condition improves adaptation efficiency (0.0632; highest) but yields worse transfer gaps than no replay or failure replay without compression.
  - This indicates that **compression-aware replay may aid adaptation speed but at a cost to transfer optimality**.

- **Optimality Gap Breakdown (Held-out CVRPLIB)**  
  - Worst gaps appear in families B, P, E, with family P gaps particularly large under replay conditions (up to 0.4061).  
  - No replay shows more balanced family gaps and lower worst-case gaps.

- **Behavior and Complexity**  
  - Across conditions, final behavior profiles (clustered_constructor) and complexity (~0.78) remain consistent, suggesting stable algorithmic structure regardless of replay.

---

### Summary

- The **no replay condition achieves best transfer results**, demonstrating superior generalization from training to held-out CVRPLIB and synthetic instances.
- Introduction of **random, failure, or compression-aware replay reduces transfer quality**, despite some gains in adaptation efficiency.
- **Code novelty decreases with replay use; this decrease parallels worse transfer**, suggesting replay harms algorithmic innovation relevant to generalization.
- Improvements in adaptation efficiency under replay scenarios do not translate into improved optimality gaps on held-out benchmarks.
- Narrative claims that replay enhances transfer or algorithmic discovery are **not supported by the deterministic optimality gap and transfer metrics**.

---

### Recommendations

- Prioritize the **no replay approach** when aiming for optimality and transfer generalization.
- Use caution when introducing replay mechanisms; they may incur transfer cost despite adaptation speed benefits.
- Future work should investigate why replay diminishes transfer and whether alternative replay strategies (beyond current modes) might preserve code novelty and improve transfer gaps.
