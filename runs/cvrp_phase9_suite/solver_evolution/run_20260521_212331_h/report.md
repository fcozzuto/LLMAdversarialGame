# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.52804 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.63892 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1447.12264 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.273435 | 0.273435 | 136.76162 | 0.0 | 0.0 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.52804.
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
- Held-out runtime ms: 77.63892.
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
- Held-out runtime ms: 1447.12264.
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
- Held-out runtime ms: 136.76162.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]

## Judge Note
### Phase-9 CVRP Solver-Evolution Suite Summary

| Metric                   | Baseline Nearest Neighbor | Baseline Clarke-Wright Savings | Baseline Regret Insertion LS | Evolved Solver (Phase 9)    |
|--------------------------|---------------------------|-------------------------------|-----------------------------|-----------------------------|
| **Feasibility Rate**     | 100%                      | 100%                          | 100%                        | 100%                        |
| **Heldout Feasible Gap** | 0.2734                    | **0.0738 (best)**             | 0.4664                      | 0.2734                      |
| **Heldout Penalized Gap** | 0.2734                    | 0.0738                        | 0.4664                      | 0.2734                      |
| **Heldout Runtime (ms)** | 42.5                      | 77.6                          | 1447.1                      | 136.8                       |
| **Robustness Dispersion**| 0.0028                    | 0.0078                        | 0.0869                      | 0.0028                      |

- **Feasibility**: All methods, including the evolved solver, achieved perfect feasibility (100%) on held-out instances.
- **Objective Gap**: The evolved solver's gap (0.2734) matches the baseline nearest neighbor constructive method but is significantly worse than the Clarke-Wright baseline (0.0738), which had the best solution quality.
- **Runtime**: The evolved solver (137 ms) is slower than nearest neighbor (43 ms) and Clarke-Wright (78 ms) but much faster than regret insertion local search (1447 ms).
- **Robustness**: Evolved solver's robustness in held-out performance dispersion is low (0.0028), similar to nearest neighbor and lower than Clarke-Wright and regret insertion.

### Conclusion
The evolved solver **did not clearly beat the fixed baselines**. It matched nearest neighbor in feasibility, gap, and robustness but was outperformed by Clarke-Wright Savings in terms of objective gap and by nearest neighbor in runtime. It was substantially faster and more robust than regret insertion local search but with worse gap quality. Thus, while robust and feasible, the solver evolution did not produce a clearly superior solver over the best fixed baseline (Clarke-Wright Savings).
