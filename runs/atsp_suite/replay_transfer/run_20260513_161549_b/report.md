# Replay-Aware ATSP Benchmark Report

## Overview
- Condition count: 4.
- Best final transfer gap: `atsp_random_replay`.
- Best TSPLIB ATSP holdout gap: `atsp_random_replay`.
- Best synthetic holdout gap: `atsp_random_replay`.

## Run Metadata
- run_name: run_20260513_161549_b
- started_at_local: 2026-05-13 16:15:49
- finished_at_local: 2026-05-13 16:26:40
- duration_hhmm: 00:11
- duration_seconds: 650.718
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB ATSP Gap | Final Synthetic Gap | Final Transfer Gap | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_no_replay | none | score_only | False | 0.242634 | 0.036251 | 0.139442 | 0.0 | 0.78 | 0.0 |
| atsp_random_replay | random | score_only | False | 0.189005 | 0.008454 | 0.098729 | 0.64691 | 0.58 | 0.010472 |
| atsp_failure_replay | failure | score_only | False | 0.193498 | 0.009004 | 0.101251 | 0.709445 | 0.58 | 0.008788 |
| atsp_failure_replay_compression | failure | novelty_gate | True | 0.255673 | 0.036251 | 0.145962 | 0.0 | 0.78 | 0.0 |

## Condition Notes
### atsp_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.242634`, synthetic `0.036251`, combined `0.139442`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.242634` across 4 instances; family means: ft=0.4, ftv=0.376317, p=0.013523, ry=0.180696.
- Panel `synthetic_holdout` mean gap `0.036251` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.059392, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 2074, "family": "ftv", "name": "ftv38", "optimality_gap": 0.355556}, {"best_known_cost": 1473, "cost": 1975, "family": "ftv", "name": "ftv35", "optimality_gap": 0.340801}, {"best_known_cost": 1286, "cost": 1642, "family": "ftv", "name": "ftv33", "optimality_gap": 0.276827}]

### atsp_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.189005`, synthetic `0.008454`, combined `0.098729`.
- Accepted-epoch count `6`, mean accepted code novelty `0.64691`, and final complexity `0.58`.
- Adaptation efficiency `0.010472` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.189005` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004982, ry=0.093884.
- Panel `synthetic_holdout` mean gap `0.008454` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1705, "family": "ftv", "name": "ftv35", "optimality_gap": 0.157502}]

### atsp_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB ATSP `0.193498`, synthetic `0.009004`, combined `0.101251`.
- Accepted-epoch count `6`, mean accepted code novelty `0.709445`, and final complexity `0.58`.
- Adaptation efficiency `0.008788` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.193498` across 4 instances; family means: ft=0.322375, ftv=0.33478, p=0.004093, ry=0.112744.
- Panel `synthetic_holdout` mean gap `0.009004` across 4 instances; family means: clockwise_ring=0.0, corridor_drift=0.0, hub_spokes=0.033816, wind_clusters=0.002199.
- Worst recent training cases: [{"best_known_cost": 1530, "cost": 1903, "family": "ftv", "name": "ftv38", "optimality_gap": 0.243791}, {"best_known_cost": 1286, "cost": 1537, "family": "ftv", "name": "ftv33", "optimality_gap": 0.195179}, {"best_known_cost": 1473, "cost": 1749, "family": "ftv", "name": "ftv35", "optimality_gap": 0.187373}]

### atsp_failure_replay_compression
- Replay mode: `failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB ATSP `0.255673`, synthetic `0.036251`, combined `0.145962`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.78`.
- Adaptation efficiency `0.0` and archive sizes `{'worst_cases': 4, 'failure_cases': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.255673` across 4 instances; family means: ft=0.426937, ftv=0.398016, p=0.022242, ry=0.175496.
- Panel `synthetic_holdout` mean gap `0.036251` across 4 instances; family means: clockwise_ring=0.085613, corridor_drift=0.0, hub_spokes=0.059392, wind_clusters=0.0.
- Worst recent training cases: [{"best_known_cost": 1473, "cost": 1911, "family": "ftv", "name": "ftv35", "optimality_gap": 0.297352}, {"best_known_cost": 1286, "cost": 1570, "family": "ftv", "name": "ftv33", "optimality_gap": 0.22084}, {"best_known_cost": 1530, "cost": 1857, "family": "ftv", "name": "ftv38", "optimality_gap": 0.213725}]

## Judge Appendix
## Benchmark Suite Analysis: Replay Modes on ATSP

| Condition                    | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Transfer Gap | Code Novelty (mean) | Complexity | Replay Mode           | Notes                                                         |
|------------------------------|-----------------|--------------------|-------------------|---------------------|------------|-----------------------|---------------------------------------------------------------|
| **atsp_no_replay**            | 0.242634        | 0.036251           | 0.139442          | 0.0                 | 0.78       | none                  | Baseline with no replay; lowest transfer performance          |
| **atsp_random_replay**        | **0.189005**    | **0.008454**       | **0.098729**      | 0.64691             | 0.58       | random                | Best overall transfer and optimality gaps; higher code novelty but simpler solutions |
| **atsp_failure_replay**       | 0.193498        | 0.009004           | 0.101251          | 0.709445            | 0.58       | failure               | Slightly worse transfer than random replay, but still improved over no replay with high code novelty |
| **atsp_failure_replay_compression** | 0.255673        | 0.036251           | 0.145962          | 0.0                 | 0.78       | failure + compression  | Worst transfer and optimality gaps; zero code novelty; highest complexity |

---

### Key Interpretations

- **Transfer Evidence (TSPLIB & Synthetic Gaps):**  
  - Random replay condition (`atsp_random_replay`) clearly outperforms no replay and failure-based replay modes in both held-out TSPLIB and synthetic holdout gaps (TSPLIB gap 0.189 vs. 0.243 no replay and ~0.193 failure replay).  
  - Synthetic holdout gaps are lowest under random replay (0.0085), indicating strong generalization to synthetic unseen problem structures.  
  - `atsp_failure_replay_compression` shows degradation in transfer metrics, indicating compression pressure under failure replay negatively impacts generalization.  

- **Code Novelty vs Transfer:**  
  - Random and failure replay show substantial mean code novelty (~0.65-0.71), contrasted with no novelty for no replay and failure replay compression.  
  - Despite higher code novelty under random and failure replay, complexity is lower (0.58 vs 0.78), which suggests replay aids in discovering simpler yet more transferable solutions.  
  - The failure replay compression condition loses code novelty without improving transfer, indicating code novelty reduction corresponds with a transfer decline in this mode.  

- **Replay Mode Distinctions:**  
  - **No Replay:** Baseline performance with moderate complexity and no code novelty.  
  - **Random Replay:** Best transfer metrics and gaps, high code novelty, and simpler policies, showing replay of random past experiences aids transfer.  
  - **Failure Replay:** Slightly weaker transfer than random replay but still better than no replay; highest code novelty.  
  - **Failure Replay + Compression:** Compression pressure results in no code novelty and worst transfer, indicating negative effects from over-compression despite failure replay.  

---

### Summary

- The **random replay** condition achieves the strongest transfer performance on held-out TSPLIB and synthetic ATSP benchmarks, with the smallest optimality gaps by a notable margin.  
- This improvement in transfer occurs despite a reduction in final solution complexity compared to no replay, indicating effective learning of generalizable and simpler strategies.  
- Code novelty is significantly higher under replay conditions, particularly random and failure replay modes, but this novelty correlates with improved or stable transfer—except under compression where novelty and transfer both degrade.  
- Failure replay without compression provides marginally inferior transfer compared to random replay but considerably better than no replay.  
- Compression combined with failure replay negatively impacts both code novelty and transfer, highlighting a tradeoff between compression pressure and generalization.  

Therefore, **random replay mode is identified as the best replay strategy**, improving generalization and optimality gaps over both no replay and failure replay modes, even though code novelty fluctuates. Compression-aware replay reduces code novelty and transfer, arguing against its use in this benchmark setting.
