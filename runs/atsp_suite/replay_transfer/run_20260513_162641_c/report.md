# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_no_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_no_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_162641_c
- started_at_local: 2026-05-13 16:26:41
- finished_at_local: 2026-05-13 16:35:58
- duration_hhmm: 00:09
- duration_seconds: 556.743
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.167273 | 0.024675 | 0.095974 | 0.841331 | 0.78 | 0.055992 |
| atsp_random_replay | random | score_only | False | 0.193105 | 0.008454 | 0.100779 | 0.801225 | 0.58 | 0.007943 |
| atsp_failure_replay | failure | score_only | False | 0.190811 | 0.009004 | 0.099908 | 0.828727 | 0.5875 | 0.013078 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.187223 | 0.009004 | 0.098114 | 0.918878 | 0.58 | 0.037338 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.167273`, synthetic `0.024675`, combined `0.095974`.
- Accepted-epoch count `2`, mean accepted code novelty `0.841331`, and final complexity `0.78`.
- Adaptation efficiency `0.055992` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.167273` across 4 instances; family means: ft=0.206372, ftv=0.300062, p=0.00089, ry=0.161767.
- Panel `synthetic_holdout` mean gap `0.024675` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.064883.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1791, "family": "ftv", "name": "ftv35", "optimality_gap": 0.215886}, {"best_known_cost": 1286, "cost": 1533, "family": "ftv", "name": "ftv33", "optimality_gap": 0.192068}, {"best_known_cost": 1530, "cost": 1716, "family": "ftv", "name": "ftv38", "optimality_gap": 0.121569}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193105`, synthetic `0.008454`, combined `0.100779`.
- Accepted-epoch count `6`, mean accepted code novelty `0.801225`, and final complexity `0.58`.
- Adaptation efficiency `0.007943` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193105` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.109416.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190811`, synthetic `0.009004`, combined `0.099908`.
- Accepted-epoch count `4`, mean accepted code novelty `0.828727`, and final complexity `0.58`.
- Adaptation efficiency `0.013078` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190811` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.101997.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.187223`, synthetic `0.009004`, combined `0.098114`.
- Accepted-epoch count `2`, mean accepted code novelty `0.918878`, and final complexity `0.58`.
- Adaptation efficiency `0.037338` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.187223` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.087644.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Conservative Interpretation of Replay-Aware ATSP Benchmark Suite Results

| Condition                    | Replay Mode       | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Adaptation Efficiency | Mean Code Novelty | Mean Complexity | Notes on Transfer and Novelty               |
|------------------------------|-------------------|------------------|---------------------|--------------------|-----------------------|-------------------|-----------------|---------------------------------------------|
| **atsp_no_replay**            | none              | **0.167273**     | 0.024675            | **0.095974**       | 0.055992              | 0.841331          | 0.78            | Best transfer observed; moderate complexity; high code novelty. |
| **atsp_random_replay**        | random            | 0.193105         | **0.008454**        | 0.100779           | 0.007943              | 0.801225          | 0.58            | Best synthetic gap but worse transfer (TSPLIB gap increases); lower complexity and code novelty. Transfer worse than no replay. |
| **atsp_failure_replay**       | failure           | 0.190811         | 0.009004            | 0.099908           | 0.013078              | 0.828727          | 0.5875          | Similar transfer gap to random replay; code novelty slightly higher but transfer does not improve over no replay. |
| **atsp_failure_replay_compression** | failure + compression | 0.187223      | 0.009004            | 0.098114           | 0.037338              | 0.918878          | 0.58            | Slight improvement in transfer gap vs other replay modes except no replay; highest code novelty; lower complexity. |

---

### Key Points

- **Transfer performance (TSPLIB gap and synthetic holdout gap)**:
  - The **no replay** condition shows the **best transfer performance** (lowest TSPLIB gap of 0.167273 and lowest transfer gap 0.095974).
  - Conditions with **random replay, failure replay**, and **failure replay with compression** achieve better synthetic holdout gaps (~0.008–0.009) but consistently higher TSPLIB gaps (~0.187–0.193), indicating **poorer generalization to held-out TSPLIB instances**.
  - This indicates that replay modes help reduce synthetic gaps but degrade transfer to real-world benchmarks.

- **Code novelty and complexity**:
  - The **no replay** condition has relatively **high code novelty (0.8413)** and **higher complexity (0.78)**.
  - Replay conditions have **lower complexity (~0.58)** and similar or higher code novelty (highest in failure replay with compression at 0.9189).
  - Despite generally higher code novelty under replay (especially compression-aware replay), **transfer performance decreases or remains worse compared to no replay**.
  - Thus, **code novelty does not translate to better transfer performance.**

- **Replay mode distinctions**:
  - **No replay** leads to best transfer performance.
  - **Random replay** reduces synthetic gap significantly but worsens transfer gap.
  - **Failure replay (with or without compression)** improves over random replay slightly in transfer, but not enough to surpass no replay.
  - **Compression-aware failure replay** attains highest novelty and lowest complexity but only modest transfer improvement relative to other replay modes.

- **Adaptation efficiency**:
  - Highest in no replay (0.0559).
  - Significantly lower in replay modes, especially random replay (0.0079).
  - Failure replay with compression has intermediate adaptation efficiency (0.0373), but with no transfer advantage over no replay.

---

### Summary

- The **best transfer results overall come from the no replay condition**, reflected by the lowest TSPLIB and transfer gaps.
- Replay conditions improve synthetic holdout gaps but **degrade or do not improve transfer to TSPLIB ATSP instances**.
- Despite increased code novelty in replay (especially failure replay with compression), there is no corresponding improvement in transfer; in fact, transfer performance worsens compared to no replay.
- Therefore, **code novelty increases under replay but does not equate to better transfer or algorithmic invention** as measured by deterministic metrics.
- Replay mode matters: **random replay yields poorest transfer, failure replays slightly better, but none surpass no replay in transfer performance**.
- Compression pressure under failure replay does not significantly improve transfer but boosts code novelty and reduces complexity.

---

### Conclusion

When prioritizing transfer metrics (held-out TSPLIB and synthetic gap) and optimality gap:

- **No replay condition is most effective for transfer and adaptation efficiency despite its higher complexity.**
- Replay-aware strategies reduce synthetic gaps but harm transfer, indicating overfitting or replay bias.
- Code novelty is not correlated with improved transfer; thus, claims of algorithmic invention based solely on increased novelty under replay are unsupported.
