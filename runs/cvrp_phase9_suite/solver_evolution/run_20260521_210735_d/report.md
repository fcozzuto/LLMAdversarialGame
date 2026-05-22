# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.75616 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 81.87964 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1463.2087 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.237296 | 0.237296 | 263.83732 | 0.594006 | 17.005 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.75616.
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
- Held-out runtime ms: 81.87964.
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
- Held-out runtime ms: 1463.2087.
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
- Train penalized gap: 0.276613.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.237296.
- Held-out runtime ms: 263.83732.
- Robustness dispersion across held-out structure families: 0.000573.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.387831, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.32015, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.28469, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.108422, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.085385, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver Evolution Suite

| Solver Condition                     | Feasibility Rate | Held-out Feasible Gap | Held-out Runtime (ms) | Robustness Dispersion | Complexity | Notes                          |
|------------------------------------|------------------|----------------------|----------------------|----------------------|------------|--------------------------------|
| Baseline Nearest Neighbor           | 1.0              | 0.2734               | 42.8                 | 0.0028               | 0          | Fastest runtime                |
| Baseline Clarke-Wright Savings      | 1.0              | **0.0738**           | 81.9                 | 0.0078               | 0          | Best gap (objective) among baselines |
| Baseline Regret Insertion LS        | 1.0              | 0.4664               | 1463.2               | 0.0869               | 0          | Longest runtime, worst gap     |
| Solver Evolution (evolved solver)  | 1.0              | 0.2373               | 263.8                 | **0.0006**           | 17.0       | Moderate gap and runtime, best robustness |

### Conservative Evaluation

- **Feasibility:** All solvers maintain perfect feasibility (1.0 rate) on held-out instances.
- **Objective Gap:** The evolved solver's gap (0.2373) is better than nearest neighbor (0.2734) and regret insertion (0.4664) but notably worse than Clarke-Wright savings baseline (0.0738).
- **Runtime:** Evolved solver runs significantly slower than the fastest (nearest neighbor: 42.8 ms vs. 263.8 ms) but much faster than regret insertion (1463.2 ms).
- **Robustness:** Evolved solver shows the lowest robustness dispersion (0.0006), indicating more consistent performance across held-out structural families.
- **Complexity & Novelty:** Evolution introduced higher complexity (mean complexity = 17) and code novelty (~0.59), indicating structural changes.

### Conclusion

The evolved phase-9 solver demonstrates robust and feasible performance with a reasonable trade-off in runtime and complexity. However, it **does not clearly beat** the best fixed baseline (Clarke-Wright savings) in terms of objective gap on held-out structure families, though it offers better robustness and intermediate runtime.
