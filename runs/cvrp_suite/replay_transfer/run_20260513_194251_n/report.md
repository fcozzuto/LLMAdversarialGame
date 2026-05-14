# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_194251_n
- started_at_local: 2026-05-13 19:42:51
- finished_at_local: 2026-05-13 19:45:45
- duration_hhmm: 00:03
- duration_seconds: 173.659
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.212727 | 0.05147 | 0.141057 | 0.0 | 0.78 | 0.0 |
| cvrp_random_replay | random | score_only | False | 0.246889 | 0.005376 | 0.13955 | 0.890836 | 0.58 | 0.002225 |
| cvrp_failure_replay | failure | score_only | False | 0.219278 | 0.005376 | 0.12421 | 0.814103 | 0.78 | 0.035504 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.22301 | 0.061086 | 0.151044 | 0.903226 | 0.78 | -0.015134 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.212727`, synthetic `0.05147`, combined `0.141057`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.212727` across 5 instances; family means: A=0.165794, B=0.194209, E=0.21881, P=0.290614.
- Panel `synthetic_holdout` mean gap `0.05147` across 4 instances; family means: alternating_belt=0.049043, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.156836.
- Worst recent training cases: [{"best_known_cost": 784, "cost": 1088, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.387755}, {"best_known_cost": 937, "cost": 1245, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.328709}, {"best_known_cost": 458, "cost": 585, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.277293}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.246889`, synthetic `0.005376`, combined `0.13955`.
- Accepted-epoch count `2`, mean accepted code novelty `0.890836`, and final complexity `0.58`.
- Adaptation efficiency `0.002225` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.246889` across 5 instances; family means: A=0.143979, B=0.248809, E=0.285988, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 591, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.290393}, {"best_known_cost": 937, "cost": 1063, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.134472}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.219278`, synthetic `0.005376`, combined `0.12421`.
- Accepted-epoch count `2`, mean accepted code novelty `0.814103`, and final complexity `0.78`.
- Adaptation efficiency `0.035504` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.219278` across 5 instances; family means: A=0.086387, B=0.211766, E=0.209213, P=0.377256.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 608, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.327511}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.22301`, synthetic `0.061086`, combined `0.151044`.
- Accepted-epoch count `2`, mean accepted code novelty `0.903226`, and final complexity `0.78`.
- Adaptation efficiency `-0.015134` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.22301` across 5 instances; family means: A=0.206806, B=0.322363, E=0.120921, P=0.142599.
- Panel `synthetic_holdout` mean gap `0.061086` across 4 instances; family means: alternating_belt=0.10097, clustered_demand=0.043468, corridor_split=0.099906, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 458, "cost": 588, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.283843}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

## Judge Appendix
### Summary of CVRP Benchmark Results by Replay Condition

| Condition                    | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (Mean) | Compression Pressure | Replay Mode                       | Notes on Transfer & Optimality                             |
|------------------------------|------------------:|--------------------:|-------------------:|--------------------:|---------------------:|----------------------------------|-----------------------------------------------------------|
| **cvrp_no_replay**            | **0.213**         | 0.051               | 0.141              | 0.0                 | No                   | None                             | Best CVRPLIB gap (heldout), moderate transfer gap; no code novelty. |
| **cvrp_random_replay**        | 0.247             | **0.0054**          | 0.140              | 0.89                | No                   | Random                           | Best synthetic gap, transfer gap close to no replay; high code novelty but worse heldout optimality. |
| **cvrp_failure_replay**       | 0.219             | 0.0054              | **0.124**          | 0.81                | No                   | Failure                         | Best transfer gap; synthetic gap equal to random replay; intermediate heldout gap; substantial code novelty. |
| **cvrp_failure_replay_compression** | 0.223             | 0.061               | 0.151              | 0.90                | Yes                  | Failure + Compression-aware      | Highest synthetic and transfer gaps, close heldout gap to failure replay; high code novelty but negative adaptation efficiency. |

---

### Interpretation (Conservative, Metric-Focused)

- **Heldout CVRPLIB gap (main optimality indicator):**  
  - **No replay condition ("cvrp_no_replay") achieved the best optimality on heldout CVRPLIB instances (0.213 gap).**  
  - Replay-based methods show **worse heldout gaps**, with random replay the worst (0.247), failure replay slightly better (0.219), and compression replay close (0.223).  
  - This suggests replay mechanisms do **not improve heldout CVRPLIB performance**; in fact, they degrade it mildly.

- **Synthetic holdout gap (generalization to synthetic scenarios):**  
  - **Replay conditions with failure and random replay yielded very low synthetic gaps (~0.0054), far superior to no replay (0.051) and compression replay (0.061).**  
  - This indicates replay improves synthetic transfer optimality, especially failure and random replay modes.

- **Mean transfer gap (average generalization):**  
  - Best transfer gap is from **failure replay (0.124), slightly better than random replay (0.140) and no replay (0.141).**  
  - Compression replay shows the worst transfer gap (0.151).  
  - Failure replay thus offers **the best transfer generalization** overall.

- **Code novelty:**  
  - No replay condition has **zero code novelty**.  
  - Replay conditions show high novelty (0.81–0.90), with compression replay highest (0.90).  
  - Despite this code novelty increase, the **heldout CVRPLIB optimality did not improve (or even worsened).**  
  - This implies increased code novelty does **not correspond to better optimality on heldout CVRPLIB**.

- **Compression pressure:**  
  - Only the failure replay compression-aware condition has compression pressure; resulted in **lower adaptation efficiency (-0.015) and worse transfer gap,** despite high code novelty.  
  - This suggests compression pressure may harm transfer and adaptation in this setting.

- **Adaptation Efficiency:**  
  - Highest in failure replay (0.0355), positive but low in random replay (0.0022), zero in no replay, and negative in failure replay compression.
  - Failure replay may enable better adaptation but does not lead to better heldout optimality.

---

### Conclusions

- The **no replay baseline achieves the best CVRPLIB heldout optimality** and moderate transfer, despite zero code novelty and no replay.  
- Both **random and failure replay improve synthetic holdout performance significantly**, with synthetic gap dropping from ~0.05 (no replay) to ~0.005.  
- **Failure replay leads to the best overall transfer gap**, outperforming no replay and random replay in transfer generalization, while maintaining moderate CVRPLIB gaps.  
- **Code novelty increases substantially under replay conditions but does not translate into better heldout CVRPLIB optimality,** indicating novelty is not equivalent to algorithmic improvement in this context.  
- Compression-aware failure replay introduces negative adaptation efficiency and worsens transfer despite very high novelty, suggesting compression pressure is detrimental here.  
- Replay mode matters: **failure replay offers the best transfer improvement, albeit with some degradation in heldout optimality** compared to no replay.  
- Narrative speculation about code novelty or replay being beneficial should be tempered—**metrics show replay improves synthetic transfer but reduces heldout optimality.**

---

### Recommendation

- Prioritize no replay for best heldout CVRPLIB gap if final optimality is primary.  
- Use failure replay when transfer generalization is critical and slight optimality degradation is acceptable.  
- Avoid compression-aware replay due to negative adaptation effects.  
- Treat code novelty increases cautiously; they do not guarantee algorithmic or performance improvements.
