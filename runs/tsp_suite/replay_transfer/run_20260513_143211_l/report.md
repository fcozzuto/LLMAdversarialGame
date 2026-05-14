# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `tsplib_random_replay`.
- Best TSPLIB holdout gap: `tsplib_random_replay`.
- Best synthetic holdout gap: `tsplib_no_replay`.

## Run Metadata
- run_name: run_20260513_143211_l
- started_at_local: 2026-05-13 14:32:11
- finished_at_local: 2026-05-13 14:42:57
- duration_hhmm: 00:11
- duration_seconds: 646.273
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_no_replay | none | score_only | False | 0.16877 | 0.0 | 0.107399 | 0.0 | 0.76 | 0.0 |
| tsplib_random_replay | random | score_only | False | 0.097675 | 0.0 | 0.062157 | 0.747293 | 0.76 | 0.024494 |
| tsplib_failure_replay | failure | score_only | False | 0.111105 | 0.0 | 0.070703 | 0.788828 | 0.76 | 0.16106 |
| tsplib_failure_replay_compression | failure | novelty_gate | True | 0.176277 | 0.010343 | 0.115937 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### tsplib_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.16877`, synthetic `0.0`, combined `0.107399`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.16877` across 7 instances; family means: ch=0.186649, kroD=0.149291, pcb=0.235141, pr=0.246091, rd=0.122756, st=0.054815.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3445, "family": "a", "name": "a280", "optimality_gap": 0.335789}, {"best_known_cost": 14379, "cost": 18952, "family": "lin", "name": "lin105", "optimality_gap": 0.318033}, {"best_known_cost": 629, "cost": 738, "family": "eil", "name": "eil101", "optimality_gap": 0.173291}]

### tsplib_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.097675`, synthetic `0.0`, combined `0.062157`.
- Accepted-epoch count `3`, mean accepted code novelty `0.747293`, and final complexity `0.76`.
- Adaptation efficiency `0.024494` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.097675` across 7 instances; family means: ch=0.183951, kroD=0.052221, pcb=0.162275, pr=0.036113, rd=0.032617, st=0.032593.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3428, "family": "a", "name": "a280", "optimality_gap": 0.329197}, {"best_known_cost": 629, "cost": 765, "family": "eil", "name": "eil101", "optimality_gap": 0.216216}, {"best_known_cost": 14379, "cost": 17241, "family": "lin", "name": "lin105", "optimality_gap": 0.19904}]

### tsplib_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.111105`, synthetic `0.0`, combined `0.070703`.
- Accepted-epoch count `2`, mean accepted code novelty `0.788828`, and final complexity `0.76`.
- Adaptation efficiency `0.16106` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.111105` across 7 instances; family means: ch=0.098865, kroD=0.070583, pcb=0.249439, pr=0.112871, rd=0.071555, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3467, "family": "a", "name": "a280", "optimality_gap": 0.34432}, {"best_known_cost": 7542, "cost": 9813, "family": "berlin", "name": "berlin52", "optimality_gap": 0.301114}, {"best_known_cost": 629, "cost": 753, "family": "eil", "name": "eil101", "optimality_gap": 0.197138}]

### tsplib_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.176277`, synthetic `0.010343`, combined `0.115937`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 6, 'failure_cases': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.176277` across 7 instances; family means: ch=0.168312, kroD=0.250305, pcb=0.216846, pr=0.240627, rd=0.164349, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19083, "family": "lin", "name": "lin105", "optimality_gap": 0.327144}, {"best_known_cost": 2579, "cost": 3332, "family": "a", "name": "a280", "optimality_gap": 0.291974}, {"best_known_cost": 629, "cost": 685, "family": "eil", "name": "eil101", "optimality_gap": 0.08903}]

## Judge Appendix
### Summary of Replay-Aware TSP Benchmark Results

| Condition                        | Replay Mode         | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Notes on Transfer & Novelty                               |
|---------------------------------|---------------------|-----------------|--------------------|-------------------|---------------------|----------------------------------------------------------|
| **tsplib_no_replay**             | None                | 0.16877         | 0.0                | 0.107399          | 0.0                 | Baseline with no replay; moderate transfer gap; no novelty.  |
| **tsplib_random_replay**         | Random              | **0.097675**    | 0.0                | **0.062157**      | 0.747293            | Best transfer performance on TSPLIB and best holdout; higher code novelty but no evidence that novelty correlates with better algorithmic behavior. |
| **tsplib_failure_replay**        | Failure             | 0.111105        | 0.0                | 0.070703          | 0.788828            | Slightly worse transfer than random replay, despite highest adaptation efficiency and code novelty.  |
| **tsplib_failure_replay_compression** | Failure + Compression | 0.176277     | 0.010343           | 0.115937          | 0.0                 | Worst transfer performance; compression pressure present; no code novelty observed. |

---

### Key Interpretations

- **Transfer Metrics (Primary Evidence):**  
  The **random replay condition** demonstrates the best transfer performance, reflected in the lowest TSPLIB optimality gap (0.097675) and the lowest mean transfer gap (0.062157). The **no replay condition** performs worse in transfer (TSPLIB gap 0.16877; transfer gap 0.107399), while both failure replay conditions perform intermediately to poorly.

- **Synthetic Holdout Gap:**  
  Only the compression-aware failure replay condition shows a notable synthetic holdout gap (0.0103), indicating slightly worse generalization there. Other replay modes achieve zero synthetic holdout gap, indicating good synthetic domain transfer.

- **Code Novelty vs Transfer:**  
  The random replay and failure replay modes show high mean code novelty (~0.75-0.79), while no replay and compression-aware failure replay show zero. However, better transfer (random replay) is associated with **higher code novelty** than no replay, which contradicts a simplistic assumption that novelty should be low to improve transfer. The compression-aware failure replay lacks code novelty but performs worst on transfer, suggesting code novelty alone does not drive generalization.

- **Replay Mode Implications:**  
  - **No Replay:** Baseline with moderate transfer and no code novelty.  
  - **Random Replay:** Best transfer with higher code novelty; implies replay diversity boosts transfer but lowers code novelty.  
  - **Failure Replay:** Moderate transfer, highest adaptation efficiency, high code novelty but no clear transfer advantage over random replay.  
  - **Failure Replay + Compression:** Compression pressure seems to impair transfer and induce some synthetic gap; no code novelty present.

- **Complexity and Behavior Profiles:**  
  All conditions have identical final complexity (0.76), so complexity is not a factor in transfer differences. Behavior profile shifts only reported in compression-aware failure replay (clustered_constructor), but without corresponding transfer advantage.

---

### Conclusion

- The **random replay condition yields the best transfer to held-out TSPLIB and synthetic instances**, supported by the lowest mean optimality gaps, despite increased code novelty compared to no replay.  
- Novelty metrics should be interpreted cautiously; higher code novelty in random replay does not imply lack of improvement — rather, transfer improves while novelty increases, showing novelty and transfer are not inversely related here.  
- Failure replay conditions, while featuring strong adaptation efficiency and code novelty, do not outperform random replay in transfer metrics.  
- Compression-aware failure replay degrades transfer and generalization despite replay use, with no code novelty, emphasizing that compression pressure can harm performance.  
- Overall, **random replay is the recommended replay strategy for optimal transfer, with no evidence that code novelty loss is necessary to gain this benefit.**
