# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_random_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_163559_d
- started_at_local: 2026-05-13 16:35:59
- finished_at_local: 2026-05-13 16:44:29
- duration_hhmm: 00:09
- duration_seconds: 510.492
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.246501 | 0.040656 | 0.143578 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.190037 | 0.008454 | 0.099246 | 0.841807 | 0.58 | 0.013208 |
| atsp_failure_replay | failure | score_only | False | 0.195764 | 0.041579 | 0.118671 | 0.0 | 0.78 | 0.0 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.192926 | 0.009004 | 0.100965 | 0.906484 | 0.58 | 0.017352 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.246501`, synthetic `0.040656`, combined `0.143578`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.246501` across 4 instances; family means: ft=0.426937, ftv=0.398016, p=0.015302, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.040656` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.077011, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1286, "cost": 1578, "family": "ftv", "name": "ftv33", "optimality_gap": 0.227061}, {"best_known_cost": 1530, "cost": 1863, "family": "ftv", "name": "ftv38", "optimality_gap": 0.217647}, {"best_known_cost": 1473, "cost": 1723, "family": "ftv", "name": "ftv35", "optimality_gap": 0.169722}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.190037`, synthetic `0.008454`, combined `0.099246`.
- Accepted-epoch count `4`, mean accepted code novelty `0.841807`, and final complexity `0.58`.
- Adaptation efficiency `0.013208` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.190037` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004982, ry=0.097143.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.195764`, synthetic `0.041579`, combined `0.118671`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.195764` across 4 instances; family means: ft=0.32281, ftv=0.295102, p=0.019395, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.041579` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.080705, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1864, "family": "ftv", "name": "ftv35", "optimality_gap": 0.265445}, {"best_known_cost": 1530, "cost": 1892, "family": "ftv", "name": "ftv38", "optimality_gap": 0.236601}, {"best_known_cost": 1286, "cost": 1511, "family": "ftv", "name": "ftv33", "optimality_gap": 0.174961}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.192926`, synthetic `0.009004`, combined `0.100965`.
- Accepted-epoch count `3`, mean accepted code novelty `0.906484`, and final complexity `0.58`.
- Adaptation efficiency `0.017352` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192926` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.110456.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1939, "family": "ftv", "name": "ftv38", "optimality_gap": 0.26732}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
```markdown
# Review of Replay-Aware ATSP Benchmark Suite

## Main Evidence Focus: Held-out TSPLIB ATSP Gaps & Synthetic Holdout Gaps

| Condition                     | Replay Mode      | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Mean Code Novelty | Mean Complexity | Notes on Novelty & Transfer                              |
|-------------------------------|------------------|-----------------|--------------------|-------------------|-------------------|-----------------|----------------------------------------------------------|
| **atsp_no_replay**             | none             | 0.2465          | 0.0407             | 0.1436            | 0.0               | 0.78            | Baseline no replay; highest gaps; zero code novelty      |
| **atsp_random_replay**         | random           | 0.1900          | 0.0085             | 0.0992            | 0.84              | 0.58            | Best transfer and synthetic gaps; high code novelty; lower complexity |
| **atsp_failure_replay**        | failure          | 0.1958          | 0.0416             | 0.1187            | 0.0               | 0.78            | Moderate gaps; zero code novelty; no compression pressure|
| **atsp_failure_replay_compression** | failure + compression | 0.1929    | 0.0090             | 0.1010            | 0.91              | 0.58            | Similar transfer to random replay; high code novelty; compression pressure applied |

---

## Interpretation

### Transfer Metrics (Held-out TSPLIB & Synthetic Gaps)
- **atsp_random_replay** achieves the lowest mean TSPLIB gap (0.1900) and synthetic gap (0.0085), with best mean transfer gap (0.0992), indicating superior generalization/transfer.
- Both **failure replay conditions** improve over no replay in transfer and synthetic gaps but are slightly worse than random replay.
- **No replay** yields substantially higher gaps across all transfer metrics.

### Code Novelty vs Transfer Performance
- Code novelty is zero for no replay and failure replay (no compression), despite improved transfer in failure replay compared to no replay.
- High code novelty (~0.84 and ~0.91) occurs under random replay and failure replay with compression, coinciding with improved transfer gaps.
- This demonstrates that **transfer improves notably with replay (especially random)** even when code novelty is zero (failure replay without compression).
- When code novelty rises (random replay and failure + compression), transfer improves further and complexity decreases.
- Hence, **increased code novelty accompanies transfer improvements but is not necessary for transfer gains**.

### Replay Mode and Complexity
- Replay presence (random or failure) reduces final complexity (~0.58) relative to no replay (~0.78).
- Compression pressure is only present in the failure replay with compression condition and coincides with high code novelty and transfer improvements similar to random replay.
- No replay conditions show clustered constructors; replay conditions yield a more balanced final behavior profile.

---

## Conservative Summary

- **Random replay ("atsp_random_replay") is most effective**, yielding lowest TSPLIB and synthetic gaps and highest transfer performance, while substantially reducing search complexity.
- Failure replay without compression improves transfer versus no replay but does not raise code novelty.
- Compression-aware failure replay produces similar transfer benefits as random replay, with even higher code novelty.
- Improvements in transfer and complexity under replay modes occur independently of code novelty in some cases; lexical/code novelty increases do not alone signify algorithmic invention without corresponding metric gains.
- No replay is the least effective condition, reinforcing that replay (random or failure) confers valuable learning benefits.
- Replay mode is a key factor influencing transfer and complexity, with random replay outperforming targeted failure replay.
- Compression pressures may further enable code novelty increases alongside transfer gains, but transfer improvements can be achieved without them.

---

# Key Recommendations
- Prioritize **random replay** for ATSP transfer benchmark tasks to maximize generalization.
- Recognize that **code novelty metrics may not fully explain transfer improvements**; focus on deterministic gaps and complexity measures.
- Carefully distinguish replay modes; replay type impacts transfer and code evolution differently.
```
