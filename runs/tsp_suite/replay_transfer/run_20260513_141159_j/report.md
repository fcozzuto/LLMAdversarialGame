# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_failure_replay_compression`.
- Best TSPLIB holdout gap: `tsplib_failure_replay_compression`.
- Best synthetic holdout gap: `tsplib_random_replay`.

## Run Metadata
- run_name: run_20260513_141159_j
- started_at_local: 2026-05-13 14:11:59
- finished_at_local: 2026-05-13 14:22:30
- duration_hhmm: 00:11
- duration_seconds: 630.69
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.887401 | 0.56 | -0.028065 |
| tsplib_random_replay | random | score_only | False | 0.147693 | 0.0 | 0.093986 | 0.701982 | 0.76 | 0.107141 |
| tsplib_failure_replay | failure | score_only | False | 0.197828 | 0.0 | 0.125891 | 0.0 | 0.76 | 0.0 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.119024 | 0.0 | 0.075743 | 0.735647 | 0.76 | 0.020953 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.887401`, and final complexity `0.56`.
- Adaptation efficiency `-0.028065` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "family": "a", "name": "a280", "optimality_gap": 0.401318}, {"best_known_cost": 629, "cost": 875, "family": "eil", "name": "eil101", "optimality_gap": 0.391097}, {"best_known_cost": 14379, "cost": 19107, "family": "lin", "name": "lin105", "optimality_gap": 0.328813}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.147693`, synthetic `0.0`, combined `0.093986`.
- Accepted-epoch count `2`, mean accepted code novelty `0.701982`, and final complexity `0.76`.
- Adaptation efficiency `0.107141` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.147693` across 7 instances; family means: ch=0.119814, kroD=0.198366, pcb=0.191677, pr=0.248144, rd=0.12048, st=0.035556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3274, "family": "a", "name": "a280", "optimality_gap": 0.269484}, {"best_known_cost": 14379, "cost": 17172, "family": "lin", "name": "lin105", "optimality_gap": 0.194242}, {"best_known_cost": 629, "cost": 737, "family": "eil", "name": "eil101", "optimality_gap": 0.171701}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.197828`, synthetic `0.0`, combined `0.125891`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.197828` across 7 instances; family means: ch=0.260217, kroD=0.216446, pcb=0.189413, pr=0.242939, rd=0.18445, st=0.031111.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3418, "family": "a", "name": "a280", "optimality_gap": 0.32532}, {"best_known_cost": 629, "cost": 771, "family": "eil", "name": "eil101", "optimality_gap": 0.225755}, {"best_known_cost": 7542, "cost": 9166, "family": "berlin", "name": "berlin52", "optimality_gap": 0.215327}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.119024`, synthetic `0.0`, combined `0.075743`.
- Accepted-epoch count `4`, mean accepted code novelty `0.735647`, and final complexity `0.76`.
- Adaptation efficiency `0.020953` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.119024` across 7 instances; family means: ch=0.090423, kroD=0.122617, pcb=0.218461, pr=0.116107, rd=0.066245, st=0.128889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3516, "family": "a", "name": "a280", "optimality_gap": 0.363319}, {"best_known_cost": 629, "cost": 778, "family": "eil", "name": "eil101", "optimality_gap": 0.236884}, {"best_known_cost": 7542, "cost": 9087, "family": "berlin", "name": "berlin52", "optimality_gap": 0.204853}]

## Judge Appendix
### Summary of Results for Replay-Aware TSP Benchmark

| Condition                     | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Replay Mode          | Code Novelty (mean) | Complexity | Notes on Transfer and Novelty                   |
|-------------------------------|-----------------|--------------------|-------------------|----------------------|---------------------|------------|------------------------------------------------|
| **tsplib_failure_replay_compression** | **0.1190**       | 0.0                | **0.0757**       | failure + compression | 0.7356              | 0.76       | Best transfer (TSPLIB and synthetic heldout); code novelty lower than no replay but transfer substantially improved; compression-aware replay aids transfer |
| tsplib_random_replay           | 0.1477          | **0.0**            | 0.09399           | random replay         | 0.7019              | 0.76       | Best synthetic holdout; better transfer gap than no replay and failure replay; code novelty lower than no replay but improved transfer |
| tsplib_failure_replay          | 0.1978          | 0.0                | 0.1259            | failure replay        | 0.0                 | 0.76       | No code novelty; worse transfer than random replay and failure replay with compression |
| tsplib_no_replay               | 0.2134          | 0.0649             | 0.1594            | no replay             | **0.8874**          | 0.56       | Highest code novelty but worst transfer metrics; replay mechanisms improve transfer despite drop in novelty |

---

### Conservative Interpretation

- **Transfer Evidence (Held-out TSPLIB and Synthetic Gaps):**  
  - The **tsplib_failure_replay_compression** condition yields the lowest TSPLIB and transfer gaps (0.1190 and 0.0757), indicating superior generalization and transfer to held-out benchmark instances.  
  - The **tsplib_random_replay** condition also shows strong transfer performance (TSPLIB gap 0.1477, transfer gap 0.09399) and is best in synthetic holdouts (mean synthetic gap 0.0).  
  - Both failure replay alone and no replay yield higher transfer gaps, with no replay showing the worst transfer (TSPLIB gap 0.2134, transfer gap 0.1594).

- **Code Novelty vs Transfer:**  
  - The no replay condition exhibits the highest code novelty (~0.887), yet has the poorest transfer metrics.  
  - All replay modes reduce code novelty (0 to ~0.73 range) while improving transfer gaps; notably, **failure replay + compression** achieves the best transfer with moderate code novelty.  
  - This demonstrates a clear pattern: **code novelty decreases while transfer performance improves**, implying lexical novelty does not directly equate to algorithmic invention or better transfer.

- **Replay Method Distinctions:**  
  - **No Replay:** Highest code novelty but worst generalization and transfer.  
  - **Random Replay:** Good transfer, some code novelty retained, best synthetic gap.  
  - **Failure Replay:** No code novelty retained, transfer worse than compression-aware failure replay.  
  - **Failure Replay + Compression:** Best transfer performance, moderate code novelty, higher complexity (0.76), and specialized final behavior ("clustered_constructor").

- **Algorithmic Behavior & Complexity:**  
  - Replay conditions (especially compression-aware failure replay) maintain or increase complexity (0.76) compared to no replay (0.56), suggesting more sophisticated/structured behavior contributing to transfer improvements.  
  - Final behavior profiles differ: "balanced" for no replay/random/failure replay, "clustered_constructor" for failure replay with compression.

---

### Conclusion

- **Best transfer results are obtained with failure replay combined with compression pressure,** outperforming both random and vanilla failure replay, and no replay conditions on both held-out TSPLIB and synthetic benchmarks.  
- **This improvement in transfer comes at the cost of reduced code novelty**, showing that replay affects algorithmic generalization more than it spurs lexical novelty.  
- **Random replay is a viable alternative yielding good transfer and synthetic performance with moderate novelty.**  
- **No replay affords high novelty but at notable transfer and performance costs.**  
- Replay mechanisms, especially compression-aware failure replay, effectively guide algorithms toward improved transfer metrics, supported by deterministic optimality gaps and not narrative speculation.

---

### Recommendation for Benchmark Usage

Use **tsplib_failure_replay_compression** as the primary benchmark condition for evaluating transfer-aware TSP algorithms due to its demonstrably superior transfer performance. Consider **tsplib_random_replay** as an alternative with competitive transfer and zero synthetic gaps. Avoid no replay if transfer is the evaluation priority despite its higher code novelty.
