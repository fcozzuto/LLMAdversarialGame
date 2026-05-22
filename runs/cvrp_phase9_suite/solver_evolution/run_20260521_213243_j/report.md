# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.18012 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.10186 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1487.586 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.073101 | 0.073101 | 271.58064 | 0.924659 | 14.96 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.18012.
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
- Held-out runtime ms: 77.10186.
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
- Held-out runtime ms: 1487.586.
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
- Train penalized gap: 0.068502.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.073101.
- Held-out runtime ms: 271.58064.
- Robustness dispersion across held-out structure families: 0.009955.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.11394, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.098323, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056154, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.052179, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.044909, errors=[]

## Judge Note
```markdown
### Phase-9 CVRP Solver-Evolution Suite Summary

- **Feasibility:**  
  All solvers, including the evolved solver and baselines, achieved perfect feasibility (100%) on held-out data.

- **Objective Gap (Held-out Feasible Gap):**  
  - Evolved solver: 0.0731  
  - Baseline Clarke-Wright Savings: 0.0738  
  - Baseline Nearest Neighbor: 0.2734  
  - Baseline Regret Insertion Local Search: 0.4664  
  The evolved solver has a slightly better gap than the best baseline (Clarke-Wright), but the difference is marginal.

- **Runtime (Held-out Runtime in ms):**  
  - Evolved solver: ~272 ms  
  - Clarke-Wright: ~77 ms (fastest)  
  - Nearest Neighbor: ~42 ms (fastest overall)  
  - Regret Insertion: ~1488 ms (slowest)  
  The evolved solver runs notably slower than the nearest neighbor and Clarke-Wright baselines but faster than regret insertion.

- **Robustness (Dispersion):**  
  - Evolved solver: 0.00996  
  - Clarke-Wright: 0.00779 (best)  
  - Nearest Neighbor: 0.00278 (lowest)  
  - Regret Insertion: 0.0869 (highest)  
  Robustness of the evolved solver is slightly worse than Clarke-Wright and nearest neighbor but much better than regret insertion.

- **Additional Notes:**  
  The evolved solver exhibits high code novelty (0.92) and additional complexity (≈15 nodes).

### Conclusion  
The phase-9 evolved solver attains feasibility equal to all baselines and a slightly improved objective gap compared to the best baseline (Clarke-Wright savings). However, this improvement in gap is marginal and comes at the cost of higher runtime and slightly reduced robustness. Therefore, the evolved solver **does not clearly and decisively outperform** the fixed baseline methods across held-out families but shows competitive performance with a trade-off in speed and complexity.
```
