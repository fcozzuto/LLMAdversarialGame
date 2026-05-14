# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay_compression`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_191315_d
- started_at_local: 2026-05-13 19:13:15
- finished_at_local: 2026-05-13 19:16:00
- duration_hhmm: 00:03
- duration_seconds: 165.382
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.245656 | 0.005376 | 0.138865 | 0.833333 | 0.78 | 0.009437 |
| cvrp_random_replay | random | score_only | False | 0.245792 | 0.005376 | 0.13894 | 0.910822 | 0.58 | -0.003227 |
| cvrp_failure_replay | failure | score_only | False | 0.228833 | 0.05147 | 0.150005 | 0.0 | 0.78 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.244758 | 0.005376 | 0.138366 | 0.920563 | 0.58 | 0.048923 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245656`, synthetic `0.005376`, combined `0.138865`.
- Accepted-epoch count `2`, mean accepted code novelty `0.833333`, and final complexity `0.78`.
- Adaptation efficiency `0.009437` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.245656` across 5 instances; family means: A=0.123037, B=0.283879, E=0.326296, P=0.211191.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245792`, synthetic `0.005376`, combined `0.13894`.
- Accepted-epoch count `2`, mean accepted code novelty `0.910822`, and final complexity `0.58`.
- Adaptation efficiency `-0.003227` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245792` across 5 instances; family means: A=0.112565, B=0.26567, E=0.276392, P=0.308664.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.228833`, synthetic `0.05147`, combined `0.150005`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.228833` across 5 instances; family means: A=0.206806, B=0.215099, E=0.211132, P=0.296029.
- Panel `synthetic_holdout` mean gap `0.05147` across 4 instances; family means: alternating_belt=0.049043, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.156836.
- Worst recent training cases: [{"best_known_cost": 937, "cost": 1271, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.356457}, {"best_known_cost": 784, "cost": 1021, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.302296}, {"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.244758`, synthetic `0.005376`, combined `0.138366`.
- Accepted-epoch count `2`, mean accepted code novelty `0.920563`, and final complexity `0.58`.
- Adaptation efficiency `0.048923` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.244758` across 5 instances; family means: A=0.115183, B=0.266344, E=0.274472, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of CVRP Benchmark Suite Results

| Condition                    | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Replay Mode        | Code Novelty (Mean) | Complexity | Notes on Transfer & Optimality              |
|------------------------------|-------------------|--------------------|--------------------|--------------------|---------------------|------------|---------------------------------------------|
| **cvrp_failure_replay**       | **0.2288**        | 0.0515             | **0.1500**         | failure            | 0.0                 | 0.78       | Best held-out CVRPLIB gap and transfer gap. Higher synthetic gap. No code novelty. Moderate complexity. |
| **cvrp_no_replay**            | 0.2457            | **0.0054**         | 0.1389             | none               | 0.83                | 0.78       | Best synthetic holdout gap. Slightly worse transfer gap than failure replay. High code novelty.     |
| **cvrp_random_replay**        | 0.2458            | 0.0054             | 0.1389             | random             | 0.91                | 0.58       | Similar performance to no replay. Highest code novelty. Lower complexity.                         |
| **cvrp_failure_replay_compression** | 0.2448      | 0.0054             | 0.1384             | failure + compression | 0.92                | 0.58       | Best transfer gap across conditions, except failure replay alone. Lower CVRPLIB gap than no replay but higher than failure replay. High code novelty with compression effect. |

---

### Conservative Interpretation

- **Transfer Evidence (CVRPLIB gap and synthetic holdout gap):**
  - The **failure replay** condition achieves the best transfer to held-out CVRPLIB instances (lowest mean gap 0.2288) and also the highest transfer gap (0.1500), indicative of improved real-world transfer.
  - The **no replay** condition yields the best synthetic holdout gap (0.0054), but slightly worse held-out CVRPLIB and transfer gaps, suggesting synthetic scenarios remain easier than real-world transfer.
  - **Random replay** mirrors no replay transfer metrics but with higher code novelty and lower complexity.
  - **Failure replay with compression** slightly degrades CVRPLIB gap (0.2448 vs 0.2288 failure replay alone) but improves mean transfer gap compared to no replay or random replay, consistent with more robust transfer behavior.

- **Code Novelty vs Transfer:**
  - **Failure replay** conditions show **zero code novelty** but better CVRPLIB transfer, indicating strong transfer is not driven by novel code generation but possibly by replaying failure cases.
  - **No replay**, **random replay**, and **failure replay compression** have higher code novelty (0.83-0.92), yet their CVRPLIB transfer is not better than failure replay alone.
  - This suggests code novelty is **not correlated** with improved transfer; transfer benefits stem more from replay mechanisms focused on failures.

- **Replay Mode Effects:**
  - **Failure replay (without compression)** achieves best held-out CVRPLIB gap, indicating replaying failure cases effectively improves real-world transfer.
  - **No replay** yields best synthetic but worse CVRPLIB gaps.
  - **Random replay** does not improve over no replay.
  - **Compression-aware failure replay** improves transfer probe gap but slightly worsens CVRPLIB gap relative to failure replay alone, a tradeoff of complexity reduction.

- **Complexity and Adaptation:**
  - Conditions with failure replay have higher complexity (0.78) versus random replay or compression-aware failure replay (0.58).
  - Adaptation efficiency is highest for compression-aware failure replay (0.049), zero or negative for others, indicating compression may help adaptation without sacrificing novelty.

---

### Key Takeaways

- **Failure replay condition shows best real-world transfer (lowest held-out CVRPLIB gap and highest transfer gap) despite zero code novelty.**
- **Synthetic holdout gaps are uniformly low across replay conditions, making CVRPLIB gap a stronger transfer indicator.**
- **Code novelty correlates inversely with transfer performance; best transfer occurs at low novelty.**
- **Compression-aware failure replay trades slight increase in CVRPLIB gap for improved adaptation efficiency and transfer probe gap, with higher code novelty.**
- Random replay provides no transfer improvement over no replay despite higher code novelty and lower complexity.

---

### Recommendations

- Prioritize **failure replay** over no replay or random replay for transfer-focused optimization in CVRP benchmarks.
- Recognize that **code novelty alone is not a reliable marker of improved transfer**; emphasize transfer metrics.
- Consider compression-aware failure replay as a tradeoff option, balancing complexity, adaptation efficiency, and moderate transfer performance.
- Further investigate why failure replay leads to better transfer despite zero code novelty — likely due to replay focus on failure case learning rather than exploration.

---

This interpretation is consistent with the main evidence (held-out CVRPLIB and synthetic gaps) and avoids speculative narrative beyond quantitative metrics and replay mode distinctions.
