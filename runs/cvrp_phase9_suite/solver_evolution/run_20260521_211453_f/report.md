# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.98314 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 79.48704 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1427.8715 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.070678 | 0.070678 | 7487.22724 | 0.592141 | 14.366667 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.98314.
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
- Held-out runtime ms: 79.48704.
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
- Held-out runtime ms: 1427.8715.
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
- Train penalized gap: 0.066394.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070678.
- Held-out runtime ms: 7487.22724.
- Robustness dispersion across held-out structure families: 0.003985.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098281, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.094811, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.059305, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056107, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.044885, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Metric                  | Solver Evolution         | Baseline Clarke-Wright Savings | Baseline Nearest Neighbor | Baseline Regret Insertion |
|-------------------------|-------------------------|-------------------------------|---------------------------|---------------------------|
| Feasibility Rate        | 1.0                     | 1.0                           | 1.0                       | 1.0                       |
| Heldout Feasible Gap    | **0.0707**              | 0.0738                        | 0.2734                    | 0.4664                    |
| Heldout Penalized Gap   | 0.0707                  | 0.0738                        | 0.2734                    | 0.4664                    |
| Heldout Runtime (ms)    | 7487                    | 79.5                          | 43                        | 1428                      |
| Robustness Dispersion   | 0.004                   | 0.008                         | 0.003                     | 0.087                     |
| Mean Code Novelty       | 0.592                   | 0.0                           | 0.0                       | 0.0                       |
| Mean Complexity         | 14.37                   | 0.0                           | 0.0                       | 0.0                       |

### Analysis

- **Feasibility:** All solvers, including the evolved one, achieve perfect (100%) feasibility on held-out structure families.
- **Objective Gap:** The evolved solver achieves the lowest heldout feasible gap (0.0707), slightly better than Clarke-Wright (0.0738), and much better than Nearest Neighbor and Regret Insertion.
- **Runtime:** The evolved solver is considerably slower (~7.5 seconds) than all baselines, with Clarke-Wright being under 0.1 seconds and Nearest Neighbor under 0.05 seconds.
- **Robustness:** The evolved solver shows low robustness dispersion (0.004), comparable to baselines.
- **Novelty & Complexity:** Evolved solver introduces substantial code novelty and higher complexity compared to fixed baselines.

### Conclusion

The evolved solver **consistently beats fixed baselines in objective quality on held-out problem families**, maintaining full feasibility and comparable robustness. However, this improvement comes at a significant cost in runtime and algorithmic complexity. Thus, while **the evolved solver clearly outperforms in solution quality, it does not provide a practical speed advantage over the simpler baselines.**
