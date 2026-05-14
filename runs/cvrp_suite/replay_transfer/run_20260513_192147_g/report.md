# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_192147_g
- started_at_local: 2026-05-13 19:21:47
- finished_at_local: 2026-05-13 19:24:46
- duration_hhmm: 00:03
- duration_seconds: 179.394
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.22093 | 0.05147 | 0.145614 | 0.0 | 0.78 | 0.0 |
| cvrp_random_replay | random | score_only | False | 0.241884 | 0.005376 | 0.136769 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay | failure | score_only | False | 0.232866 | 0.007671 | 0.132779 | 0.874439 | 0.78 | 0.005256 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.245806 | 0.005376 | 0.138948 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.22093`, synthetic `0.05147`, combined `0.145614`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.22093` across 5 instances; family means: A=0.206806, B=0.194209, E=0.21881, P=0.290614.
- Panel `synthetic_holdout` mean gap `0.05147` across 4 instances; family means: alternating_belt=0.049043, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.156836.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 544, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.187773}, {"best_known_cost": 937, "cost": 1083, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.155816}, {"best_known_cost": 784, "cost": 882, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.125}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.241884`, synthetic `0.005376`, combined `0.136769`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.241884` across 5 instances; family means: A=0.143979, B=0.254873, E=0.238004, P=0.31769.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1062, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.133404}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.232866`, synthetic `0.007671`, combined `0.132779`.
- Accepted-epoch count `2`, mean accepted code novelty `0.874439`, and final complexity `0.78`.
- Adaptation efficiency `0.005256` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.232866` across 5 instances; family means: A=0.122164, B=0.19963, E=0.247601, P=0.395307.
- Panel `synthetic_holdout` mean gap `0.007671` across 4 instances; family means: alternating_belt=0.030685, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 613, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.338428}, {"best_known_cost": 937, "cost": 1219, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.300961}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.245806`, synthetic `0.005376`, combined `0.138948`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245806` across 5 instances; family means: A=0.143979, B=0.248809, E=0.285988, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 858, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.094388}]

## Judge Appendix
### Summary of Replay-Aware CVRP Benchmark Suite Results

| Condition                      | Replay Mode            | Heldout CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap   | Code Novelty Mean | Mean Complexity | Comments on Transfer & Novelty                             |
|-------------------------------|-----------------------|---------------------|----------------------|----------------|-------------------|-----------------|------------------------------------------------------------|
| **cvrp_no_replay**             | None                  | **0.22093**         | 0.05147              | 0.14561        | 0.0               | 0.78            | Best transfer gap among conditions with zero code novelty. |
| **cvrp_random_replay**         | Random replay         | 0.24188             | **0.00538**          | 0.13677        | 0.0               | 0.58            | Best synthetic holdout gap but higher heldout CVRPLIB gap; no code novelty. |
| **cvrp_failure_replay**        | Failure replay        | 0.23287             | 0.00767              | **0.13278**    | **0.8744**        | 0.78            | Best transfer gap and highest code novelty; however, heldout gaps higher than no replay. |
| **cvrp_failure_replay_compression** | Failure replay + compression | 0.24581             | 0.00538              | 0.13895        | 0.0               | 0.58            | Compression lowers complexity; transfer gap worse than failure replay without compression and no code novelty. |

---

### Interpretation:

1. **Transfer Evidence (Heldout CVRPLIB & Synthetic Gaps)**
   - **Best heldout CVRPLIB gap**: *cvrp_no_replay* (0.22093), indicating strongest direct transfer to heldout CVRPLIB instances.
   - **Best synthetic holdout gap**: *cvrp_random_replay* and *cvrp_failure_replay_compression* (0.0054), suggesting best adaptation to synthetic problem variations.
   - **Best combined transfer gap**: *cvrp_failure_replay* (0.13278), slightly outperforming *cvrp_no_replay* (0.14561) and *cvrp_random_replay* (0.13677).

2. **Replay Mode Effects:**
   - *No replay* yields the strongest CVRPLIB heldout performance and balanced transfer gap.
   - *Random replay* significantly improves synthetic transfer (gap 0.0054) but worsens CVRPLIB heldout gap (0.2419).
   - *Failure replay* improves transfer gap slightly over no replay but results in poorer heldout CVRPLIB (0.2329 vs 0.2209).
   - Adding *compression* to failure replay reduces complexity but degrades transfer performance and eliminates code novelty.

3. **Code Novelty vs Transfer:**
   - *Failure replay* results in high code novelty (0.8744 mean) but transfer improvements are modest and heldout CVRPLIB gap is not better than no replay.
   - Other conditions have zero code novelty; thus, lexical or algorithmic novelty claims are unsupported except for failure replay.
   - However, improved transfer metrics under failure replay occur despite increased code novelty, contrasting with *no replay* and *random replay*.

4. **Complexity:**
   - Replay modes introducing compression lowered complexity (0.58), but this did not translate into improved transfer or heldout CVRPLIB gaps.
   - Balanced profiles had higher complexity (0.78).

---

### Conservative Conclusion:

- The **no replay** condition provides the best **heldout CVRPLIB optimality gap**, thus strongest conservative evidence for transfer to standard benchmark instances.
- The **random replay** condition improves synthetic holdout performance dramatically (lowest synthetic gap), suggesting better adaptation to synthetic distributions but at the cost of worsening heldout CVRPLIB gaps.
- The **failure replay** condition achieves the best combined **transfer gap** slightly and shows high code novelty, indicating some algorithmic innovation; however, this does not yet translate into robust improvements on the established CVRPLIB heldout benchmark.
- Compression-aware replay lowers complexity but does not improve transfer performance nor code novelty.
- Code novelty and algorithmic improvements in failure replay do not clearly correspond to improved heldout CVRPLIB gaps; thus, lexical novelty does not equate to algorithmic invention in aggregate transfer.

---

### Final prioritized ranking:

| Metric                 | Best Condition          | Notes                                     |
|------------------------|------------------------|-------------------------------------------|
| Heldout CVRPLIB gap    | **cvrp_no_replay**     | Strongest transfer on realistic benchmarks. |
| Synthetic holdout gap  | **cvrp_random_replay** | Best synthetic adaptation but weaker heldout. |
| Transfer gap (combined) | **cvrp_failure_replay** | Slightly better transfer gap; highest novelty but heldout gap worse than no replay.|

---

### Recommendation for benchmark suite:

- Prioritize **no replay** and **failure replay** modes when targeting overall transfer, with caution interpreting failure replay novelty due to unclear heldout benefit.
- Random replay benefits synthetic domains but may harm real-world benchmark transfer.
- Compression-aware replay not justified based on current transfer metrics.
- Do not claim algorithmic novelty without consistent improvement in heldout CVRPLIB gaps despite high code novelty under failure replay.
