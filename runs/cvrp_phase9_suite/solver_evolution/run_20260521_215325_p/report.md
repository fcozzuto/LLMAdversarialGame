# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 44.09786 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 86.00882 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1709.50804 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.109282 | 0.109282 | 1462.0288 | 0.559805 | 13.42 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 44.09786.
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
- Held-out runtime ms: 86.00882.
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
- Held-out runtime ms: 1709.50804.
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
- Train penalized gap: 0.204197.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.109282.
- Held-out runtime ms: 1462.0288.
- Robustness dispersion across held-out structure families: 0.009168.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.161842, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.109343, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.107204, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.087219, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.080801, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Metric                     | Baseline Nearest Neighbor | Baseline Clarke-Wright | Baseline Regret Insertion LS | Evolved Solver (Phase-9)         |
|----------------------------|---------------------------|-----------------------|-----------------------------|---------------------------------|
| **Feasibility Rate**        | 100%                      | 100%                  | 100%                        | 100%                            |
| **Heldout Feasible Gap**    | 0.273                     | **0.074 (Best)**      | 0.466                       | 0.109                           |
| **Heldout Penalized Gap**   | 0.273                     | 0.074                 | 0.466                       | 0.109                           |
| **Heldout Runtime (ms)**    | 44.1                      | 86.0                  | 1709.5                      | 1462.0                          |
| **Robustness Dispersion**   | 0.0028                    | 0.0078                | 0.0869                      | 0.0092                          |

- **Feasibility:** All methods including the evolved solver maintain perfect feasibility (1.0).
- **Objective Gap:** The Clarke-Wright baseline achieves the lowest heldout gaps, outperforming the evolved solver in solution quality by a noticeable margin (0.074 vs. 0.109).
- **Runtime:** The evolved solver is significantly slower than Clarke-Wright and nearest neighbor, though faster than regret insertion local search.
- **Robustness:** The evolved solver shows low robustness dispersion close to Clarke-Wright, indicating consistent performance.
- **Novelty & Complexity:** Evolved solver exhibits high code novelty and moderate complexity, reflecting innovation.

### Conclusion

The evolved solver achieves perfect feasibility and reasonable robustness but does **not clearly outperform** the best fixed baseline (Clarke-Wright) in objective gap or runtime on held-out instances across multiple structure families.
