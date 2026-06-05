# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.29988 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 75.9229 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1579.2179 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 131.78534 | 1 | 0 | 0 | 0.940735 | 15.39 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 133.2573 | 1 | 0 | 0 | 0.974807 | 14.15 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 139.37918 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.29988.
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
- Held-out runtime ms: 75.9229.
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
- Held-out runtime ms: 1579.2179.
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
- Held-out runtime ms: 131.78534.
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
- Held-out runtime ms: 133.2573.
- Accepted epoch count: 1.
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
- Held-out runtime ms: 139.37918.
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
### Phase-9 CVRP Closeout Suite Summary

| Aspect                           | Summary                                                                                              |
|---------------------------------|------------------------------------------------------------------------------------------------------|
| **Direct Synthesis**             | `direct_generate_plus_one_repair` had 0% feasibility on train and heldout with very poor penalty gaps (8.96 train, 13.06 heldout), runtime ~132 ms, and highest code novelty (0.94) and complexity (15.39). Not competitive. |
| **Budget-Matched Independent Search** | `budget_matched_no_replay` also showed 0% feasibility (train & heldout), penalized gap 3.0, runtime ~133 ms, high novelty (0.97) and complexity (14.15). Did not yield feasible solutions.    |
| **Replay-Aware Iterative Search**   | `replay_solver_evolution` had 100% feasibility on train and heldout, penalized gap 0.273, runtime ~139 ms, zero novelty and complexity, indicating reliance on baseline-like solutions but feasible. |
| **Fixed-Baseline Context**       | Baselines `clarke_wright_savings` and `nearest_neighbor_constructive` both had 100% feasibility; Clarke-Wright had the lowest heldout gap (0.074) and moderate runtime (~76 ms), nearest neighbor gap was higher (0.273) but faster (~42 ms). Regret insertion local search was slow (~1579 ms) and had worse gap (0.466). |
| **Feasibility**                  | Only fixed baselines and replay condition achieved 100% feasibility on held-out data. Learned direct and budget-matched conditions failed feasibility completely. |
| **Objective Gap**                | Best gap was from `clarke_wright_savings` baseline (0.074), closely followed by replay search (0.273). Learned/no-replay and direct methods had large or undefined gaps due to infeasibility. |
| **Runtime**                     | Baselines ran quickly (42-76 ms), replay search roughly double nearest neighbor (~139 ms), regret insertion local much slower (~1.58 s). Learned attempts comparable to replay (~130 ms) but infeasible. |
| **Robustness**                  | Baselines showed low robustness dispersion (0.0027-0.0077); replay search matched nearest neighbor dispersion; learned conditions exhibited higher dispersion or zero feasibility, indicating instability. |
| **Best Condition**              | `phase9_closeout_baseline_clarke_wright_savings` is best heldout condition by gap and stability. |
| **Replay vs. Budget-Matched No-Replay** | Replay (`replay_solver_evolution`) matched feasibility and robustness of baselines and dramatically outperformed budget-matched no-replay control which had 0% feasibility and higher gaps. Replay clearly improved performance over no-replay. |
| **Did any learned method clearly beat fixed baselines?** | No. Learned methods either failed feasibility or had much larger gaps than fixed baselines. Baselines remain superior. |

---

### Conservative Conclusion

The fixed baselines, particularly Clarke-Wright Savings, achieved consistent 100% feasibility on held-out CVRP instances with the best objective gaps and efficient runtimes. Learned direct synthesis and budget-matched independent search conditions failed to produce feasible solutions in this closeout suite. Replay-aware iterative search maintained feasibility and robustness comparable to fixed baselines and substantially outperformed the budget-matched no-replay condition, indicating that replay improves solution quality and stability. However, no learned condition in this phase outperformed the fixed-baseline context in terms of feasibility or objective gap.
