# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_random_replay`.
- Best CVRPLIB holdout gap: `cvrp_random_replay`.
- Best synthetic holdout gap: `cvrp_no_replay`.

## Run Metadata
- run_name: run_20260513_195810_s
- started_at_local: 2026-05-13 19:58:10
- finished_at_local: 2026-05-13 20:01:12
- duration_hhmm: 00:03
- duration_seconds: 181.988
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.247184 | 0.005376 | 0.139714 | 0.925859 | 0.58 | -0.003142 |
| cvrp_random_replay | random | score_only | False | 0.222852 | 0.00754 | 0.127158 | 0.795003 | 0.78 | 0.012852 |
| cvrp_failure_replay | failure | score_only | False | 0.246867 | 0.005376 | 0.139538 | 0.917671 | 0.58 | -0.004132 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.260052 | 0.005376 | 0.146863 | 0.762695 | 0.58 | 0.036652 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.247184`, synthetic `0.005376`, combined `0.139714`.
- Accepted-epoch count `3`, mean accepted code novelty `0.925859`, and final complexity `0.58`.
- Adaptation efficiency `-0.003142` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.247184` across 5 instances; family means: A=0.138743, B=0.254873, E=0.285988, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 587, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.281659}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.222852`, synthetic `0.00754`, combined `0.127158`.
- Accepted-epoch count `2`, mean accepted code novelty `0.795003`, and final complexity `0.78`.
- Adaptation efficiency `0.012852` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.222852` across 5 instances; family means: A=0.120419, B=0.228589, E=0.28215, P=0.254513.
- Panel `synthetic_holdout` mean gap `0.00754` across 4 instances; family means: alternating_belt=0.03016, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 458, "cost": 574, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.253275}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.246867`, synthetic `0.005376`, combined `0.139538`.
- Accepted-epoch count `2`, mean accepted code novelty `0.917671`, and final complexity `0.58`.
- Adaptation efficiency `-0.004132` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.246867` across 5 instances; family means: A=0.103839, B=0.267694, E=0.293666, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.260052`, synthetic `0.005376`, combined `0.146863`.
- Accepted-epoch count `2`, mean accepted code novelty `0.762695`, and final complexity `0.58`.
- Adaptation efficiency `0.036652` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.260052` across 5 instances; family means: A=0.103839, B=0.267694, E=0.339731, P=0.3213.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 602, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.31441}, {"best_known_cost": 937, "cost": 1073, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.145144}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Replay-aware CVRP Benchmark Results

| Condition                   | Replay Mode          | Held-out CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Adaptation Efficiency | Code Novelty (Mean) | Complexity | Notes on Trends                         |
|-----------------------------|---------------------|----------------------|----------------------|--------------|-----------------------|---------------------|------------|---------------------------------------|
| **cvrp_no_replay**           | None                | 0.2472               | **0.00538**          | 0.1397       | -0.0031               | **0.926**           | 0.58       | Highest code novelty, moderate transfer gaps |
| **cvrp_random_replay**       | Random Replay       | **0.2229 (best)**    | 0.00754              | **0.1272 (best)** | 0.0129                | 0.795               | 0.78       | Best transfer and heldout gaps, lower code novelty vs no replay, higher complexity |
| **cvrp_failure_replay**      | Failure Replay      | 0.2469               | 0.00538              | 0.1395       | -0.0041               | 0.918               | 0.58       | Transfer gaps similar to no replay, code novelty similar to no replay |
| **cvrp_failure_replay_compression** | Failure Replay + Compression | 0.2601               | 0.00538              | 0.1469       | 0.0367                | 0.763               | 0.58       | Worst CVRPLIB gap and transfer, lowest code novelty, positive adaptation efficiency |

---

### Interpretation:  

- **Main transfer evidence (Held-out CVRPLIB and Synthetic gaps)**:  
  - **Random replay condition (cvrp_random_replay) shows the best transfer performance**, with lowest mean CVRPLIB gap (0.2229) and lowest mean transfer gap (0.1272). It also shows higher synthetic holdout gap (0.00754) than no replay but still small.  
  - **No replay (cvrp_no_replay) achieves the best synthetic holdout gap (0.00538)** but has worse heldout CVRPLIB and transfer gaps than random replay.  
  - Failure replay conditions (cvrp_failure_replay, cvrp_failure_replay_compression) do not improve transfer gaps compared to no replay and generally are worse on CVRPLIB gap, especially with compression-aware mode.  

- **Code novelty vs. transfer trade-off**:  
  - The no replay condition has the highest code novelty (~0.926) but lower transfer performance.  
  - Random replay reduces code novelty (~0.795) but improves transfer metrics substantially. This suggests a trade-off where replay degrades novelty but improves solution quality on held-out and transferred problems.  
  - Failure replay conditions have relatively high code novelty (~0.918, 0.763) but do not improve transfer compared to no replay.  

- **Complexity**:  
  - Random replay yields higher complexity (0.78) vs no replay and failure replay (both ~0.58). This may relate to more complex behavior profiles enabling better transfer.  
  - Compression-aware failure replay lowers code novelty and increases adaptation efficiency positively but degrades transfer and optimality gaps.  

- **Adaptation efficiency**:  
  - Only random replay and compression-aware failure replay show positive adaptation efficiency, indicating efficiency in learning or adapting new solutions.  
  - Despite positive efficiency, compression-aware failure replay has worse gaps, highlighting efficiency alone is insufficient for transfer quality.  

---

### Conservative Conclusions:

- **Random replay delivers the best transfer performance on held-out CVRPLIB and synthetic problems.** This is the strongest evidence for beneficial replay use in the benchmark.  
- **No replay attains the best synthetic holdout gap and highest code novelty, but worse overall transfer and heldout CVRPLIB gaps than random replay.** Novelty decreases under random replay, indicating replay may reduce code diversity but improve solution generalization.  
- **Failure replay modes do not improve transfer gaps compared to no replay and may degrade performance especially with compression pressure despite some gains in adaptation efficiency or complexity.**  
- **Increased lexical or code novelty does not correlate with improved transfer or held-out optimality gaps. Thus, code novelty is not a proxy for algorithmic invention in this context.**  
- **Random replay has the most favorable balance of transfer gaps and adaptation efficiency, but at the cost of increased solution complexity and decreased code novelty.**  

---

### Final Recommendation:

Prioritize **random replay** for transfer quality improvements in replay-aware CVRP benchmarks. Avoid failure replay and overemphasis on code novelty or compression-aware replay alone, as these do not translate to better transfer or heldout gaps.
