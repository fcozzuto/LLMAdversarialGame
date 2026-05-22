# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.84516 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.5732 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1496.794 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.070818 | 0.070818 | 265.62958 | 0.549316 | 12.085 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.84516.
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
- Held-out runtime ms: 77.5732.
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
- Held-out runtime ms: 1496.794.
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
- Train penalized gap: 0.067409.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070818.
- Held-out runtime ms: 265.62958.
- Robustness dispersion across held-out structure families: 0.004281.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098427, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095804, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.057656, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056107, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.046096, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver Evolution Suite

| Solver Condition                      | Feasibility | Heldout Feasible Gap | Runtime (ms) | Robustness Dispersion | Notes                           |
|-------------------------------------|-------------|---------------------|--------------|----------------------|--------------------------------|
| Baseline Nearest Neighbor Constructive | 100%        | 0.2734              | 42.8         | 0.0028               | Fastest runtime, largest gap   |
| Baseline Clarke-Wright Savings      | 100%        | 0.0738              | 77.6         | 0.0078               | Good gap and runtime           |
| Baseline Regret Insertion + Local Search | 100%        | 0.4664              | 1496.8       | 0.0869               | Worst gap, much slower         |
| **Evolved Solver (phase9_solver_evolution)** | **100%**    | **0.0708**          | 265.6        | 0.0043               | Best gap, moderate runtime, low robustness dispersion, high complexity and novelty |

### Conservative Interpretation

- **Feasibility:** All solvers, including the evolved one, maintain perfect feasibility (100%) on held-out families.
- **Objective Gap:** The evolved solver achieves the lowest feasible gap (0.0708), slightly outperforming Clarke-Wright Savings baseline (0.0738) and significantly better than others.
- **Runtime:** The evolved solver’s runtime (~266 ms) is higher than the two fastest baselines (42.8 ms and 77.6 ms) but much lower than regret insertion local search (~1497 ms).
- **Robustness:** Robustness dispersion of the evolved solver is quite low (0.0043), better than Clarke-Wright (0.0078) and regret insertion (0.0869), and close to nearest neighbor (0.0028).
- **Novelty and Complexity:** The evolved solver introduces substantial code novelty (0.55) and complexity (12.1), indicating more sophisticated heuristics.

### Conclusion

The evolved phase-9 CVRP solver **does not clearly beat all fixed baselines across all axes**; it:

- Slightly improves the objective gap compared to the best baseline (Clarke-Wright Savings).
- Ensures robust feasibility and reasonable runtime (moderate, not the fastest).
- Exhibits higher code novelty and complexity.

It can be considered as a **competitive and robust solver with a slight advantage in solution quality over classical heuristics**, but runtime and complexity trade-offs should be weighed depending on application needs.
