# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_no_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_failure_replay`.

## Run Metadata
- run_name: run_20260513_193644_l
- started_at_local: 2026-05-13 19:36:44
- finished_at_local: 2026-05-13 19:39:46
- duration_hhmm: 00:03
- duration_seconds: 182.572
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.225234 | 0.01914 | 0.133637 | 0.783611 | 0.78 | 0.010307 |
| cvrp_random_replay | random | score_only | False | 0.227843 | 0.01914 | 0.135086 | 0.875321 | 0.78 | 0.019345 |
| cvrp_failure_replay | failure | score_only | False | 0.245738 | 0.005376 | 0.13891 | 0.863841 | 0.78 | 0.015991 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.256804 | 0.005376 | 0.145058 | 0.887047 | 0.58 | 0.012532 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.225234`, synthetic `0.01914`, combined `0.133637`.
- Accepted-epoch count `2`, mean accepted code novelty `0.783611`, and final complexity `0.78`.
- Adaptation efficiency `0.010307` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.225234` across 5 instances; family means: A=0.091623, B=0.244087, E=0.293666, P=0.252708.
- Panel `synthetic_holdout` mean gap `0.01914` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.055054.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 562, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.227074}, {"best_known_cost": 672, "cost": 808, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.202381}, {"best_known_cost": 784, "cost": 863, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.100765}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.227843`, synthetic `0.01914`, combined `0.135086`.
- Accepted-epoch count `2`, mean accepted code novelty `0.875321`, and final complexity `0.78`.
- Adaptation efficiency `0.019345` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.227843` across 5 instances; family means: A=0.109075, B=0.244761, E=0.287908, P=0.252708.
- Panel `synthetic_holdout` mean gap `0.01914` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.055054.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 609, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.329694}, {"best_known_cost": 937, "cost": 1187, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.266809}, {"best_known_cost": 672, "cost": 808, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.202381}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245738`, synthetic `0.005376`, combined `0.13891`.
- Accepted-epoch count `2`, mean accepted code novelty `0.863841`, and final complexity `0.78`.
- Adaptation efficiency `0.015991` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.245738` across 5 instances; family means: A=0.086387, B=0.27715, E=0.295585, P=0.292419.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 817, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.215774}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.256804`, synthetic `0.005376`, combined `0.145058`.
- Accepted-epoch count `4`, mean accepted code novelty `0.887047`, and final complexity `0.58`.
- Adaptation efficiency `0.012532` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.256804` across 5 instances; family means: A=0.115183, B=0.259605, E=0.330134, P=0.319495.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Results by Condition

| Condition                    | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Complexity | Replay Mode    | Selection Mode | Code Novelty (mean) | Archive Size | Compression Pressure | Adaptation Efficiency |
|------------------------------|-------------------|--------------------|--------------------|-----------------|----------------|----------------|---------------------|--------------|----------------------|-----------------------|
| **cvrp_no_replay**            | **0.225234**      | 0.01914            | **0.133637**       | 0.78            | none           | score_only     | 0.7836              | 14           | no                   | 0.01031               |
| cvrp_random_replay            | 0.227843          | 0.01914            | 0.135086           | 0.78            | random         | score_only     | 0.8753              | 14           | no                   | 0.01935               |
| cvrp_failure_replay           | 0.245738          | **0.005376**       | 0.13891            | 0.78            | failure        | score_only     | 0.8638              | 14           | no                   | 0.01599               |
| cvrp_failure_replay_compression| 0.256804         | **0.005376**       | 0.145058           | **0.58**        | failure        | novelty_gate   | 0.8870              | 14           | yes                  | 0.01253               |

---

### Interpretation

**Main Transfer Evidence:**
- The best final CVRPLIB held-out gap and transfer gap are achieved by the **no replay** condition (`0.225234` heldout gap; `0.133637` transfer gap), indicating superior generalization to CVRPLIB instances and transfer performance.
- Synthetic holdout gap is lowest in both **failure replay** conditions (`0.005376`), indicating they provide better synthetic domain generalization but not better CVRPLIB transfer.
  
**Replay Modes:**
- **No replay** yields the best transfer performance despite having the lowest code novelty (`0.7836`).
- **Random replay** increases code novelty (`0.8753`) and adaptation efficiency (`0.01935`), but with slightly worse CVRPLIB transfer metrics compared to no replay.
- **Failure replay** (both score_only and novelty_gate selection) shows increased code novelty (~`0.86-0.88`), better synthetic generalization, but degrades CVRPLIB transfer performance.
- **Compression-aware failure replay** reduces complexity significantly (0.58 vs 0.78) with no improvement in transfer or heldout gaps, indicating compression reduces code complexity but not transfer performance.

**Algorithmic Novelty vs Lexical Novelty:**
- Code novelty is higher with replay approaches but does **not** coincide with improved transfer to CVRPLIB, suggesting lexical novelty increases without corresponding transfer gains.
- The best transfer performance (no replay) occurs with **lower code novelty**, supporting the conservative interpretation that no replay yields more robust transfer despite less exploratory diversity.

**Summary:**
- **No replay condition provides best heldout CVRPLIB gap and overall transfer gap, representing strongest transfer performance.** 
- **Failure replay strategies improve synthetic domain generalization but at the cost of worse CVRPLIB transfer gaps.**
- **Increased replay modes lead to higher code novelty but do not translate into improved transfer performance.**
- **Compression-aware replay reduces code complexity but further degrades CVRPLIB transfer.**

---

### Recommendations

- Prioritize **no replay** setting for benchmarks focused on CVRPLIB transfer and heldout generalization.
- Consider failure replay only if synthetic holdout performance is critical, acknowledging it harms CVRPLIB transfer.
- Lexical/code novelty is not evidence of algorithmic improvement unless coupled with better transfer metrics; here it is not.
- Compression affects complexity but not transfer; use cautiously when aiming for generalization in CVRP benchmarks.
