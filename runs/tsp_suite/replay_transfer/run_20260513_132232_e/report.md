# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_132232_e
- started_at_local: 2026-05-13 13:22:32
- finished_at_local: 2026-05-13 13:32:39
- duration_hhmm: 00:10
- duration_seconds: 606.772
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.876497 | 0.56 | -0.028414 |
| tsplib_random_replay | random | score_only | False | 0.174852 | 0.0 | 0.111269 | 0.783231 | 0.76 | 0.010286 |
| tsplib_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.885112 | 0.56 | -0.028138 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.876497`, and final complexity `0.56`.
- Adaptation efficiency `-0.028414` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.174852`, synthetic `0.0`, combined `0.111269`.
- Accepted-epoch count `2`, mean accepted code novelty `0.783231`, and final complexity `0.76`.
- Adaptation efficiency `0.010286` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.174852` across 7 instances; family means: ch=0.119618, kroD=0.117169, pcb=0.275848, pr=0.440555, rd=0.065234, st=0.085926.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3060, "family": "a", "name": "a280", "optimality_gap": 0.186506}, {"best_known_cost": 7542, "cost": 8060, "family": "berlin", "name": "berlin52", "optimality_gap": 0.068682}, {"best_known_cost": 14379, "cost": 15319, "family": "lin", "name": "lin105", "optimality_gap": 0.065373}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.885112`, and final complexity `0.56`.
- Adaptation efficiency `-0.028138` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

## Judge Appendix
```markdown
### Summary of Replay Conditions in TSP Benchmark Suite

| Condition                     | Replay Mode           | Compression | Mean Held-out TSPLIB Gap | Mean Synthetic Holdout Gap | Mean Transfer Gap | Final Complexity | Code Novelty (mean) | Notes on Metrics and Transfer          |
|-------------------------------|----------------------|-------------|-------------------------|----------------------------|-------------------|------------------|---------------------|---------------------------------------|
| tsplib_no_replay              | None                 | No          | 0.213                   | 0.065                      | 0.159             | 0.56             | 0.876               | Baseline gaps relatively high.        |
| tsplib_random_replay          | Random               | No          | **0.175**               | **0.0**                    | **0.111**         | 0.76             | 0.783               | Best transfer and generalization performance; lower code novelty than no replay. |
| tsplib_failure_replay         | Failure              | No          | 0.213                   | 0.065                      | 0.159             | 0.56             | 0.885               | Same gaps as no replay; high code novelty but no transfer improvement. |
| tsplib_failure_replay_compression | Failure + Compression | Yes         | 0.213                   | 0.065                      | 0.159             | 0.56             | 0.0                 | No code novelty; no gap improvement over failure replay without compression. |

---

### Detailed Interpretation

- **Transfer metrics (held-out TSPLIB and synthetic holdout gaps):**
  - **tsplib_random_replay** achieves the lowest held-out TSPLIB gap (0.175) and synthetic holdout gap (0.0), representing the best transfer/generalization.
  - Other replay conditions, including no replay and failure replay (with or without compression), show the same higher held-out and synthetic gaps (0.213 and 0.065 respectively).
  
- **Code novelty vs. Transfer:**
  - **tsplib_random_replay** shows a notable reduction in mean code novelty (~0.783) compared to no replay (~0.876) and failure replay (~0.885), while achieving better transfer performance.
  - This indicates that lower lexical/code novelty does not preclude improved transfer/generalization.
  - Failure replay (both with and without compression) maintains high code novelty but does not improve transfer gaps relative to no replay.
  - Compression-aware failure replay notably results in zero code novelty but offers no improvement in transfer, suggesting compression reduces novelty without benefiting algorithmic performance.

- **Replay modes:**
  - **No replay:** Baseline with no replay experience; associated with largest transfer gaps.
  - **Random replay:** Sampling replayed experiences randomly; yields best transfer performance and lowers code novelty.
  - **Failure replay:** Replaying failure cases only; no transfer improvement compared to no replay.
  - **Failure replay with compression:** Adds compression pressure to failure replay; further lowers code novelty to zero but transfer gaps remain unimproved.

- **Complexity and behavior:**
  - Random replay leads to higher final complexity (0.76) and clustered constructor behavior profile, correlated with better transfer.
  - Other conditions have moderate complexity (0.56) and balanced behavior.

- **Adaptation efficiency:**
  - Random replay uniquely shows positive adaptation efficiency (0.0103), indicating better learning dynamics.

---

### Conclusions

- **Best transfer and generalization are achieved under tsplib_random_replay, confirming the efficacy of random replay over no replay or failure-only replay in this benchmark.**
- **Improved transfer under random replay occurs despite a decline in code novelty, indicating code novelty is not a driver of transfer performance here.**
- **Failure replay (with or without compression) maintains high code novelty but does not improve transfer metrics versus no replay, challenging the assumption that lexical novelty correlates with algorithmic innovation.**
- **Compression-aware replay suppresses code novelty entirely without providing transfer benefits, suggesting it reduces exploration without enhancing solution quality.**

**Hence, random replay is the most effective replay strategy for this TSP benchmark suite, yielding better optimality gaps and transfer with moderately lower code novelty.**
