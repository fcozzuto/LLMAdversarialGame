# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_192724_i
- started_at_local: 2026-05-13 19:27:24
- finished_at_local: 2026-05-13 19:30:16
- duration_hhmm: 00:03
- duration_seconds: 171.787
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.234747 | 0.005376 | 0.132804 | 0.679487 | 0.78 | 0.036792 |
| cvrp_random_replay | random | score_only | False | 0.240934 | 0.005376 | 0.136242 | 0.911469 | 0.58 | 0.049481 |
| cvrp_failure_replay | failure | score_only | False | 0.238632 | 0.005376 | 0.134963 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.235906 | 0.005376 | 0.133448 | 0.899749 | 0.58 | 0.050162 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.234747`, synthetic `0.005376`, combined `0.132804`.
- Accepted-epoch count `2`, mean accepted code novelty `0.679487`, and final complexity `0.78`.
- Adaptation efficiency `0.036792` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.234747` across 5 instances; family means: A=0.151832, B=0.219154, E=0.28215, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.240934`, synthetic `0.005376`, combined `0.136242`.
- Accepted-epoch count `2`, mean accepted code novelty `0.911469`, and final complexity `0.58`.
- Adaptation efficiency `0.049481` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.240934` across 5 instances; family means: A=0.115183, B=0.229914, E=0.328215, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.238632`, synthetic `0.005376`, combined `0.134963`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.238632` across 5 instances; family means: A=0.143979, B=0.229914, E=0.287908, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.235906`, synthetic `0.005376`, combined `0.133448`.
- Accepted-epoch count `2`, mean accepted code novelty `0.899749`, and final complexity `0.58`.
- Adaptation efficiency `0.050162` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.235906` across 5 instances; family means: A=0.13438, B=0.225192, E=0.287908, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 589, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.286026}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
```markdown
# CVRP Replay-Aware Benchmark Suite Analysis

## Summary of Main Metrics (Lower gaps are better):

| Condition                     | CVRPLIB Gap | Synthetic Gap | Transfer Gap | Code Novelty | Complexity | Replay Mode         |
|-------------------------------|-------------|---------------|--------------|--------------|------------|---------------------|
| cvrp_no_replay                | 0.2347      | 0.0054        | **0.1328**   | 0.6795       | 0.78       | none                |
| cvrp_random_replay            | 0.2409      | 0.0054        | 0.1362       | **0.9115**   | 0.58       | random              |
| cvrp_failure_replay           | 0.2386      | 0.0054        | 0.1350       | 0.0          | 0.58       | failure             |
| cvrp_failure_replay_compression | 0.2359    | 0.0054        | 0.1334       | 0.8997       | 0.58       | failure + compression|

---

## Optimality Gaps and Transfer

- The **no replay** condition (cvrp_no_replay) achieves the best held-out CVRPLIB gap (0.2347) and best synthetic holdout gap (0.0054).
- It also yields the lowest mean transfer gap (0.1328), outperforming all replay conditions.
- The replay conditions (random, failure, failure+compression) show slightly higher CVRPLIB gaps (~0.236 to 0.241) and transfer gaps (~0.133 to 0.136).
- Differences in synthetic gaps are negligible across conditions (all 0.0054).

## Code Novelty vs. Transfer

- Random replay and failure+compression replay increase **code novelty** substantially (~0.9 mean novelty), compared to no replay (0.68) and failure replay (0.0).
- Despite higher novelty, these replay modes do not improve transfer metrics and actually perform slightly worse than no replay.
- Failure replay condition with zero code novelty performs poorly on transfer compared to no replay.
- Thus, increased code novelty from replay modes does **not translate to better algorithmic transfer** or optimality gap improvements.

## Replay Mode Effects

- **No replay** (none) yields the best overall transfer and held-out gap metrics at the cost of higher complexity (0.78).
- **Random replay** trades off slight degradation in transfer/held-out gaps for significantly lower complexity (0.58) and higher novelty.
- **Failure replay** (no novelty) and **failure replay with compression** (high novelty) show no meaningful benefit in transfer metrics compared to no replay, despite replaying failure cases.
- Compression pressure in failure replay does not produce transfer gains.

## Complexity and Adaptation Efficiency

- No replay shows highest complexity (0.78), with replay modes consistently at 0.58 complexity.
- Adaptation efficiency is highest with failure+compression replay (0.050), followed by random replay (0.049), but this does not yield optimality gains.
- No replay has lowest adaptation efficiency (~0.037) but best transfer/held-out gap metrics.

---

# Conclusions

- **Best condition for generalization and transfer is no replay (cvrp_no_replay)**, judged by held-out CVRPLIB gaps and synthetic gaps.
- Replay modes increase code novelty but do not improve—and may slightly degrade—transfer performance.
- Compression-aware replay does not deliver transfer advantage vs. simple no replay, despite efforts to preserve novelty.
- Algorithmic improvements should prioritize reducing optimality gaps on held-out CVRPLIB benchmarks over maximizing code novelty.
- Replay conditions alter behavioral profiles and reduce complexity but without transfer gains.
- Claims of algorithmic invention based on code novelty alone are not substantiated by transfer or gap improvements here.

---

# Recommendation

For applications prioritizing transfer and solution quality, **prefer no replay training conditions**. Use replay modes only if complexity reduction or controlled novelty is specifically desired, acknowledging potential slight loss in optimality and transfer performance.
```
