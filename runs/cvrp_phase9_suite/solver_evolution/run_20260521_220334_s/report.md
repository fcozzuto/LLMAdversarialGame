# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.5223 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 79.42908 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1471.5379 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.263478 | 0.263478 | 160.56024 | 0.657136 | 12.115 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 43.5223.
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
- Held-out runtime ms: 79.42908.
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
- Held-out runtime ms: 1471.5379.
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
- Train penalized gap: 0.297436.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.263478.
- Held-out runtime ms: 160.56024.
- Robustness dispersion across held-out structure families: 0.003514.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.400708, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.353572, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.307367, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.137927, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.117816, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver Evolution Suite

| Condition                              | Feasibility Rate | Held-out Feasible Gap | Held-out Runtime (ms) | Robustness Dispersion | Notes on Objective & Runtime                              |
|--------------------------------------|------------------|----------------------|----------------------|----------------------|----------------------------------------------------------|
| Baseline Nearest Neighbor Constructive | 100%             | 0.2734               | 43.5                 | 0.0028               | Fastest runtime, moderate gap                            |
| Baseline Clarke-Wright Savings        | 100%             | **0.0738**           | 79.4                 | 0.0078               | Best objective gap, moderate runtime                      |
| Baseline Regret Insertion + Local Search | 100%         | 0.4664               | 1471.5               | 0.0869               | Worst objective gap, slowest runtime                      |
| Evolved Solver                       | 100%             | 0.2635               | 160.6                | 0.0035               | Moderate gap and runtime, good robustness, code novelty  |

### Feasibility
- All conditions, including the evolved solver, achieved perfect feasibility (100%) on held-out instances.

### Objective Gap
- Clarke-Wright Savings baseline clearly outperforms all others with the lowest feasible gap (0.0738).
- The evolved solver has a feasible gap (0.2635) slightly better than Nearest Neighbor (0.2734) but much better than Regret Insertion (0.4664).
- No clear improvement over the best baseline (Clarke-Wright).

### Runtime
- Nearest Neighbor is fastest (~43 ms), Clarke-Wright is moderate (~79 ms).
- The evolved solver runs slower (~161 ms) than these baselines but much faster than Regret Insertion (~1472 ms).

### Robustness
- The evolved solver exhibits low robustness dispersion (0.0035), indicating consistent performance.
- Clarke-Wright has slightly higher dispersion (0.0078).
- Regret Insertion shows high dispersion (0.0869), indicating less consistent results.

### Code Novelty and Complexity
- Evolved solver shows substantial code novelty (0.657) and some complexity (12.1), indicating significant changes compared to fixed baselines with zero novelty.

### Conclusion
- The evolved solver **did not clearly beat** the best baseline (Clarke-Wright Savings) in terms of objective gap or runtime.
- It demonstrated competitive feasibility and robustness with moderate objective gap and runtime, exceeding Nearest Neighbor performance for objective but not surpassing Clarke-Wright.
- Overall, the evolved solver offers a balanced trade-off but not a definitive improvement over the strongest fixed baseline.
