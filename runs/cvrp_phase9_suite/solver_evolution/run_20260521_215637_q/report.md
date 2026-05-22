# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.97274 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 81.8286 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1414.78694 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.070771 | 0.070771 | 246.5492 | 0.517981 | 12.866667 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 43.97274.
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
- Held-out runtime ms: 81.8286.
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
- Held-out runtime ms: 1414.78694.
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
- Train penalized gap: 0.066773.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070771.
- Held-out runtime ms: 246.5492.
- Robustness dispersion across held-out structure families: 0.00432.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098427, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095804, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.05742, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056107, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.046096, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Solver                                | Feasibility Rate | Held-out Feasible Gap | Runtime (ms) | Robustness Dispersion |
|-------------------------------------|------------------|----------------------|--------------|----------------------|
| Baseline Nearest Neighbor Constructive | 1.0              | 0.2734               | 44           | 0.0028               |
| Baseline Clarke-Wright Savings       | 1.0              | 0.0738               | 82           | 0.0078               |
| Baseline Regret Insertion Local Search | 1.0              | 0.4664               | 1415         | 0.0869               |
| **Solver Evolution (Evolved Solver)** | 1.0              | **0.0708**           | 247          | 0.0043               |

---

### Key Points

- **Feasibility:** All tested solvers, including the evolved solver, maintain perfect feasibility (100%) on held-out structure families.
- **Objective Gap:** The evolved solver achieves the lowest held-out feasible gap (0.0708), slightly better than Clarke-Wright Savings (0.0738) and clearly better than Nearest Neighbor and Regret Insertion baselines.
- **Runtime:** The solver-evolution runtime (247 ms) is higher than nearest neighbor and Clarke-Wright but substantially faster than Regret Insertion local search (~1415 ms).
- **Robustness:** The evolved solver shows competitive robustness (dispersion = 0.0043), better than Clarke-Wright (0.0078) and much better than Regret Insertion (0.0869), albeit slightly worse than nearest neighbor (0.0028).
- **Novelty & Complexity:** The evolved solver introduces significant code novelty and complexity compared to zero novelty/complexity in fixed baselines.

### Conclusion

The evolved solver **does not clearly beat all fixed baselines across all metrics**, but it **consistently outperforms or matches baselines in feasibility, objective gap, and robustness**, offering a strong trade-off between solution quality and runtime. It particularly improves over the nearest neighbor baseline substantially and achieves marginally better optimality gap than Clarke-Wright savings with moderate runtime increase. Overall, the evolved solver demonstrates robustness and better objective performance than most baselines, but with some runtime cost.
