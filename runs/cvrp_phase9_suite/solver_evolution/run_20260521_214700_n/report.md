# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.31666 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.4171 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1500.70588 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.171366 | 0.171366 | 1616.67754 | 0.68734 | 13.43 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.31666.
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
- Held-out runtime ms: 77.4171.
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
- Held-out runtime ms: 1500.70588.
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
- Train penalized gap: 0.178906.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.171366.
- Held-out runtime ms: 1616.67754.
- Robustness dispersion across held-out structure families: 0.012712.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.280276, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.240128, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.135099, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.108363, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.092963, errors=[]

## Judge Note
### Phase-9 CVRP Solver-Evolution Suite Summary

| Metric                      | Nearest Neighbor | Clarke-Wright Savings | Regret Insertion LS | Solver Evolution (Evolved)  |
|-----------------------------|------------------|----------------------|--------------------|-----------------------------|
| **Feasibility (heldout)**   | 1.0              | 1.0                  | 1.0                | 1.0                         |
| **Heldout Feasible Gap**    | 0.2734           | **0.0738 (best)**    | 0.4664             | 0.1714                      |
| **Heldout Runtime (ms)**    | 42.3             | 77.4                 | 1500.7             | 1616.7                      |
| **Robustness Dispersion**   | 0.0028           | 0.0078               | 0.0869             | 0.0127                      |
| **Code Novelty / Complexity**| 0 / 0           | 0 / 0                | 0 / 0              | 0.6873 / 13.43              |

---

### Analysis

- **Feasibility:** All solvers achieved perfect feasibility (1.0) on held-out data.
- **Objective gap:** The Clarke-Wright Savings baseline achieved the lowest (best) heldout gap (0.0738), outperforming the evolved solver (0.1714) by a substantial margin.
- **Runtime:** The evolved solver and the Regret Insertion local search are much slower (≈1.6 seconds) compared to simpler baselines (nearest neighbor: 42 ms, Clarke-Wright: 77 ms).
- **Robustness:** The evolved solver shows moderate robustness dispersion (0.0127), better than Regret Insertion but worse than the Clark-Wright baseline.
- **Novelty/complexity:** The solver evolution introduced significantly more complexity and novelty in code compared to baselines (0 novelty, 0 complexity).

---

### Conclusion

The evolved solver maintained feasibility and showed reasonable robustness, but **did not clearly beat the fixed baselines** in objective gap or runtime. Specifically, the Clarke-Wright Savings baseline outperformed the evolved solver in both solution quality and computational efficiency on held-out CVRP instances across multiple structure families.
