# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 44.59524 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 82.94436 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1475.02968 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.273435 | 0.273435 | 138.02448 | 0.0 | 0.0 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 44.59524.
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
- Held-out runtime ms: 82.94436.
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
- Held-out runtime ms: 1475.02968.
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
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 138.02448.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Metric                   | Nearest Neighbor (NN)       | Clarke-Wright Savings (CWS)   | Regret Insertion + Local Search (RILS) | Solver Evolution (SE)          |
|--------------------------|-----------------------------|-------------------------------|----------------------------------------|-------------------------------|
| Feasibility Rate         | 1.0                         | 1.0                           | 1.0                                    | 1.0                           |
| Heldout Feasible Gap     | 0.2734                      | **0.0738 (best gap)**         | 0.4664                                 | 0.2734 (same as NN)            |
| Heldout Penalized Gap    | 0.2734                      | 0.0738                        | 0.4664                                 | 0.2734                        |
| Heldout Runtime (ms)     | 44.6 (fastest)              | 82.9                          | 1475.0 (slowest)                       | 138.0                         |
| Robustness Dispersion    | 0.00278                     | 0.00779                       | 0.0869                                | 0.00278                      |
| Train Performance Trends | Matches heldout gap (0.3377)| Slightly better on train (0.0648) | Similar to heldout (0.4510)            | Matches NN (0.3377)            |

#### Interpretation
- **Feasibility:** All solvers including the evolved solver achieve perfect feasibility on train and heldout sets.
- **Objective Gap:** Clarke-Wright Savings dramatically outperforms others with the lowest gap (0.074 vs. ≥0.273). The evolved solver matches the Nearest Neighbor baseline gap (0.273), which is significantly worse than Clarke-Wright.
- **Runtime:** Nearest Neighbor is fastest (~45ms), followed by Clarke-Wright (~83ms), evolved solver at 138ms, and Regret insertion is much slower (~1475ms).
- **Robustness:** The evolved solver has robustness dispersion equal to Nearest Neighbor (0.0028), better than Clarke-Wright and much better than Regret insertion.
- **Evolved Solver Effectiveness:** The evolved solver does **not** improve over the best fixed baseline (Clarke-Wright Savings) in objective gap and is slower than the two fastest baselines. It only matches the performance of the Nearest Neighbor baseline.

### Conclusion
The evolved solver does **not clearly beat** the fixed baselines. Clarke-Wright Savings remains the best overall method in terms of objective gap while retaining perfect feasibility and acceptable runtime. The evolved solver offers no clear advantage in terms of solution quality or efficiency across heldout structure families.
