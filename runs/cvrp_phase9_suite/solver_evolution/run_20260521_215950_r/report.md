# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.59546 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 79.42246 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1365.54064 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.077593 | 0.077593 | 519.74634 | 0.540663 | 12.863333 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.59546.
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
- Held-out runtime ms: 79.42246.
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
- Held-out runtime ms: 1365.54064.
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
- Train penalized gap: 0.103492.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.077593.
- Held-out runtime ms: 519.74634.
- Robustness dispersion across held-out structure families: 0.009168.
- Worst held-out instances:
  - X-n275-k28: feasible=True, penalized gap=0.100165, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.088987, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.077024, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.075673, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.046118, errors=[]

## Judge Note
**Summary of phase-9 CVRP Solver-Evolution Suite**

| Aspect              | phase9_baseline_nearest_neighbor_constructive | phase9_baseline_clarke_wright_savings (Best Baseline) | phase9_baseline_regret_insertion_local_search | phase9_solver_evolution (Evolved Solver) |
|---------------------|----------------------------------------------|-----------------------------------------------------|----------------------------------------------|-------------------------------------------|
| **Feasibility**     | 100% heldout & train                           | 100% heldout & train                                | 100% heldout & train                           | 100% heldout & train                      |
| **Objective Gap (Heldout)** | 0.2734                                       | **0.0738**                                          | 0.4664                                        | 0.0776                                    |
| **Runtime (ms, Heldout)**    | 42.6                                          | 79.4                                                | 1365.5                                        | 520.0                                     |
| **Robustness Dispersion**    | 0.0028                                        | 0.0078                                              | 0.0869                                        | 0.0092                                    |
| **Complexity & Novelty**     | 0 (fixed baseline)                             | 0 (fixed baseline)                                  | 0 (fixed baseline)                             | Mean complexity ~12.9, novelty ~0.54       |

### Interpretation

- **Feasibility:** All methods achieve full feasibility on held-out data.
- **Objective Gap:** The solver-evolution approach attains a heldout gap (0.0776) very close to the best baseline Clarke-Wright (0.0738), significantly better than Nearest Neighbor and Regret Insertion.
- **Runtime:** The evolved solver's runtime (~520 ms) is substantially greater than Clarke-Wright (~79 ms) but far less than Regret Insertion (~1365 ms).
- **Robustness:** Evolved solver robustness dispersion (0.0092) is slightly higher than Clarke-Wright (0.0078) but well below Regret Insertion.
- **Complexity & Novelty:** The evolved solver introduces meaningful novelty and complexity, showing effective evolutionary search.

### Conclusion

The evolved solver:

- Maintains perfect feasibility.
- Achieves objective gaps nearly as good as the best baseline Clarke-Wright savings heuristic.
- Runs slower than Clarke-Wright but faster than Regret Insertion.
- Demonstrates stable performance (reasonable robustness).
- Does **not clearly beat** the best fixed baseline (Clarke-Wright) in objective gap or runtime but competes closely while adding novelty and complexity.

Thus, the evolution approach yields a **competitive but not clearly superior** solver compared to fixed baselines on held-out CVRP instances.
