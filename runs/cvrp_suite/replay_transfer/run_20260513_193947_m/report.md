# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_193947_m
- started_at_local: 2026-05-13 19:39:47
- finished_at_local: 2026-05-13 19:42:50
- duration_hhmm: 00:03
- duration_seconds: 182.974
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.218068 | 0.005376 | 0.123538 | 0.767949 | 0.78 | 0.021668 |
| cvrp_random_replay | random | score_only | False | 0.24523 | 0.005376 | 0.138628 | 0.890782 | 0.58 | 0.0061 |
| cvrp_failure_replay | failure | score_only | False | 0.215701 | 0.01914 | 0.128341 | 0.826087 | 0.78 | 0.057228 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.243813 | 0.005376 | 0.137841 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.218068`, synthetic `0.005376`, combined `0.123538`.
- Accepted-epoch count `2`, mean accepted code novelty `0.767949`, and final complexity `0.78`.
- Adaptation efficiency `0.021668` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.218068` across 5 instances; family means: A=0.095986, B=0.237997, E=0.247601, P=0.270758.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.24523`, synthetic `0.005376`, combined `0.138628`.
- Accepted-epoch count `2`, mean accepted code novelty `0.890782`, and final complexity `0.58`.
- Adaptation efficiency `0.0061` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.24523` across 5 instances; family means: A=0.121291, B=0.254873, E=0.293666, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.215701`, synthetic `0.01914`, combined `0.128341`.
- Accepted-epoch count `2`, mean accepted code novelty `0.826087`, and final complexity `0.78`.
- Adaptation efficiency `0.057228` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.215701` across 5 instances; family means: A=0.094241, B=0.187483, E=0.259117, P=0.350181.
- Panel `synthetic_holdout` mean gap `0.01914` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.055054.
- Worst recent training cases: [{"best_known_cost": 784, "cost": 1087, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.38648}, {"best_known_cost": 458, "cost": 600, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.310044}, {"best_known_cost": 672, "cost": 829, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.233631}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.243813`, synthetic `0.005376`, combined `0.137841`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.243813` across 5 instances; family means: A=0.11082, B=0.269043, E=0.268714, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of CVRP Benchmark Conditions

| Condition                    | Replay Mode               | Mean Held-out CVRPLIB Gap | Mean Synthetic Holdout Gap | Mean Transfer Gap | Code Novelty (mean) | Adaptation Efficiency | Replay Compression | Final Complexity | Notes on Replay Type            |
|------------------------------|--------------------------|---------------------------|----------------------------|-------------------|---------------------|-----------------------|--------------------|------------------|-------------------------------|
| **cvrp_no_replay**            | none                     | **0.2181**                | **0.0054**                 | **0.1235**        | 0.768               | 0.0217                | No                 | 0.78             | No replay                     |
| **cvrp_random_replay**        | random                   | 0.2452                    | 0.0054                     | 0.1386            | 0.891               | 0.0061                | No                 | 0.58             | Random replay                 |
| **cvrp_failure_replay**       | failure                  | **0.2157 (best held-out**) | 0.0191                     | 0.1283            | 0.826               | **0.0572 (best)**     | No                 | 0.78             | Replay of failure cases       |
| **cvrp_failure_replay_compression** | failure + compression-aware | 0.2438                    | 0.0054                     | 0.1378            | **0.0 (lowest)**     | 0.0                   | Yes                | 0.58             | Replay + compression + novelty |

---

### Conservative Interpretation

- **Held-out CVRPLIB Gap** (key metric for transfer):
  - Best is **cvrp_failure_replay** (0.2157), slightly better than no replay (0.2181).
  - Random replay and compression conditions perform worse (>0.24 gap).
  
- **Synthetic Holdout Gap** (transfer on synthetic data):
  - Lowest gaps (0.0054) for **no replay**, **random replay**, and **compression replay**.
  - Failure replay without compression shows noticeably worse synthetic gap (0.0191), indicating possibly less synthetic domain generality.

- **Mean Transfer Gap** (averaged transfer domain gap):
  - Lowest for **no replay** (0.1235), followed by failure replay (0.1283).
  - Random and compression-aware replay have higher transfer gaps (~0.138).
  
- **Code Novelty**:
  - Highest on random replay (0.891), followed by failure replay (0.826) and no replay (0.768).
  - Compression replay has zero novelty despite similar replay mode.

- **Adaptation Efficiency**:
  - Highest for failure replay (0.0572), lower for no replay (0.0217), and random replay (0.0061).
  - Compression-aware failure replay shows zero adaptation efficiency.

- **Replay mode and effects**:
  - Failure replay improves held-out CVRPLIB gap and adaptation efficiency compared to no replay.
  - Random replay leads to higher code novelty but worse optimality gaps.
  - Compression-aware replay reduces code novelty to zero and yields poor adaptation despite replaying failures.
  
- **Final Behavior Complexity**:
  - Higher complexity (0.78) for no replay and failure replay suggests more complex behavior profiles correlate with better gaps.
  - Lower complexity (0.58) for random and compression replay conditions aligned with worse generalization.

---

### Important Points

- **Best transfer performance (held-out CVRPLIB gap and synthetic gap) is with failure replay (no compression) and no replay conditions.** No replay has the best synthetic and transfer gaps but slightly worse held-out CVRPLIB gap.

- **Code novelty decreases with compression-aware replay and fails to improve transfer despite replaying failure cases.**

- Random replay increases code novelty but results in worse gaps and lower adaptation efficiency.

- Replay mode substantially affects transfer ability: failure replay aids held-out generalization by improving optimality gap and adaptation efficiency, even though synthetic domain gaps are slightly worse.

- No replay condition shows a strong tradeoff with moderate code novelty and best synthetic transfer gaps.

---

### Final Conservative Conclusions

- **Failure replay improves held-out CVRPLIB optimality gap and adaptation efficiency over no replay and random replay, indicating beneficial specialized replay of failure cases.**

- **No replay achieves the best synthetic holdout and lowest mean transfer gap, illustrating strong transfer despite lack of replay.**

- **Random replay increases code novelty but at the cost of worse transfer performance and adaptation efficiency.**

- **Compression-aware replay sharply decreases code novelty and adaptation efficiency, impairing transfer despite replaying failure cases.**

- **Overall, replaying failure cases without compression represents the best practical tradeoff between transfer optimality gap and adaptation.**

- **Lexical code novelty does not strictly correlate with transfer improvements, especially seen in compression failure replay condition where novelty drops but transfer is poor (no benefit in this case).**

---

### Recommendations for Benchmark Suite Use

- Prioritize **failure replay without compression** for benchmarks aiming to optimize transfer on held-out CVRPLIB instances.

- Use **no replay** condition as a baseline for synthetic domain transfer quality.

- Treat **random replay** and **compression-aware replay** conditions cautiously, as increased novelty or replay compression do not guarantee transfer or optimality benefits.

- Emphasize deterministic metrics (held-out gaps, transfer gaps, adaptation efficiency) over code novelty for algorithmic assessment.
