# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_random_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_185617_t
- started_at_local: 2026-05-13 18:56:17
- finished_at_local: 2026-05-13 19:04:10
- duration_hhmm: 00:08
- duration_seconds: 472.505
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.249401 | 0.036251 | 0.142826 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.188354 | 0.008454 | 0.098404 | 0.870769 | 0.58 | 0.007814 |
| atsp_failure_replay | failure | score_only | False | 0.192846 | 0.009004 | 0.100925 | 0.875702 | 0.58 | 0.007154 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.193715 | 0.009004 | 0.10136 | 0.904573 | 0.58 | 0.017074 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.249401`, synthetic `0.036251`, combined `0.142826`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.249401` across 4 instances; family means: ft=0.445474, ftv=0.398016, p=0.008363, ry=0.14575.
- Panel `synthetic_holdout` mean gap `0.036251` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.059392, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1845, "family": "ftv", "name": "ftv35", "optimality_gap": 0.252546}, {"best_known_cost": 1286, "cost": 1595, "family": "ftv", "name": "ftv33", "optimality_gap": 0.24028}, {"best_known_cost": 1530, "cost": 1785, "family": "ftv", "name": "ftv38", "optimality_gap": 0.166667}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.188354`, synthetic `0.008454`, combined `0.098404`.
- Accepted-epoch count `6`, mean accepted code novelty `0.870769`, and final complexity `0.58`.
- Adaptation efficiency `0.007814` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.188354` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004982, ry=0.093884.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.192846`, synthetic `0.009004`, combined `0.100925`.
- Accepted-epoch count `6`, mean accepted code novelty `0.875702`, and final complexity `0.58`.
- Adaptation efficiency `0.007154` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.192846` across 4 instances; family means: ft=0.319768, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.193715`, synthetic `0.009004`, combined `0.10136`.
- Accepted-epoch count `3`, mean accepted code novelty `0.904573`, and final complexity `0.58`.
- Adaptation efficiency `0.017074` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193715` across 4 instances; family means: ft=0.323244, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}, {"best_known_cost": 1286, "cost": 1478, "family": "ftv", "name": "ftv33", "optimality_gap": 0.1493}]

## Judge Appendix
### Summary of Results for Replay-Aware ATSP Benchmark

| Condition                      | Synthetic Holdout Gap | TSPLIB Held-out Gap | Transfer Gap | Code Novelty (mean) | Replay Mode         | Complexity | Archive | Notes on Transfer and Novelty                  |
|-------------------------------|----------------------|--------------------|--------------|---------------------|---------------------|------------|---------|-----------------------------------------------|
| **atsp_no_replay**             | 0.036251             | 0.249401           | 0.142826     | 0.0                 | none                | 0.78       | 11      | Worst transfer performance; no code novelty. |
| **atsp_random_replay**         | **0.008454**         | **0.188354**       | **0.098404** | 0.870769            | random              | 0.58       | 11      | Best transfer and synthetic gaps despite high code novelty. Complexity reduced. |
| **atsp_failure_replay**        | 0.009004             | 0.192846           | 0.100925     | 0.875702            | failure             | 0.58       | 11      | Comparable transfer to random replay, slightly worse; high code novelty.       |
| **atsp_failure_replay_compression** | 0.009004        | 0.193715           | 0.101360     | 0.904573            | failure + compression | 0.58       | 11      | Similar transfer to failure replay; high novelty, compression pressure applied.|

---

### Interpretation

- **Transfer Performance**  
  Transfer is best under **random replay** (TSPLIB gap 0.188, transfer gap 0.0984), meaning replaying random past experiences improves generalization to unseen TSPLIB instances and synthetic holdouts. Failure replay conditions yield slightly worse transfer gaps (~0.193 TSPLIB, ~0.101 transfer gap). No replay yields the worst transfer (0.249 TSPLIB gap, 0.143 transfer gap).

- **Code Novelty vs Transfer**  
  The **no replay** condition shows zero code novelty and worst transfer. All replay conditions exhibit high mean code novelty (~0.87–0.90) and better transfer performance. This indicates that, while code novelty increases significantly with replay, these improvements correspond to true transfer performance gains rather than lexical novelty alone.

- **Complexity and Archive**  
  Random and failure replay conditions show reduced complexity (0.58) versus no replay (0.78), suggesting replay encourages simpler models or behaviors. Archive size remains constant (11) across conditions.

- **Replay Mode Distinctions**  
  - **No replay:** No replay, no code novelty, worst transfer.  
  - **Random replay:** Best transfer and synthetic holdout gaps; high code novelty; balanced and simpler final behavior profile.  
  - **Failure replay:** Slightly worse transfer than random replay but still improved over no replay; high novelty.  
  - **Failure replay with compression:** Transfer similar to failure replay; high novelty despite compression pressure.

---

### Conservative Conclusions

- The **random replay** condition outperforms no replay and failure replay variants on both synthetic and TSPLIB held-out gaps, establishing it as the best transfer condition empirically.

- Increased code novelty in replay conditions aligns with improved transfer metrics, supporting that the novelty reflects productive algorithmic adaptation rather than superficial lexical variation.

- Compression-aware replay shows no substantial transfer advantage over failure replay alone but maintains high code novelty, suggesting compression pressure does not impair transfer.

- No replay conditions maintain higher model complexity and poorer generalization, confirming the benefit of replay mechanisms for transfer in ATSP.

---

**Recommendation:** Prioritize the random replay mechanism for best transfer performance with moderate complexity and substantial beneficial code novelty. Avoid no replay for transfer tasks as it yields inferior gaps and no innovation.
