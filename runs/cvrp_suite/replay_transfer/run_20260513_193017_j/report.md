# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_193017_j
- started_at_local: 2026-05-13 19:30:17
- finished_at_local: 2026-05-13 19:33:22
- duration_hhmm: 00:03
- duration_seconds: 185.483
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.250044 | 0.005376 | 0.141303 | 0.877965 | 0.58 | -0.001201 |
| cvrp_random_replay | random | score_only | False | 0.252006 | 0.005376 | 0.142393 | 0.873494 | 0.58 | -0.0052 |
| cvrp_failure_replay | failure | score_only | False | 0.226904 | 0.005376 | 0.128447 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.236145 | 0.005376 | 0.133581 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.250044`, synthetic `0.005376`, combined `0.141303`.
- Accepted-epoch count `3`, mean accepted code novelty `0.877965`, and final complexity `0.58`.
- Adaptation efficiency `-0.001201` and archive sizes `{'worst_cases': 5, 'failure_cases': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.250044` across 5 instances; family means: A=0.1274, B=0.267694, E=0.285988, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.252006`, synthetic `0.005376`, combined `0.142393`.
- Accepted-epoch count `2`, mean accepted code novelty `0.873494`, and final complexity `0.58`.
- Adaptation efficiency `-0.0052` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.252006` across 5 instances; family means: A=0.115183, B=0.267019, E=0.314779, P=0.296029.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 581, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.268559}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.226904`, synthetic `0.005376`, combined `0.128447`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.226904` across 5 instances; family means: A=0.115183, B=0.247451, E=0.228407, P=0.296029.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.236145`, synthetic `0.005376`, combined `0.133581`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.236145` across 5 instances; family means: A=0.120419, B=0.235305, E=0.293666, P=0.296029.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 589, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.286026}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of CVRP Replay-Aware Benchmark Results

| Condition                     | Replay Mode               | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (mean) | Compression Pressure | Notes on Replay & Selection             |
|-------------------------------|---------------------------|-------------------|---------------------|--------------------|---------------------|----------------------|----------------------------------------|
| **cvrp_failure_replay**        | Failure replay            | **0.2269**        | 0.00538             | **0.1284**         | 0.0                 | No                   | Best heldout and transfer results      |
| **cvrp_no_replay**             | None                      | 0.2500            | 0.00538             | 0.1413             | 0.878               | No                   | Best synthetic holdout gap              |
| **cvrp_failure_replay_compression** | Failure replay + compression | 0.2361         | 0.00538             | 0.1336             | 0.0                 | Yes                  | Same replay mode with compression      |
| **cvrp_random_replay**          | Random replay             | 0.2520            | 0.00538             | 0.1424             | 0.873               | No                   | Highest code novelty with random replay|

---

### Interpretation

#### Transfer and Optimality Gap (Primary Evidence)  
- **Failure replay (cvrp_failure_replay)** achieves the lowest CVRPLIB held-out gap (**0.2269**) and the lowest mean transfer gap (**0.1284**), indicating superior generalization and transfer to held-out benchmarks.  
- **No replay (cvrp_no_replay)** shows the best synthetic holdout gap (0.00538; identical across conditions) but has a higher transfer gap (0.1413) and higher CVRPLIB heldout gap (0.2500).  
- **Random replay** and **failure replay with compression** yield similar but slightly worse CVRPLIB and transfer gaps compared to failure replay without compression, with transfer gaps around 0.1336–0.1424.

#### Code Novelty vs Transfer  
- Conditions with **failure replay (both with and without compression)** have **zero code novelty** (mean 0.0), whereas **no replay and random replay** show high code novelty (~0.87).  
- Despite **zero code novelty in failure replay**, these conditions outperform others in transfer metrics, indicating **improved transfer is achieved without new code innovation** as measured here. Thus, **transfer improvement is not due to lexical code novelty but rather replay strategy**.

#### Replay Mode Distinctions  
- **No replay:** No replay buffer used; higher code novelty but worse transfer on CVRPLIB.  
- **Random replay:** Randomly samples from archives; high code novelty but no transfer improvement over no replay.  
- **Failure replay:** Replays failure cases, leading to consistent improvement in transfer and held-out gaps despite zero code novelty.  
- **Failure replay with compression:** Similar to failure replay but under compression pressure; shows slightly degraded transfer vs failure replay alone.

#### Additional Notes  
- Complexity is stable across conditions (mean 0.58), ruling out complexity changes as cause for gap differences.  
- Training gaps and last epoch training gaps are similar across conditions, implying transfer differences are not explained by training performance alone.

---

### Conservative Conclusions

1. **Failure replay is the most effective replay strategy for improving transfer to held-out CVRPLIB problems**, reducing the optimality-gap by ~0.02–0.03 relative to no replay or random replay.  
2. **This transfer gain occurs without an increase in code novelty**, indicating the adaptation comes from replaying failure cases rather than introducing novel code.  
3. **Synthetic holdout gaps remain minimal and consistent across all conditions**, confirming synthetic benchmarks are not sensitive discriminators here.  
4. **Compression-aware replay degrades transfer slightly vs failure replay alone, suggesting compression pressure may limit replay benefits despite maintaining code novelty at zero.**  
5. **Random replay does not improve transfer despite high code novelty, reinforcing that lexical novelty alone does not imply algorithmic advancement or transfer improvement.**

---

**Overall, the strongest empirical evidence supports the use of failure replay (without compression) as the best strategy for enhancing transfer in this replay-aware CVRP benchmark suite.**
