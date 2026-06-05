# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.55776 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.12722 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1360.19192 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 135.26838 | 1 | 0 | 0 | 0.968411 | 15.15 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 204.11066 | 2 | 0 | 0 | 0.940383 | 15.08 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 141.26554 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.55776.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]
### phase9_closeout_baseline_clarke_wright_savings
- Execution mode: `baseline_clarke_wright_savings`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.064783.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.073766.
- Held-out runtime ms: 76.12722.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.007791.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.108521, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.099285, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.061249, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057708, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.042065, errors=[]
### phase9_closeout_baseline_regret_insertion_local_search
- Execution mode: `baseline_regret_insertion_local_search`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.451049.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.466391.
- Held-out runtime ms: 1360.19192.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.086899.
- Worst held-out instances:
  - X-n275-k28: feasible=True, penalized gap=0.746105, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.650864, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.395235, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.390341, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.149411, errors=[]
### phase9_closeout_direct_generate_plus_one_repair
- Execution mode: `direct_generate_plus_one_repair`.
- Train feasibility rate: 0.0.
- Train penalized gap: 8.958333.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 13.06.
- Held-out runtime ms: 135.26838.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 1.616667.
- Worst held-out instances:
  - X-n275-k28: feasible=False, penalized gap=15.7, errors=["NameError: name 'isinstance' is not defined", 'missing 274 customers']
  - X-n247-k50: feasible=False, penalized gap=14.3, errors=["NameError: name 'isinstance' is not defined", 'missing 246 customers']
  - X-n223-k34: feasible=False, penalized gap=13.1, errors=["NameError: name 'isinstance' is not defined", 'missing 222 customers']
  - X-n190-k8: feasible=False, penalized gap=11.45, errors=["NameError: name 'isinstance' is not defined", 'missing 189 customers']
  - X-n176-k26: feasible=False, penalized gap=10.75, errors=["NameError: name 'isinstance' is not defined", 'missing 175 customers']
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 204.11066.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.0.
- Worst held-out instances:
  - X-n176-k26: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n190-k8: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n223-k34: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n247-k50: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n275-k28: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
### phase9_closeout_replay_solver_evolution
- Execution mode: `replay_solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 141.26554.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                                | Feasibility Rate (Heldout) | Heldout Feasible Gap | Runtime (ms) | Robustness Dispersion | Notes                                                   |
|-----------------------------------------|----------------------------|---------------------|--------------|----------------------|---------------------------------------------------------|
| **phase9_closeout_baseline_nearest_neighbor_constructive** | 100%                       | 0.2734              | 42.6         | 0.0028               | Baseline, fast runtime, moderate gap and robustness     |
| **phase9_closeout_baseline_clarke_wright_savings**         | 100%                       | **0.0738 (Best)**   | 76.1         | 0.0078               | Best heldout gap, baseline, slightly longer runtime     |
| **phase9_closeout_baseline_regret_insertion_local_search** | 100%                       | 0.4664              | 1360.2       | 0.0869               | Slowest, worst gap, baseline                            |
| **phase9_closeout_direct_generate_plus_one_repair**        | 0%                         | 0.0                 | 135.3        | 1.6167               | Zero feasibility, large penalized gap (13.06), high complexity and novelty |
| **phase9_closeout_budget_matched_no_replay**               | 0%                         | 0.0                 | 204.1        | 0.0                  | Zero feasibility, penalized gap 3.0, learned condition, no replay         |
| **phase9_closeout_replay_solver_evolution**                | 100%                       | 0.2734              | 141.3        | 0.0028               | Feasibility matched baseline nearest neighbor, no gap improvement over learned or baseline, replay condition |

---

### Key Points:

- **Baselines performed well** with perfect feasibility and the Clarke-Wright savings baseline achieved the best heldout objective gap (0.0738).
- **Learned conditions did not clearly beat the fixed baselines**:
  - The direct synthesis (direct_generate_plus_one_repair) failed feasibility entirely and had a large objective gap.
  - Budget-matched independent search without replay also had zero feasibility, disqualifying it from outperforming baselines.
- **Replay-aware iterative search condition** (`replay_solver_evolution`) achieved full feasibility and similar gap as nearest neighbor baseline but did **not improve upon baseline or learned no-replay control** in objective gap.
- Replay was **better in feasibility and robustness than budget-matched no replay**, which had zero feasibility, indicating replay improves feasibility but does not yet reduce the objective gap below baselines or no-replay learned conditions under the current setup.

---

### Conclusions

- The **best heldout condition by objective gap was the Clarke-Wright savings baseline**.
- No learned or replay condition clearly outperformed the best fixed baseline.
- **Replay improved feasibility over budget-matched no-replay learned control**, but no gap improvements were observed.
- Learned methods showed higher complexity and novelty but failed to produce feasible solutions or better gaps within the evaluation timeframe.

---

**Overall conservative assessment:** Baseline heuristics currently dominate in the phase-9 CVRP closeout suite by solution quality and feasibility. Replay aids feasibility compared to learned no-replay, but learned methods still lag behind fixed baseline performance in objective gap and robustness.
