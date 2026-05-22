# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.65276 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.20898 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1438.19396 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.200191 | 0.200191 | 183.02154 | 0.772718 | 12.23 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.65276.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]
### phase9_baseline_clarke_wright_savings
- Execution mode: `baseline_clarke_wright_savings`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.064783.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.073766.
- Held-out runtime ms: 77.20898.
- Robustness dispersion across held-out structure families: 0.007791.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.108521, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.099285, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.061249, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057708, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.042065, errors=[]
### phase9_baseline_regret_insertion_local_search
- Execution mode: `baseline_regret_insertion_local_search`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.451049.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.466391.
- Held-out runtime ms: 1438.19396.
- Robustness dispersion across held-out structure families: 0.086899.
- Worst held-out instances:
  - X-n275-k28: feasible=True, penalized gap=0.746105, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.650864, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.395235, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.390341, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.149411, errors=[]
### phase9_solver_evolution
- Execution mode: `solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.216219.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.200191.
- Held-out runtime ms: 183.02154.
- Robustness dispersion across held-out structure families: 0.010162.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.268391, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.253555, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.230653, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.140754, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.107602, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Metric                   | Baseline Nearest Neighbor | Baseline Clarke-Wright Savings | Baseline Regret Insertion LS | Evolved Solver           |
|--------------------------|---------------------------|-------------------------------|-----------------------------|--------------------------|
| **Feasibility Rate**     | 1.0                       | 1.0                           | 1.0                         | 1.0                      |
| **Heldout Feasible Gap** | 0.2734                    | **0.0738 (best)**             | 0.4664                      | 0.2002                   |
| **Heldout Runtime (ms)** | 42.65                     | 77.21                         | 1438.19                     | 183.02                   |
| **Robustness Dispersion**| 0.00278                   | 0.00779                       | 0.0869                      | 0.01016                  |

- **Feasibility:** All solvers, including the evolved one, achieved perfect feasibility (1.0) on held-out instances.
- **Objective Gap:** The evolved solver’s heldout gap (0.2002) is better than nearest neighbor (0.2734) and regret insertion local search (0.4664), but clearly worse than Clarke-Wright savings (0.0738).
- **Runtime:** The evolved solver is slower than both nearest neighbor (42.7 ms) and Clarke-Wright (77.2 ms), but significantly faster than regret insertion local search (1438 ms).
- **Robustness:** The evolved solver’s robustness dispersion (0.0102) is higher than nearest neighbor and Clarke-Wright but much lower than regret insertion local search.

### Conclusion

While the evolved solver shows improvement over some baselines (nearest neighbor and regret insertion local search) in objective gap and maintains feasibility, it does **not** clearly outperform the best fixed baseline (Clarke-Wright savings), which remains superior in solution quality and runtime. The evolved solver offers a moderate tradeoff between runtime and solution gap but does not dominate the fixed baselines across all metrics.
