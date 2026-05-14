# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_190437_a
- started_at_local: 2026-05-13 19:04:37
- finished_at_local: 2026-05-13 19:07:27
- duration_hhmm: 00:03
- duration_seconds: 170.049
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.243302 | 0.005376 | 0.137557 | 0.906959 | 0.58 | 0.001157 |
| cvrp_random_replay | random | score_only | False | 0.274255 | 0.02481 | 0.163391 | 0.779781 | 0.78 | -0.031245 |
| cvrp_failure_replay | failure | score_only | False | 0.25085 | 0.005376 | 0.14175 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.261192 | 0.005376 | 0.147496 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.243302`, synthetic `0.005376`, combined `0.137557`.
- Accepted-epoch count `3`, mean accepted code novelty `0.906959`, and final complexity `0.58`.
- Adaptation efficiency `0.001157` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.243302` across 5 instances; family means: A=0.112565, B=0.255548, E=0.285988, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 593, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.29476}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.274255`, synthetic `0.02481`, combined `0.163391`.
- Accepted-epoch count `2`, mean accepted code novelty `0.779781`, and final complexity `0.78`.
- Adaptation efficiency `-0.031245` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.274255` across 5 instances; family means: A=0.165794, B=0.250139, E=0.414587, P=0.290614.
- Panel `synthetic_holdout` mean gap `0.02481` across 4 instances; family means: alternating_belt=0.049043, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.050197.
- Worst recent training cases: [{"best_known_cost": 784, "cost": 1017, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.297194}, {"best_known_cost": 458, "cost": 567, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.237991}, {"best_known_cost": 937, "cost": 1142, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.218783}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.25085`, synthetic `0.005376`, combined `0.14175`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.25085` across 5 instances; family means: A=0.143979, B=0.254873, E=0.293666, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.261192`, synthetic `0.005376`, combined `0.147496`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.261192` across 5 instances; family means: A=0.143979, B=0.254873, E=0.34357, P=0.308664.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 585, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.277293}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Replay-Aware CVRP Benchmark Results

| Condition                     | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Code Novelty | Replay Mode          | Complexity | Adaptation Efficiency | Notes                                                           |
|-------------------------------|-------------------|--------------------|--------------------|-------------------|---------------------|------------|-----------------------|-----------------------------------------------------------------|
| **cvrp_no_replay**             | **0.2433**        | **0.0054**         | **0.1376**         | 0.907             | None                | 0.58       | 0.00116               | Best performance overall on transfer and held-out benchmarks.  |
| cvrp_random_replay             | 0.2743            | 0.0248             | 0.1634             | 0.780             | Random replay       | 0.78       | -0.0312               | Higher gaps despite moderate code novelty; worse transfer.      |
| cvrp_failure_replay            | 0.2509            | 0.0054             | 0.1418             | 0.0               | Failure replay      | 0.58       | 0.0                   | Performance slightly worse than no replay; zero code novelty.   |
| cvrp_failure_replay_compression| 0.2612            | 0.0054             | 0.1475             | 0.0               | Failure + compression| 0.58       | 0.0                   | Compression pressure present; no improvements over failure replay.|

---

### Conservative Interpretation

- **Transfer Metrics (Held-out CVRPLIB & Synthetic Holdout Gaps):**  
  The **no replay** condition consistently yields the lowest mean optimality gaps on both held-out CVRPLIB (0.2433) and synthetic benchmarks (0.0054), as well as the lowest transfer gap (0.1376). This supports superior generalization and transfer capability without replay.

- **Replay Modes and Impact:**  
  - **Random replay** results in the worst transfer and held-out gaps, accompanied by the lowest adaptation efficiency, despite a relatively high code novelty (~0.78).  
  - **Failure replay** (with and without compression pressure) yields slightly better transfer gaps than random replay but still worse than no replay. Notably, failure replay conditions show zero code novelty, indicating code reuse rather than innovation.

- **Code Novelty vs. Transfer:**  
  High code novelty (no replay) correlates here with superior transfer performance. Conversely, failure replay conditions show zero code novelty but do not improve transfer gaps compared to no replay. Random replay sees a drop in code novelty relative to no replay and results in decreased transfer performance.

- **Compression Pressure:**  
  The addition of compression-aware replay (failure + compression) does not improve transfer gaps or held-out performance and maintains zero code novelty, suggesting no benefit from compression in this context.

---

### Key Takeaways

- The **no replay** condition is optimal for transfer, yielding the best held-out CVRPLIB gaps (~24.3%), synthetic gaps (~0.5%), and transfer gaps (~13.8%).  
- Introducing replay (random or failure-based) reduces transfer performance despite sometimes lower or equal code novelty, indicating replay harms or fails to enhance transfer robustness in this setting.  
- Code novelty decreases under replay conditions; however, lack of code novelty does not translate into better transfer. Thus, no evidence supports equating lexical novelty alone with improved algorithmic invention or transfer.  
- Compression-aware replay does not provide transfer benefits here and retains zero code novelty.  
- Overall, transfer improvements correlate positively with no replay, moderate complexity (~0.58), and higher code novelty.

---

### Recommendations for Benchmark Suite Usage

- Prioritize the **no replay** condition results when evaluating transfer and generalization performance.  
- Treat replay-inclusive conditions (random, failure, compression) as inferior baselines in terms of transfer despite potentially different exploratory behaviors.  
- Avoid interpreting code novelty without supporting transfer metrics as evidence of algorithmic novelty or invention.  
- Consider analyzing why replay hurts transfer—possibly preventing exploration or overfitting to replayed failures—and investigate this in future work.
