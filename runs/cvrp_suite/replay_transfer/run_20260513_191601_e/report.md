# Replay-Aware CVRP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `cvrp_failure_replay`.
- Best CVRPLIB holdout gap: `cvrp_no_replay`.
- Best synthetic holdout gap: `cvrp_random_replay`.

## Run Metadata
- run_name: run_20260513_191601_e
- started_at_local: 2026-05-13 19:16:01
- finished_at_local: 2026-05-13 19:18:58
- duration_hhmm: 00:03
- duration_seconds: 176.732
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_no_replay | none | score_only | False | 0.243109 | 0.01914 | 0.143567 | 0.867949 | 0.78 | 0.01253 |
| cvrp_random_replay | random | score_only | False | 0.253867 | 0.005376 | 0.143427 | 0.910327 | 0.58 | -0.004228 |
| cvrp_failure_replay | failure | score_only | False | 0.245177 | 0.005376 | 0.138599 | 0.871877 | 0.78 | -0.001404 |
| cvrp_failure_replay_compression | failure | novelty_gate | True | 0.253827 | 0.005376 | 0.143404 | 0.0 | 0.58 | 0.0 |

## Condition Notes
### cvrp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.243109`, synthetic `0.01914`, combined `0.143567`.
- Accepted-epoch count `2`, mean accepted code novelty `0.867949`, and final complexity `0.78`.
- Adaptation efficiency `0.01253` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.243109` across 5 instances; family means: A=0.075916, B=0.254196, E=0.324376, P=0.306859.
- Panel `synthetic_holdout` mean gap `0.01914` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.055054.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 672, "cost": 807, "family": "B", "name": "B-n31-k5", "optimality_gap": 0.200893}]

### cvrp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.253867`, synthetic `0.005376`, combined `0.143427`.
- Accepted-epoch count `2`, mean accepted code novelty `0.910327`, and final complexity `0.58`.
- Adaptation efficiency `-0.004228` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.253867` across 5 instances; family means: A=0.143979, B=0.248809, E=0.326296, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1063, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.134472}, {"best_known_cost": 784, "cost": 860, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.096939}]

### cvrp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: CVRPLIB `0.245177`, synthetic `0.005376`, combined `0.138599`.
- Accepted-epoch count `2`, mean accepted code novelty `0.871877`, and final complexity `0.78`.
- Adaptation efficiency `-0.001404` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_cvrplib` mean gap `0.245177` across 5 instances; family means: A=0.091623, B=0.248805, E=0.324376, P=0.312274.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 611, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.334061}, {"best_known_cost": 937, "cost": 1236, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.319104}, {"best_known_cost": 784, "cost": 950, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.211735}]

### cvrp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: CVRPLIB `0.253827`, synthetic `0.005376`, combined `0.143404`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.58`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 5, 'failure_cases': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_cvrplib` mean gap `0.253827` across 5 instances; family means: A=0.115183, B=0.271742, E=0.309021, P=0.301444.
- Panel `synthetic_holdout` mean gap `0.005376` across 4 instances; family means: alternating_belt=0.021505, clustered_demand=0.0, corridor_split=0.0, radial_heavy=0.0.
- Worst recent training cases: [{"best_known_cost": 458, "cost": 604, "family": "P", "name": "P-n40-k5", "optimality_gap": 0.318777}, {"best_known_cost": 937, "cost": 1072, "family": "A", "name": "A-n44-k6", "optimality_gap": 0.144077}, {"best_known_cost": 784, "cost": 858, "family": "A", "name": "A-n32-k5", "optimality_gap": 0.094388}]

## Judge Appendix
### Summary of CVRP Benchmark Transfer and Optimality Gaps

| Condition                   | Replay Mode    | Final CVRPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (mean) | Complexity | Notes on Replay & Selection         |
|-----------------------------|---------------|-------------------|---------------------|--------------------|---------------------|------------|-----------------------------------|
| **cvrp_no_replay**           | None          | **0.2431 (best)** | 0.01914             | 0.14357 (3rd best) | 0.868               | 0.78       | No replay; "score_only" selection |
| **cvrp_random_replay**       | Random replay | 0.2539            | **0.00538 (best)**  | 0.14343 (4th best) | **0.910**           | 0.58       | Random replay; "score_only"       |
| **cvrp_failure_replay**      | Failure replay| 0.2452            | 0.00538             | **0.1386 (best)**  | 0.872               | 0.78       | Failure replay; "score_only"      |
| **cvrp_failure_replay_compression** | Failure replay + compression | 0.2538   | 0.00538             | 0.14340            | 0.0                 | 0.58       | Failure replay + compression; novelty gate |

---

### Key Observations

1. **Held-out CVRPLIB Gap (Primary transfer metric)**
   - Best (lowest) gap: **cvrp_no_replay (0.2431)**
   - Failure replay (0.2452) and failure replay with compression (0.2538) slightly worse.
   - Random replay worst (0.2539).
   
2. **Synthetic Holdout Gap**
   - Best: **Failure replay, random replay, and failure replay compression conditions tie (~0.0054)**
   - No replay significantly worse (0.0191).

3. **Transfer Gap**
   - Best: **cvrp_failure_replay (0.1386)**
   - No replay (0.1436), random replay (0.1434), and compression-aware (0.1434) conditions are close but worse than failure replay.

4. **Code Novelty**
   - Declines to zero with compression-aware replay (0.0).
   - Highest with random replay (0.91), slightly lower with no replay and failure replay (~0.87).
   - Despite zero code novelty, compression-aware replay does not improve transfer metrics.

5. **Complexity**
   - Higher complexity (0.78) under no replay and failure replay.
   - Lower (0.58) for random replay and failure replay + compression.

6. **Adaptation Efficiency and Accepted Epochs**
   - All conditions have low accepted epoch counts (mostly 2, except 1 with compression).
   - Adaptation efficiency negative or close to zero except positive for no replay.

---

### Conservative Interpretation

- **No replay achieves the best generalization performance on the held-out CVRPLIB dataset, indicating stronger transfer optimality despite its higher synthetic gap.**
- **Failure replay condition shows the best transfer gap metric, suggesting failure replay slightly improves transferring to related problem settings.**
- **Random replay achieves the lowest synthetic gap and highest code novelty but does not lead to better held-out CVRPLIB or transfer gap performance, implying lexical/code novelty alone does not correspond to algorithmic improvement or transfer.**
- **Compression-aware failure replay reduces code novelty drastically without improving transfer or optimality gaps, indicating that replay compression may limit beneficial adaptation.**
- **Overall, replay modes improve synthetic holdout gap compared to no replay, but no replay still dominates held-out CVRPLIB optimality. Failure replay may offer a modest transfer advantage, albeit with similar held-out performance to no replay.**

---

### Additional Notes

- Differences in transfer gaps among conditions are relatively small (0.1386 to 0.1436), suggesting subtle effects.
- Selection mode differs for compression-aware replay ("novelty_gate") vs others ("score_only"), which might affect code novelty and adaptation behavior.
- No evidence from metrics to support claims of algorithmic invention purely based on code novelty.

---

### Summary Table

| Condition                   | Held-out CVRPLIB Gap (↓ better) | Synthetic Holdout Gap (↓ better) | Transfer Gap (↓ better) | Code Novelty | Replay Type           | Comments                                    |
|-----------------------------|---------------------------------|---------------------------------|------------------------|--------------|----------------------|---------------------------------------------|
| **cvrp_no_replay**          | **0.2431 (best)**               | 0.0191                         | 0.1436                 | 0.868        | None                 | Best held-out performance                    |
| **cvrp_failure_replay**     | 0.2452                         | 0.0054                         | **0.1386 (best)**      | 0.872        | Failure Replay       | Best transfer gap highlighting mild benefit|
| **cvrp_random_replay**      | 0.2539                         | **0.0054 (best)**              | 0.1434                 | **0.910**    | Random Replay        | Highest novelty but worse held-out CVRPLIB  |
| **cvrp_failure_replay_compression** | 0.2538                 | 0.0054                         | 0.1434                 | 0.0          | Failure Replay + Comp.| Compression reduces novelty, no performance gain |

---

**Conclusion:**

- The benchmark supports the conclusion that **no replay ensures superior held-out CVRPLIB optimality**, while **failure replay offers a small transfer gap improvement** without increasing novelty.
- Code novelty improvements with random replay do not translate into unequivocal transfer or optimality gains.
- Compression-aware replay sacrifices code novelty with no clear transfer benefit.
- Interpretations should focus on numeric gaps rather than code novelty or qualitative narratives of algorithmic invention.
