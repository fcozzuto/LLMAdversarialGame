# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_192447_h
- started_at_local: 2026-05-13 19:24:47
- finished_at_local: 2026-05-13 19:27:23
- duration_hhmm: 00:03
- duration_seconds: 156.231
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.218845 | 0.005376 | 0.12397 | 0.742409 | 0.78 | 0.035508 |
| cvrp_random_replay | random | score_only | False | 0.241545 | 0.005376 | 0.136581 | 0.727318 | 0.58 | 0.002027 |
| cvrp_failure_replay | failure | score_only | False | 0.24828 | 0.005376 | 0.140323 | 0.762695 | 0.58 | 0.05248 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.22084 | 0.026996 | 0.134687 | 0.780645 | 0.78 | 0.009335 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.218845`, synthetic `0.005376`, combined `0.12397`.
- Accepted-epoch count `3`, mean accepted code novelty `0.742409`, and final complexity `0.78`.
- Adaptation efficiency `0.035508` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_cvrplib` mean gap `0.218845` across 5 instances; family means: A=0.091623, B=0.243412, E=0.264875, P=0.250903.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 937, "cost": 1280, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.366062}, {"best_known_cost": 458, "cost": 618, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.349345}, {"best_known_cost": 672, "cost": 845, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.25744}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.241545`, synthetic `0.005376`, combined `0.136581`.
- Accepted-epoch count `2`, mean accepted code novelty `0.727318`, and final complexity `0.58`.
- Adaptation efficiency `0.002027` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.241545` across 5 instances; family means: A=0.103839, B=0.251508, E=0.299424, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1065, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.136606}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.24828`, synthetic `0.005376`, combined `0.140323`.
- Accepted-epoch count `2`, mean accepted code novelty `0.762695`, and final complexity `0.58`.
- Adaptation efficiency `0.05248` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.24828` across 5 instances; family means: A=0.13438, B=0.252174, E=0.299424, P=0.303249.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1072, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.144077}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.22084`, synthetic `0.026996`, combined `0.134687`.
- Accepted-epoch count `2`, mean accepted code novelty `0.780645`, and final complexity `0.78`.
- Adaptation efficiency `0.009335` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.22084` across 5 instances; family means: A=0.147469, B=0.272493, E=0.245681, P=0.166065.
- Panel `synthetic_holdout` mean gap `0.026996` across 4 instances; family means: alternating_belt=0.064516, clustered_demand=0.043468, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 458, "cost": 588, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.283843}, {"best_known_cost": 672, "cost": 805, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.197917}]

## Judge Appendix
### Summary of CVRP Benchmark Results

| Condition                    | CVRPLIB Gap | Synthetic Gap | Transfer Gap | Code Novelty (mean) | Replay Mode               | Notes on Complexity & Archive      |
|------------------------------|-------------|---------------|--------------|---------------------|--------------------------|-----------------------------------|
| **cvrp_no_replay**            | **0.2188**  | **0.0054**    | **0.1240**   | 0.7424              | none                     | Complexity 0.78, Archive size 14  |
| cvrp_random_replay            | 0.2415      | 0.0054        | 0.1366       | 0.7273              | random                   | Complexity 0.58, Archive size 14  |
| cvrp_failure_replay           | 0.2483      | 0.0054        | 0.1403       | 0.7627              | failure                  | Complexity 0.58, Archive size 14  |
| cvrp_failure_replay_compression| 0.2208     | 0.0270        | 0.1347       | 0.7806              | failure + compression    | Complexity 0.78, Archive size 14  |

---

### Key Interpretations

- **Best performance in transfer and held-out gaps occurs under the no replay condition (`cvrp_no_replay`):**
  - Exhibits lowest mean gaps on held-out CVRPLIB (0.2188) and synthetic data (0.0054).
  - Also has the best mean transfer gap (0.1240).
  
- **Replay usage (random or failure) generally increases both CVRPLIB and transfer gaps despite slight variations:**
  - Random replay and failure replay conditions show worse performance on main transfer metrics (+0.02–0.03 gap increase in CVRPLIB and ~0.01–0.02 in transfer gap).
  - Compression-aware failure replay improves synthetic gap slightly versus failure replay without compression (0.027 vs. 0.0054 is actually worse in synthetic gap), but still lags behind no replay.

- **Code novelty is slightly decreased in random replay (0.727) but higher for failure replay variants (0.763–0.781):**
  - Despite higher code novelty under failure replay conditions, transfer metrics degrade compared to no replay.
  - This suggests **code novelty improvements do not translate into better transfer** in failure or random replay cases.
  
- **Complexity differences:**
  - No replay and failure replay with compression maintain higher complexity (~0.78) while other replay modes are less complex (~0.58).
  - Complexity does not align consistently with gap improvements.

- **Family-wise worst cases:**
  - Larger gaps on families B, E, and P across all conditions.
  - No replay condition has slightly lower worst-case optimality gaps.

---

### Conservative Conclusions

1. **No replay yields the best transfer and heldout optimality gaps despite slightly lower code novelty than failure-replay variants.** This prioritizes the transfer metrics over mere code novelty or complexity.

2. **Random and failure replay approaches lead to degraded transfer performance, even if code novelty is marginally higher, indicating replay strategies here do not improve cross-distribution generalization.**

3. **Compression-aware failure replay improves complexity and code novelty but does not outperform no replay in transfer gaps nor synthetic gaps, suggesting compression pressure alone is insufficient to improve transfer.**

4. **Lexical/code novelty gains under failure or random replay are not indicative of algorithmic invention, as deterministic optimality gap metrics do not support a transfer advantage.**

5. **No evidence supports contention that replay (especially failure or random) improves transfer; on the contrary, it degrades transfer metrics compared to no replay.**

---

### Summary Table: Rank by Transfer Performance

| Rank | Condition             | Mean Transfer Gap | Mean CVRPLIB Gap | Mean Synthetic Gap | Code Novelty (mean) | Replay Type           |
|-------|----------------------|-------------------|------------------|--------------------|---------------------|----------------------|
| 1     | cvrp_no_replay       | **0.1240**        | **0.2188**       | **0.0054**         | 0.7424              | none                 |
| 2     | cvrp_failure_replay_compression | 0.1347          | 0.2208           | 0.0270             | 0.7806              | failure + compression |
| 3     | cvrp_random_replay   | 0.1366            | 0.2415           | 0.0054             | 0.7273              | random               |
| 4     | cvrp_failure_replay  | 0.1403            | 0.2483           | 0.0054             | 0.7627              | failure              |

---

**Overall, the no replay condition should be prioritized for CVRP transfer purposes. Replay strategies increase code novelty but do not yield better practical transfer performance according to held-out CVRPLIB and synthetic gaps.**
