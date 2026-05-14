# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_random_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_190728_b
- started_at_local: 2026-05-13 19:07:28
- finished_at_local: 2026-05-13 19:10:23
- duration_hhmm: 00:03
- duration_seconds: 174.855
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.245937 | 0.00754 | 0.139983 | 0.838358 | 0.78 | -0.013078 |
| cvrp_random_replay | random | score_only | False | 0.247013 | 0.005376 | 0.139619 | 0.914351 | 0.58 | 0.005856 |
| cvrp_failure_replay | failure | score_only | False | 0.252953 | 0.005376 | 0.142919 | 0.932697 | 0.58 | 0.052592 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.250364 | 0.005376 | 0.14148 | 0.921805 | 0.58 | 0.049644 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245937`, synthetic `0.00754`, combined `0.139983`.
- Accepted-epoch count `2`, mean accepted code novelty `0.838358`, and final complexity `0.78`.
- Adaptation efficiency `-0.013078` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.245937` across 5 instances; family means: A=0.078534, B=0.238022, E=0.303263, P=0.371841.
- Panel `synthetic_holdout` mean gap `0.00754` across 4 instances; family means: alternating_belt=0.03016, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 582, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.270742}, {"best_known_cost": 937, "cost": 1083, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.155816}, {"best_known_cost": 784, "cost": 882, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.125}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.247013`, synthetic `0.005376`, combined `0.139619`.
- Accepted-epoch count `3`, mean accepted code novelty `0.914351`, and final complexity `0.58`.
- Adaptation efficiency `0.005856` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.247013` across 5 instances; family means: A=0.115183, B=0.241387, E=0.332054, P=0.305054.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1065, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.136606}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.252953`, synthetic `0.005376`, combined `0.142919`.
- Accepted-epoch count `2`, mean accepted code novelty `0.932697`, and final complexity `0.58`.
- Adaptation efficiency `0.052592` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.252953` across 5 instances; family means: A=0.123037, B=0.260946, E=0.314779, P=0.305054.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.250364`, synthetic `0.005376`, combined `0.14148`.
- Accepted-epoch count `2`, mean accepted code novelty `0.921805`, and final complexity `0.58`.
- Adaptation efficiency `0.049644` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.250364` across 5 instances; family means: A=0.123037, B=0.254873, E=0.301344, P=0.31769.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 585, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.277293}, {"best_known_cost": 937, "cost": 1072, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.144077}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of CVRP Replay-Aware Benchmark Results

| Condition                      | Replay Mode       | Final CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Adaptation Efficiency | Complexity | Code Novelty (mean) | Notes                                         |
|-------------------------------|-------------------|-------------------|----------------------|--------------|-----------------------|------------|---------------------|-----------------------------------------------|
| **cvrp_no_replay**             | None              | **0.2459**        | 0.00754              | 0.1400       | -0.0131               | 0.78       | 0.838               | Best held-out CVRPLIB gap. Higher complexity.  |
| **cvrp_random_replay**         | Random Replay     | 0.2470            | **0.00538**          | **0.1396**   | +0.00586              | 0.58       | **0.914**           | Best synthetic & transfer gaps. Code novelty ↑, complexity ↓. |
| **cvrp_failure_replay**        | Failure Replay    | 0.2530            | 0.00538              | 0.1429       | **+0.0526**           | 0.58       | 0.933               | Worst CVRPLIB gap but best adaptation efficiency. High novelty. |
| **cvrp_failure_replay_compression** | Failure Replay + Compression | 0.2504          | 0.00538              | 0.1415       | +0.0496               | 0.58       | 0.922               | Near failure replay performance, with compression pressure. |

---

### Interpretation

- **Transfer Performance:**
  - The best transfer metrics (held-out CVRPLIB gap, synthetic gap, and mean transfer gap) are overall achieved by the **random replay** condition.
    - Synthetic holdout gap is lowest (0.00538) here.
    - Transfer gap (~0.1396) is slightly better than no replay (0.1400).
  - No replay achieves the best held-out CVRPLIB gap (0.2459) but slightly worse synthetic gap and similar transfer gap.
  - Failure replay conditions show marginally worse held-out performance (CVRPLIB gap ~0.25) but slightly higher transfer gap, with better adaptation efficiency.

- **Code Novelty vs Transfer:**
  - Code novelty is highest in failure replay scenarios (~0.93), while random replay also has increased code novelty (~0.91) compared to no replay (~0.84).
  - Despite higher code novelty in failure replay, this does not translate to better CVRPLIB or synthetic gaps compared to random replay.
  - Random replay condition improves transfer metrics while code novelty also increases and complexity decreases relative to no replay.
  - Hence, increases in code novelty under failure replay are not accompanied by better transfer performance, contrary to random replay where code novelty gain aligns with improved transfer.

- **Replay Mode Effects:**
  - **No Replay (baseline):** Achieves best held-out CVRPLIB gap but worse synthetic gap and transfer gap.
  - **Random Replay:** Best synthetic and transfer gaps with modest CVRPLIB gap, lower complexity, and higher code novelty. Suggests replay of random past cases improves generalization and transfer more than no replay.
  - **Failure Replay:** Slightly worse CVRPLIB and transfer gaps than random replay, but higher adaptation efficiency and code novelty. Indicates focused replay of failure cases boosts adaptation but not best overall transfer.
  - **Failure Replay + Compression:** Similar trends as failure replay without compression but with compression pressure and novelty-based selection mode.

---

### Conservative Conclusions

- The **random replay** condition offers the best combination of transfer performance (lowest synthetic and transfer gaps) and code novelty with reduced algorithmic complexity relative to no replay.
- Although **no replay** attains a marginally better CVRPLIB held-out gap, its synthetic and transfer performance are inferior to random replay.
- **Failure replay** variants increase code novelty and adaptation efficiency but do not improve held-out CVRPLIB or synthetic gaps over random replay, indicating limited benefit for transfer.
- The data indicates that increased code novelty alone (especially under failure replay) is not sufficient for better transfer if not supported by deterministic gap metrics.
- Compression-aware failure replay does not improve performance over failure replay without compression.
- Lexical/code novelty changes should not be interpreted as algorithmic innovation without consistent improvements in optimality gaps and transfer metrics.

---

### Recommendation

For better transfer generalization on CVRP benchmarks, especially in real-world held-out sets and synthetic distributions:

- Prioritize **random replay** over no replay and failure replay approaches.
- Treat increases in code novelty without concurrent optimality gain cautiously.
- Replaying diverse past random cases appears more effective than focusing on failure cases alone.
