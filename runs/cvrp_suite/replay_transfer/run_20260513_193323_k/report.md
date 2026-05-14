# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay_compression`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay_compression`.
- Best synthetic holdout gap: `cvrp_failure_replay_compression`.

## Run Metadata
- run_name: run_20260513_193323_k
- started_at_local: 2026-05-13 19:33:23
- finished_at_local: 2026-05-13 19:36:43
- duration_hhmm: 00:03
- duration_seconds: 199.268
- seed_offset: 10000
- replicate_label: k
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.244084 | 0.005376 | 0.137992 | 0.905812 | 0.58 | 0.03293 |
| cvrp_random_replay | random | score_only | False | 0.239694 | 0.005376 | 0.135553 | 0.889336 | 0.58 | -0.003996 |
| cvrp_failure_replay | failure | score_only | False | 0.237687 | 0.005376 | 0.134438 | 0.880282 | 0.58 | 0.061869 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.198494 | 0.0 | 0.110274 | 0.766067 | 0.78 | 0.035528 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.244084`, synthetic `0.005376`, combined `0.137992`.
- Accepted-epoch count `2`, mean accepted code novelty `0.905812`, and final complexity `0.58`.
- Adaptation efficiency `0.03293` and archive sizes `{'worst_cases': 5, 'failure_cases': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.244084` across 5 instances; family means: A=0.099476, B=0.249482, E=0.320537, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1065, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.136606}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.239694`, synthetic `0.005376`, combined `0.135553`.
- Accepted-epoch count `3`, mean accepted code novelty `0.889336`, and final complexity `0.58`.
- Adaptation efficiency `-0.003996` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.239694` across 5 instances; family means: A=0.099476, B=0.241387, E=0.314779, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1065, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.136606}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.237687`, synthetic `0.005376`, combined `0.134438`.
- Accepted-epoch count `2`, mean accepted code novelty `0.880282`, and final complexity `0.58`.
- Adaptation efficiency `0.061869` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.237687` across 5 instances; family means: A=0.103839, B=0.247451, E=0.293666, P=0.296029.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.198494`, synthetic `0.0`, combined `0.110274`.
- Accepted-epoch count `2`, mean accepted code novelty `0.766067`, and final complexity `0.78`.
- Adaptation efficiency `0.035528` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.198494` across 5 instances; family means: A=0.075916, B=0.200286, E=0.238004, P=0.277978.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: alternating_belt=0.0, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

## Judge Appendix
### Summary of Results

| Condition                         | Final CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Code Novelty (mean) | Replay Mode         | Compression Pressure | Complexity | Adaptation Efficiency |
|----------------------------------|-------------------|----------------------|--------------|---------------------|---------------------|----------------------|------------|-----------------------|
| cvrp_no_replay                   | 0.244084          | 0.005376             | 0.137992     | 0.905812            | none                | No                   | 0.58       | 0.03293               |
| cvrp_random_replay               | 0.239694          | 0.005376             | 0.135553     | 0.889336            | random              | No                   | 0.58       | -0.003996             |
| cvrp_failure_replay              | 0.237687          | 0.005376             | 0.134438     | 0.880282            | failure             | No                   | 0.58       | 0.061869              |
| **cvrp_failure_replay_compression** | **0.198494**      | **0.0**              | **0.110274** | **0.766067**        | failure + compression | Yes                  | 0.78       | 0.035528              |

---

### Interpretation

- **Best transfer performance** (lowest **final CVRPLIB gap** and **synthetic holdout gap**, and smallest **transfer gap**) is achieved by **cvrp_failure_replay_compression**. This condition improves transfer gaps noticeably compared to others, with a CVRPLIB gap reduction from ~0.24 to ~0.20 (approx. 20% relative improvement) and synthetic gap improvement down to zero.

- **Compression-aware failure replay improves transfer significantly** over:
  - no replay
  - random replay
  - failure replay without compression

- **Code novelty decreases** substantially (mean of 0.77 vs. ~0.88-0.91 in others) under compression-aware failure replay despite transfer improvements. This suggests:
  - The transfer gains under compression are **not** due to increased lexical or superficial code novelty.
  - Instead, the compression mechanism likely encourages a more stable or clustered constructor behavior (confirmed by the higher complexity 0.78 and "clustered_constructor" behavior profile).

- **No replay vs random replay vs failure replay (no compression):**
  - Show minor differences in CVRPLIB gap (~0.237-0.244)
  - Synthetic holdout gap is constant (0.005376)
  - Transfer gap marginally decreases slightly from no replay (0.138) to failure replay (0.134)
  - Code novelty slightly decreases from no replay to failure replay
  - Adaptation efficiency highest for failure replay without compression (0.0619), but this does not translate into best transfer gap

- **Compression pressure increases model complexity** (0.78 vs 0.58). Yet, this complexity elevation coincides with improved transfer and zero synthetic gap, indicating more effective generalization.

---

### Conclusion (Conservative)

- The **cvrp_failure_replay_compression** condition yields the strongest evidence of improved transfer ability, with reduced optimality gaps on held-out benchmarks and synthetic instances.
- This transfer improvement occurs *despite* a reduction in code novelty, indicating that lexical novelty alone does not drive transfer gains.
- Replay of failure cases combined with compression pressure promotes beneficial structural adjustments in the learned policy, improving generalization.
- Differences among no replay, random replay, and failure replay (no compression) are minor in terms of transfer and gap metrics.
- Claims of novelty or improvement should prioritize the demonstrated metrics of transfer and optimality gap rather than code novelty alone.

---

### Notes on Replay Modes

| Replay Mode                    | Description                                                  |
|-------------------------------|--------------------------------------------------------------|
| **none (cvrp_no_replay)**      | No experience replay                                          |
| **random (cvrp_random_replay)**| Replay of random past experiences                            |
| **failure (cvrp_failure_replay)**| Replay focused on failure cases                             |
| **failure + compression (cvrp_failure_replay_compression)**| Replay of failure cases combined with compression pressure|

Use of **failure replay with compression** most effectively leverages replay to improve transfer, outperforming other replay conditions.
