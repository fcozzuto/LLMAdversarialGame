# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.10264 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 74.4726 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1362.8355 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.238752 | 0.238752 | 1412.60854 | 0.768672 | 12.523333 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.10264.
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
- Held-out runtime ms: 74.4726.
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
- Held-out runtime ms: 1362.8355.
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
- Train penalized gap: 0.246296.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.238752.
- Held-out runtime ms: 1412.60854.
- Robustness dispersion across held-out structure families: 0.001915.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.369131, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.32542, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.262507, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.123734, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.112968, errors=[]

## Judge Note
```markdown
### Summary of Phase-9 CVRP Solver-Evolution Suite

- **Feasibility:**  
  All solvers, including the evolved solver and baselines, achieved a perfect feasibility rate of **1.0** on held-out instances across different structure families.

- **Objective Gap (Held-out Feasible Gap):**  
  - Best baseline: Clarke-Wright Savings with gap **0.0738**  
  - Evolved solver: gap **0.2388**, better than Nearest Neighbor (0.2734) and Regret Insertion (0.4664) but worse than Clarke-Wright  
 
- **Runtime:**  
  - Nearest Neighbor: ~42 ms (fastest)  
  - Clarke-Wright Savings: ~74 ms  
  - Regret Insertion Local Search: ~1363 ms  
  - Evolved solver: ~1413 ms (slowest)  

- **Robustness (Dispersion):**  
  - Evolved solver showed the lowest robustness dispersion at **0.0019**, indicating high solution consistency.  
  - Baselines had higher dispersions: Clarke-Wright (0.0078), Nearest Neighbor (0.0028), Regret Insertion (0.0869).

- **Additional Notes:**  
  - The evolved solver exhibits high code novelty (0.77) and increased complexity (12.5), indicating substantial innovation.  
  - Training metrics align with held-out trends, confirming consistent performance.

### Conclusion

The evolved solver **did not clearly beat** the strongest fixed baseline (Clarke-Wright Savings) in terms of objective gap and runtime. However, it outperformed some baselines (Nearest Neighbor and Regret Insertion) in solution quality while offering the highest robustness (lowest dispersion). The trade-off is substantially longer runtime and higher complexity. Thus, the evolved solver offers a promising but not strictly superior alternative to existing baselines.
```
