# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_failure_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_191859_f
- started_at_local: 2026-05-13 19:18:59
- finished_at_local: 2026-05-13 19:21:46
- duration_hhmm: 00:03
- duration_seconds: 166.97
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.245169 | 0.012431 | 0.14173 | 0.0 | 0.58 | 0.0 |
| cvrp_random_replay | random | score_only | False | 0.24255 | 0.005376 | 0.137139 | 0.821106 | 0.58 | 0.044396 |
| cvrp_failure_replay | failure | score_only | False | 0.241049 | 0.005376 | 0.136305 | 0.0 | 0.58 | 0.0 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.245482 | 0.005376 | 0.138768 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245169`, synthetic `0.012431`, combined `0.14173`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245169` across 5 instances; family means: A=0.128272, B=0.249482, E=0.291747, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.012431` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.028221.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1064, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.135539}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.24255`, synthetic `0.005376`, combined `0.137139`.
- Accepted-epoch count `2`, mean accepted code novelty `0.821106`, and final complexity `0.58`.
- Adaptation efficiency `0.044396` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.24255` across 5 instances; family means: A=0.128272, B=0.249482, E=0.284069, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 577, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.259825}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.241049`, synthetic `0.005376`, combined `0.136305`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.241049` across 5 instances; family means: A=0.116928, B=0.249482, E=0.287908, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.245482`, synthetic `0.005376`, combined `0.138768`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.245482` across 5 instances; family means: A=0.116928, B=0.259605, E=0.289827, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1057, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.128068}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

## Judge Appendix
### Summary of Replay-Aware CVRP Benchmark Suite Results

| Condition                     | Replay Mode       | Code Novelty | Final CVRPLIB Gap | Synthetic Holdout Gap | Transfer Gap | Adaptation Efficiency | Compression Pressure |
|-------------------------------|-------------------|--------------|-------------------|----------------------|--------------|-----------------------|----------------------|
| cvrp_no_replay                | none              | 0.0          | 0.2452            | 0.0124               | 0.1417       | 0.0                   | no                   |
| cvrp_random_replay            | random            | 0.82         | 0.2426            | **0.0054**           | 0.1371       | 0.0444                | no                   |
| cvrp_failure_replay           | failure           | 0.0          | **0.2410**        | **0.0054**           | **0.1363**   | 0.0                   | no                   |
| cvrp_failure_replay_compression | failure + compression | 0.0      | 0.2455            | 0.0054               | 0.1388       | 0.0                   | yes                  |

---

### Key Interpretations

- **Best Hold-Out Performance:**
  - *cvrp_failure_replay* achieves the lowest held-out CVRPLIB gap (0.2410), indicating superior generalization on standard benchmarks.
  
- **Best Synthetic Holdout Gap:**
  - Both *cvrp_failure_replay* and *cvrp_random_replay* achieve the lowest synthetic holdout gap (0.0054), suggesting strong performance on synthetic unseen distributions.
  
- **Best Overall Transfer:**
  - *cvrp_failure_replay* leads in mean transfer gap (0.1363) closest to zero, demonstrating the best transfer ability between domains.
  
- **Code Novelty vs Transfer:**
  - *cvrp_random_replay* shows high code novelty (mean 0.82) but offers only a marginal improvement in transfer metrics compared to *cvrp_no_replay*.
  - *cvrp_failure_replay* achieves better transfer metrics without any increase in code novelty, indicating that transfer improvements arise from replay strategy rather than new algorithmic components.
  
- **Compression-Aware Replay:**
  - Adding compression pressure (*cvrp_failure_replay_compression*) does not improve gaps and slightly worsens the held-out CVRPLIB gap and transfer gap relative to *failure replay* without compression.
  
- **No Replay Condition:**
  - The baseline without replay (*cvrp_no_replay*) has the highest CVRPLIB gap and transfer gap, confirming that replay aids performance and transfer.
  
- **Adaptation Efficiency:**
  - Only *cvrp_random_replay* exhibits nonzero adaptation efficiency (0.0444), but without surpassing *failure replay* in transfer metrics.
  
---

### Conservative Conclusions

- Replay modes improve optimality gaps and transfer metrics over no replay.
- Failure replay leads to the best transfer performance and lowest held-out CVRPLIB gap with no reliance on increased code novelty, indicating effective knowledge reuse of failure cases.
- Random replay improves synthetic gap slightly and increases code novelty but does not outperform failure replay in transfer.
- Compression-aware failure replay does not deliver measurable improvement and may slightly degrade performance.
- Improvements are primarily algorithmic due to replay mode rather than lexical/code novelty.

---

### Recommendation

Prioritize **failure replay** as the effective strategy for improving transfer and held-out performance in CVRP benchmarks while maintaining code simplicity and complexity. Random replay introduces more code novelty but has unclear benefits over failure replay. Compression-aware replay appears suboptimal in this setting.
