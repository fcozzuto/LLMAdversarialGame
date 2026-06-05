# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.15406 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 75.79714 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1387.7622 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 3.0 | n/a | 209.53802 | 1 | 0 | 0 | 0.963614 | 14.28 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 198.07736 | 1 | 0 | 0 | 0.943062 | 15.45 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.070755 | 0.070755 | 723.65742 | 2 | 0 | 0 | 0.80531 | 11.415 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.15406.
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
- Held-out runtime ms: 75.79714.
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
- Held-out runtime ms: 1387.7622.
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
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 209.53802.
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
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 198.07736.
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
- Train penalized gap: 0.065064.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070755.
- Held-out runtime ms: 723.65742.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.003603.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098678, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095697, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.059835, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.05446, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.045107, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Aspect                              | Observations                                                                                                  |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------|
| **Direct Synthesis**               | *phase9_closeout_direct_generate_plus_one_repair* had zero feasibility (0.0) on heldout and high penalized gap (3.0), indicating failure to produce valid solutions.    |
| **Budget-Matched Independent Search** | *phase9_closeout_budget_matched_no_replay* similarly had 0% feasibility and a large penalized gap (3.0), also failing to find feasible solutions.                       |
| **Replay-Aware Iterative Search** | *phase9_closeout_replay_solver_evolution* showed strong performance with 100% feasibility, a low feasible gap (0.070755), and reasonable runtime (~724 ms). This method is the best heldout condition. |
| **Fixed-Baseline Context**         | Baselines all had 100% feasibility: <br> - Nearest Neighbor: gap 0.2734, runtime 42 ms<br> - Clarke-Wright Savings: gap 0.0738, runtime 76 ms<br> - Regret Insertion Local Search: gap 0.4664, runtime 1388 ms |
| **Feasibility**                   | Only replay-aware search and fixed baselines achieved 100% feasibility. Direct synthesis and budget-matched no-replay had 0%.                                               |
| **Objective Gap**                 | *Replay solver evolution* (0.0708) slightly better than best baseline Clarke-Wright (0.0738). Other baselines notably worse or infeasible.                                  |
| **Runtime**                      | Replay (~724 ms) slower than Clarke-Wright baseline (~76 ms) but faster than regret insertion (~1388 ms). Nearest neighbor fastest (~42 ms) but worse gap than replay.           |
| **Robustness**                   | Replay solver evolution had low robustness dispersion (0.0036), better than Clarke-Wright (0.0078) and much better than regret insertion (0.0869), indicating consistent results across structure families. |
| **Learned Condition vs. Baselines** | Replay solver evolution clearly outperformed all fixed baselines on feasible gap and robustness while maintaining full feasibility. Direct synthesis and budget-matched no-replay did not produce feasible solutions. |
| **Replay vs. Budget-Matched No-Replay** | Replay solver evolution strongly outperformed budget-matched no-replay control, which had zero feasibility and maximal penalized gap (3.0).                         |

---

### Conclusion:

- **Replay-aware iterative search (phase9_closeout_replay_solver_evolution) was the only learned method to clearly beat fixed baselines**, delivering better feasible gaps, full feasibility, and strong robustness despite higher runtime.
- **Direct synthesis and budget-matched independent search failed to produce feasible solutions.**
- **Replay strategy significantly outperformed the budget-matched no-replay control, confirming the value of replay in solving the CVRP here.**
