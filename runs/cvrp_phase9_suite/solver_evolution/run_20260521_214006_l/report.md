# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.37244 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.68216 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1450.44374 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.206322 | 0.206322 | 295.0254 | 0.569242 | 15.225 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.37244.
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
- Held-out runtime ms: 76.68216.
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
- Held-out runtime ms: 1450.44374.
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
- Train penalized gap: 0.188377.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.206322.
- Held-out runtime ms: 295.0254.
- Robustness dispersion across held-out structure families: 0.008095.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.369185, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.299109, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.203551, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.096879, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.062885, errors=[]

## Judge Note
### Phase-9 CVRP Solver-Evolution Suite Summary

| Metric                  | Baseline Nearest Neighbor | Baseline Clarke-Wright Savings | Baseline Regret Insertion LS | Evolved Solver (Phase-9)         |
|-------------------------|---------------------------|--------------------------------|------------------------------|---------------------------------|
| **Feasibility Rate (heldout/train)** | 1.0 / 1.0                  | 1.0 / 1.0                       | 1.0 / 1.0                    | 1.0 / 1.0                       |
| **Heldout Objective Gap** | 0.2734                    | **0.0738 (best)**               | 0.4664                       | 0.2063                          |
| **Heldout Penalized Gap** | 0.2734                    | 0.0738                         | 0.4664                       | 0.2063                          |
| **Heldout Runtime (ms)**  | 42.4                      | 76.7                           | 1450.4                       | 295.0                           |
| **Robustness Dispersion** | 0.0028                    | 0.0078                         | 0.0869                       | 0.0081                          |

### Analysis

- **Feasibility:** All methods, including the evolved solver, maintain perfect feasibility (100%) on held-out instances.
- **Objective Gap:** The Clarke-Wright baseline has the lowest heldout gap (0.0738), outperforming the evolved solver (0.2063) and others.
- **Runtime:** Nearest Neighbor is fastest (~42ms), Clarke-Wright moderate (~77ms), evolved solver slower (~295ms), and Regret Insertion LS is much slower (~1450ms).
- **Robustness:** All methods show low robustness dispersion; nearest neighbor is the tightest, evolved solver close to Clarke-Wright.
- **Novelty & Complexity:** The evolved solver exhibits significant code novelty (0.57) and higher complexity (15.2), indicating exploration beyond baselines.

### Conclusion

The evolved solver achieves full feasibility and competitive robustness but **does not clearly beat the best fixed baseline (Clarke-Wright savings) in objective gap or runtime** across held-out CVRP families. It offers a tradeoff of moderate gap and runtime with higher novelty and complexity but without a definitive performance advantage over the strongest fixed heuristic baseline.
