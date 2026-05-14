# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_random_replay`.
- Best synthetic holdout gap: `atsp_failure_replay`.

## Run Metadata
- run_name: run_20260513_165255_f
- started_at_local: 2026-05-13 16:52:55
- finished_at_local: 2026-05-13 17:03:40
- duration_hhmm: 00:11
- duration_seconds: 644.84
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.192059 | 0.030781 | 0.11142 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.160422 | 0.027584 | 0.094003 | 0.653594 | 0.78 | 0.055151 |
| atsp_failure_replay | failure | score_only | False | 0.191028 | 0.009004 | 0.100016 | 0.744019 | 0.58 | 0.021662 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.172128 | 0.027465 | 0.099796 | 0.698911 | 0.78 | 0.034411 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192059`, synthetic `0.030781`, combined `0.11142`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192059` across 4 instances; family means: ft=0.280377, ftv=0.295102, p=0.01726, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.030781` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.037511, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1887, "family": "ftv", "name": "ftv35", "optimality_gap": 0.281059}, {"best_known_cost": 1286, "cost": 1591, "family": "ftv", "name": "ftv33", "optimality_gap": 0.23717}, {"best_known_cost": 1530, "cost": 1842, "family": "ftv", "name": "ftv38", "optimality_gap": 0.203922}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.160422`, synthetic `0.027584`, combined `0.094003`.
- Accepted-epoch count `3`, mean accepted code novelty `0.653594`, and final complexity `0.78`.
- Adaptation efficiency `0.055151` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.160422` across 4 instances; family means: ft=0.246054, ftv=0.295102, p=0.003737, ry=0.096797.
- Panel `synthetic_holdout` mean gap `0.027584` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.024723, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1572, "family": "ftv", "name": "ftv33", "optimality_gap": 0.222395}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1530, "cost": 1761, "family": "ftv", "name": "ftv38", "optimality_gap": 0.15098}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.191028`, synthetic `0.009004`, combined `0.100016`.
- Accepted-epoch count `3`, mean accepted code novelty `0.744019`, and final complexity `0.58`.
- Adaptation efficiency `0.021662` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.191028` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.172128`, synthetic `0.027465`, combined `0.099796`.
- Accepted-epoch count `2`, mean accepted code novelty `0.698911`, and final complexity `0.78`.
- Adaptation efficiency `0.034411` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.172128` across 4 instances; family means: ft=0.292976, ftv=0.294482, p=0.001068, ry=0.099986.
- Panel `synthetic_holdout` mean gap `0.027465` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033248, wind_clusters=0.076613.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1995, "family": "ftv", "name": "ftv38", "optimality_gap": 0.303922}, {"best_known_cost": 1473, "cost": 1748, "family": "ftv", "name": "ftv35", "optimality_gap": 0.186694}, {"best_known_cost": 1286, "cost": 1366, "family": "ftv", "name": "ftv33", "optimality_gap": 0.062208}]

## Judge Appendix
### Summary of Replay-Aware ATSP Benchmark Results

| Condition                      | Replay Mode        | Synthetic Holdout Gap | Held-out TSPLIB Gap | Transfer Gap | Code Novelty (mean) | Complexity | Notes on Transfer vs Novelty                  |
|------------------------------|--------------------|----------------------|---------------------|--------------|---------------------|------------|-----------------------------------------------|
| **atsp_no_replay**            | None               | 0.0308               | 0.1921              | 0.1114       | 0.0                 | 0.78       | Baseline. No code novelty. Transfer gaps are highest here.            |
| **atsp_random_replay**        | Random Replay      | 0.0276               | **0.1604**          | **0.0940**   | 0.654               | 0.78       | Best held-out TSPLIB gap and transfer gap, despite only moderate complexity. Code novelty is substantially higher than no replay.    |
| **atsp_failure_replay**       | Failure Replay     | **0.0090**           | 0.1910              | 0.1000       | 0.744               | 0.58       | Best synthetic gap with lower complexity, but no TSPLIB gap improvement vs no replay. Transfer gap improved vs no replay. Code novelty increases notably. |
| **atsp_failure_replay_compression** | Failure Replay + Compression | 0.0275           | 0.1721              | 0.0998       | 0.699               | 0.78       | Compression pressure active. TSPLIB and transfer gaps intermediate. Code novelty higher than no replay but lower than random replay failure replay. |

---

### Interpretation Focused on Optimality Gap & Transfer (Main Evidence)

- **Transfer performance (held-out TSPLIB & transfer gaps) favors `atsp_random_replay` over other conditions**, with a mean held-out TSPLIB gap of 0.1604 and transfer gap 0.0940, indicating better generalization to unseen ATSP instances.
- Although the **`atsp_failure_replay` condition has the best synthetic holdout gap (0.0090), its held-out TSPLIB gap (0.1910) is comparable to no replay (0.1921) and worse than random replay**, so transfer to real-world instances is not improved here.
- Compression-aware failure replay gives **no significant TSPLIB or transfer gap advantage compared to random or simple failure replay**, despite compression pressure and moderate code novelty.
- **No replay has the worst transfer performance and zero code novelty**, confirming no replay leads to poorer adaptation to new instances.

---

### Code Novelty vs Transfer

- **Code novelty increases from no replay (0.0) to random replay (~0.65) and failure replay (~0.74), but transfer gap is best for random replay**.
- Failure replay modes (with or without compression) have higher code novelty but do **not improve TSPLIB transfer over random replay**, showing that increased lexical novelty does not guarantee better transfer.
- Since complexity remains relatively stable except for lower in failure replay (0.58), improvements in transfer (random replay) are not simply due to lower model complexity or oversimplification.

---

### Replay Mode Impact

- **No replay results in poorer transfer and zero adaptation efficiency.**
- **Random replay is associated with better held-out TSPLIB and transfer gaps, moderately high code novelty, and stable complexity.**
- **Failure replay improves synthetic gap and induces higher code novelty and reduced complexity, but does not improve TSPLIB transfer or reduce transfer gap as effectively as random replay.**
- **Compression-aware failure replay does not outperform pure failure replay or random replay in transfer metrics, despite added compression pressure and high code novelty.**

---

### Conservative Conclusion

- The **random replay condition provides the best overall transfer to held-out TSPLIB ATSP instances and synthetic benchmarks, with a reasonable balance of complexity and code novelty**.
- Failure replay (with or without compression) boosts code novelty and synthetic performance but does not translate into improved transfer to TSPLIB ATSP benchmark instances.
- Code novelty increases with replay modes, but **lexical novelty alone is not indicative of transfer improvement**, especially as failure replay conditions have higher novelty but not better TSPLIB transfer compared to random replay.
- Compression-aware replay adds little transfer benefit beyond failure replay, suggesting compression pressure may not directly enhance generalization in this context.

---

# Key Metrics Table (condensed)

| Replay Mode                   | Synthetic Gap | Held-out TSPLIB Gap | Transfer Gap | Mean Code Novelty | Complexity | Adaptation Efficiency |
|------------------------------|---------------|---------------------|--------------|-------------------|------------|-----------------------|
| No Replay                    | 0.03078       | 0.19206             | 0.11142      | 0.0               | 0.78       | 0.0                   |
| Random Replay                | 0.02758       | **0.16042**         | **0.09400**  | 0.654             | 0.78       | 0.055                 |
| Failure Replay              | **0.00900**   | 0.19103             | 0.10002      | 0.744             | 0.58       | 0.022                 |
| Failure Replay + Compression | 0.02747       | 0.17213             | 0.09980      | 0.699             | 0.78       | 0.034                 |

---

# Final Notes

- Prioritize random replay as the most effective transfer condition.
- Failure replay improves synthetic gaps and code novelty but not transfer to held-out TSPLIB.
- Compression-aware replay adds complexity management but no transfer advantage.
- Avoid conflating code novelty or lexical novelty with algorithmic invention without supporting transfer gap improvement.
