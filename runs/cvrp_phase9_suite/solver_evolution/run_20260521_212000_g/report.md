# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.60538 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 82.9971 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1550.08702 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.268095 | 0.268095 | 153.2471 | 0.762016 | 15.106667 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.60538.
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
- Held-out runtime ms: 82.9971.
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
- Held-out runtime ms: 1550.08702.
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
- Train penalized gap: 0.312474.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.268095.
- Held-out runtime ms: 153.2471.
- Robustness dispersion across held-out structure families: 0.004803.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.400869, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.360349, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.314415, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.141048, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.123794, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite Results

| Metric                    | Nearest Neighbor | Clarke-Wright Savings | Regret Insertion LS | Solver Evolution (Evolved) |
|---------------------------|------------------|----------------------|--------------------|---------------------------|
| **Feasibility Rate**      | 1.0              | 1.0                  | 1.0                | 1.0                       |
| **Held-out Feasible Gap** | 0.2734           | **0.0738 (best)**    | 0.4664             | 0.2681                    |
| **Held-out Runtime (ms)** | 42.6             | 83.0                 | 1550.1             | 153.2                     |
| **Robustness Dispersion** | 0.0028           | 0.0078               | 0.0869             | 0.0048                    |

- **Feasibility:** All solvers, including the evolved one, achieved perfect feasibility (100%) on held-out problems.
- **Objective Gap:** The solver-evolution approach had a feasible gap (~0.268) similar to the nearest neighbor constructive (~0.273), but significantly worse than Clarke-Wright (~0.074), which had the best gap.
- **Runtime:** The evolved solver's runtime (~153 ms) was longer than both nearest neighbor (~43 ms) and Clarke-Wright (~83 ms), but much faster than regret insertion local search (~1550 ms).
- **Robustness:** The evolved solver showed low robustness dispersion (~0.0048), close to nearest neighbor and better than Clarke-Wright and regret insertion LS.

**Conclusion:**  
The evolved solver maintained feasibility and robustness but did **not** clearly outperform the best fixed baseline (Clarke-Wright Savings), which had the lowest objective gap and competitive runtime. Hence, the solver evolution did not decisively beat the fixed baselines across held-out structure families.
