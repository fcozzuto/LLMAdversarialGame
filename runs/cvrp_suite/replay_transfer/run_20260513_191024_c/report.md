# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_191024_c
- started_at_local: 2026-05-13 19:10:24
- finished_at_local: 2026-05-13 19:13:14
- duration_hhmm: 00:03
- duration_seconds: 170.358
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.245759 | 0.012431 | 0.142058 | 0.908405 | 0.58 | 0.036692 |
| cvrp_random_replay | random | score_only | False | 0.251066 | 0.005376 | 0.14187 | 0.805416 | 0.58 | 0.039517 |
| cvrp_failure_replay | failure | score_only | False | 0.24297 | 0.005376 | 0.137373 | 0.889447 | 0.58 | 0.041784 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.253161 | 0.005376 | 0.143034 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245759`, synthetic `0.012431`, combined `0.142058`.
- Accepted-epoch count `2`, mean accepted code novelty `0.908405`, and final complexity `0.58`.
- Adaptation efficiency `0.036692` and archive sizes `{'worst_cases': 5, 'failure_cases': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245759` across 5 instances; family means: A=0.103839, B=0.269722, E=0.284069, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.012431` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.028221.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 581, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.268559}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.251066`, synthetic `0.005376`, combined `0.14187`.
- Accepted-epoch count `2`, mean accepted code novelty `0.805416`, and final complexity `0.58`.
- Adaptation efficiency `0.039517` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.251066` across 5 instances; family means: A=0.103839, B=0.256232, E=0.333973, P=0.305054.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.24297`, synthetic `0.005376`, combined `0.137373`.
- Accepted-epoch count `2`, mean accepted code novelty `0.889447`, and final complexity `0.58`.
- Adaptation efficiency `0.041784` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.24297` across 5 instances; family means: A=0.115183, B=0.256232, E=0.28215, P=0.305054.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.253161`, synthetic `0.005376`, combined `0.143034`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.253161` across 5 instances; family means: A=0.133508, B=0.256232, E=0.314779, P=0.305054.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of CVRP Replay-Aware Benchmark Results

| Condition                     | CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Code Novelty (Mean) | Replay Mode                   | Notes on Transfer & Novelty                                                                         |
|-------------------------------|-------------|----------------------|--------------|---------------------|-------------------------------|----------------------------------------------------------------------------------------------------|
| **cvrp_no_replay**            | 0.2458      | 0.0124               | 0.1421       | 0.9084              | None                          | Baseline with no replay; moderate gaps and highest code novelty. Transfer gap better than random replay but not best. |
| **cvrp_random_replay**        | 0.2511      | **0.0054**           | 0.1419       | 0.8054              | Random Replay                 | Lowest synthetic gap indicating best adaptation in synthetic holdout; transfer gap similar to no_replay; code novelty dropped but transfer not.|
| **cvrp_failure_replay**       | **0.2430**  | **0.0054**           | **0.1374**   | 0.8894              | Failure Replay                | Best performance on CVRPLIB heldout and transfer gap metrics; synthetic holdout gap matches best (random replay). Code novelty slightly reduced compared to no_replay but higher than random replay. |
| cvrp_failure_replay_compression | 0.2532    | 0.0054               | 0.1430       | 0.0                 | Failure Replay + Compression  | Worst CVRPLIB and transfer gap among failure replay variants; identical synthetic gap. Zero code novelty likely due to compression pressure limiting code changes. |

---

### Interpretation

- **Transfer Evidence**:  
  - *Failure replay* condition exhibits the lowest CVRPLIB heldout gap (0.2430) and transfer gap (0.1374), indicating it best supports transfer to unseen real-world data.  
  - *Random replay* excels at synthetic holdout (0.0054 gap) but shows slightly worse heldout gap (0.2511) than failure replay.  
  - No replay is intermediate in transfer gap (0.1421), lower than random replay despite higher code novelty.

- **Code Novelty vs Transfer**:  
  - Code novelty is highest without replay (0.9084) but transfer metrics do not improve accordingly; higher novelty without replay does not translate into better transfer.  
  - Introducing replay (both failure and random) reduces code novelty (~0.8-0.9) yet improves or maintains transfer performance.  
  - Compression-aware failure replay drastically reduces code novelty to zero and degrades transfer, showing that novelty alone is not sufficient or beneficial under compression pressure.

- **Replay Modes Impact**:  
  - *Failure replay* is the best replay method for transfer to heldout CVRPLIB instances, outperforming no replay and random replay in key deterministic metrics.  
  - *Random replay* provides best synthetic generalization but slightly worse real-world transfer, suggesting synthetic gap is not always aligned with CVRPLIB holds out generalization.  
  - Compression-aware replay harms transfer despite replaying failures, likely due to reduced adaptation efficiency (0 accepted epochs) and zero code novelty.

- **Complexity and Adaptation**:  
  - All conditions maintain the same mean complexity (0.58), so complexity differences do not explain transfer variance.  
  - Adaptation efficiency is highest for failure replay (0.0418), next random replay (0.0395), lower no replay (0.0367), and zero for compression replay. This aligns with transfer gap improvements.

---

### Key Takeaways

- Failure replay condition is the strongest performer on main transfer metrics (CVRPLIB gap and transfer gap), despite moderate decrease in code novelty compared to no replay.  
- Random replay yields the best synthetic holdout gap but no significant improvement or even slightly worse CVRPLIB transfer gap than failure replay.  
- Code novelty alone does not indicate algorithmic improvement or transfer performance; replay-based conditions show better transfer despite lower novelty.  
- Compression-aware replay prevents adaptation and transfer improvement, highlighting a tradeoff when replay is combined with compression pressure.  

**Conclusion:**
Failure replay is recommended for improved transfer in replay-aware CVRP training, as it achieves the lowest real-world CVRPLIB gap and transfer gap, showing reliable transfer gains that are not solely explained by code novelty increases.
