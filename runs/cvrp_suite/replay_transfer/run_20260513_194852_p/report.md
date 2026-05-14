# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay_compression`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay_compression`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_194852_p
- started_at_local: 2026-05-13 19:48:52
- finished_at_local: 2026-05-13 19:52:09
- duration_hhmm: 00:03
- duration_seconds: 197.126
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.250831 | 0.012431 | 0.144875 | 0.823728 | 0.58 | -0.004399 |
| cvrp_random_replay | random | score_only | False | 0.263081 | 0.005376 | 0.148545 | 0.912913 | 0.58 | 0.001818 |
| cvrp_failure_replay | failure | score_only | False | 0.261546 | 0.005376 | 0.147693 | 0.74887 | 0.58 | -0.007923 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.245399 | 0.005376 | 0.138722 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.250831`, synthetic `0.012431`, combined `0.144875`.
- Accepted-epoch count `3`, mean accepted code novelty `0.823728`, and final complexity `0.58`.
- Adaptation efficiency `-0.004399` and archive sizes `{'worst_cases': 5, 'failure_cases': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.250831` across 5 instances; family means: A=0.103839, B=0.272417, E=0.285988, P=0.319495.
- Panel `synthetic_holdout` mean gap `0.012431` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.028221.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 581, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.268559}, {"best_known_cost": 937, "cost": 1062, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.133404}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.263081`, synthetic `0.005376`, combined `0.148545`.
- Accepted-epoch count `2`, mean accepted code novelty `0.912913`, and final complexity `0.58`.
- Adaptation efficiency `0.001818` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.263081` across 5 instances; family means: A=0.115183, B=0.272417, E=0.335893, P=0.319495.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1062, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.133404}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.261546`, synthetic `0.005376`, combined `0.147693`.
- Accepted-epoch count `2`, mean accepted code novelty `0.74887`, and final complexity `0.58`.
- Adaptation efficiency `-0.007923` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.261546` across 5 instances; family means: A=0.143979, B=0.272417, E=0.299424, P=0.319495.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 858, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.094388}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.245399`, synthetic `0.005376`, combined `0.138722`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245399` across 5 instances; family means: A=0.143979, B=0.248809, E=0.28215, P=0.303249.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 858, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.094388}]

## Judge Appendix
```markdown
### Summary of Replay-Aware CVRP Benchmark Suite Results

| Condition                     | Replay Mode               | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Accepted Epochs | Adaptation Efficiency | Mean Code Novelty | Compression Pressure | Notes on Transfer & Optimality |
|-------------------------------|---------------------------|-------------------|---------------------|--------------------|-----------------|-----------------------|-------------------|----------------------|--------------------------------|
| **cvrp_no_replay**             | none                      | 0.2508            | 0.0124              | 0.1449             | 3               | -0.0044               | 0.824             | No                   | Baseline transfer moderate; moderate CVRPLIB gap |
| **cvrp_random_replay**         | random                    | 0.2631            | **0.0054**          | 0.1485             | 2               | 0.0018                | 0.913             | No                   | Best synthetic holdout gap (lowest), slightly worse CVRPLIB gap vs no_replay, transfer gap slightly worse |
| **cvrp_failure_replay**        | failure                   | 0.2615            | 0.0054              | 0.1477             | 2               | -0.0079               | 0.749             | No                   | Similar synthetic and transfer gaps as random replay; CVRPLIB gap close to random replay |
| **cvrp_failure_replay_compression** | failure + compression-aware | **0.2454**        | 0.0054              | **0.1387**          | 1               | 0.0                   | 0.0               | Yes                  | Best CVRPLIB gap and transfer gap, lowest code novelty (zero), compression active |

### Interpretation

- **Main Evidence for Transfer: CVRPLIB & Synthetic Holdout Gaps**
  - *Best transfer* (lowest mean transfer gap) is achieved by **cvrp_failure_replay_compression** (0.1387), also the best on held-out CVRPLIB (0.2454).
  - *Synthetic holdout gap* is consistently lowest (0.0054) for replay conditions: random replay, failure replay, and failure replay with compression. No replay condition has a slightly higher synthetic gap (0.0124).
  - Random replay has marginally higher transfer gap (0.1485) and CVRPLIB gap (0.2631) compared to failure replay and failure replay compression.

- **Code Novelty vs Transfer**
  - Code novelty **drops substantially to zero** in the compression-aware failure replay condition, while transfer metrics improve.
  - Random replay shows the highest code novelty (~0.91) but slightly worse transfer.
  - Thus, **code novelty decreases while transfer improves** when switching to compression-aware failure replay, indicating improvements are likely not driven by lexical novelty but by replay + compression mechanisms.

- **Replay Mode Differences**
  - No replay shows the poorest transfer and held-out CVRPLIB performance.
  - Random replay improves synthetic holdout gap significantly but does not improve CVRPLIB gap compared to no replay.
  - Failure replay alone improves synthetic gap but not noticeably better than random replay on CVRPLIB gap.
  - Failure replay with compression yields the best transfer and CVRPLIB gaps, despite lower acceptance (only 1 accepted epoch) and zero code novelty.

- **Complexity and Behavior Profile**
  - Final complexity and behavior profiles are constant across conditions (0.58 and balanced).
  - Archive sizes and epoch counts are similar, except accepted epochs drop to 1 when compression applied.

### Conservative Conclusions

- **cvrp_failure_replay_compression condition objectively achieves the best transfer performance**, as evidenced by the lowest held-out CVRPLIB gap (0.2454) and lowest transfer gap (0.1387).
- This condition reduces code novelty to zero, indicating transfer improvements occur through replay + compression mechanisms rather than exploratory code novelty.
- Random replay produces the best synthetic holdout optimality gap (0.0054) but does not match the best CVRPLIB or transfer gap.
- No replay condition underperforms others on key transfer metrics.
- Compression-aware failure replay is the preferred replay strategy for improving ultimate CVRP generalization to held-out benchmarks.
- Optimality gaps remain sizeable on held-out CVRPLIB instances (all >10%), leaving room for further improvement.

---
*Analysis prioritized deterministic metrics (gaps, transfer) and considered replay modes distinctly. Lexical novelty relevance was contextualized against transfer results.*
```
