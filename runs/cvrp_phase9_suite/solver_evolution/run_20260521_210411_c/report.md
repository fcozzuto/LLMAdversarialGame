# Phase 9 CVRP Solver Evolution Report

## Overview
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.15912 | 0.0 | 0.0 |
| phase9_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 85.13068 | 0.0 | 0.0 |
| phase9_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1486.83892 | 0.0 | 0.0 |
| phase9_solver_evolution | solver_evolution | 1.0 | 0.152817 | 0.152817 | 242.93476 | 0.53038 | 15.6575 |

## Condition Notes
### phase9_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 43.15912.
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
- Held-out runtime ms: 85.13068.
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
- Held-out runtime ms: 1486.83892.
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
- Train penalized gap: 0.197631.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.152817.
- Held-out runtime ms: 242.93476.
- Robustness dispersion across held-out structure families: 0.003803.
- Worst held-out instances:
  - X-n190-k8: feasible=True, penalized gap=0.270141, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.176371, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.120137, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.113337, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.0841, errors=[]

## Judge Note
### Summary of Phase-9 CVRP Solver-Evolution Suite

| Metric                    | NN Constructive           | Clarke-Wright Savings  | Regret Insertion LS      | Evolved Solver           |
|---------------------------|--------------------------|-----------------------|-------------------------|--------------------------|
| **Feasibility Rate**      | 1.0 (Heldout & Train)    | 1.0 (Heldout & Train) | 1.0 (Heldout & Train)   | 1.0 (Heldout & Train)    |
| **Objective Gap (Heldout)** | 0.2734                   | **0.0738 (best)**     | 0.4664                  | 0.1528                   |
| **Runtime (Heldout ms)**  | 43.16                    | 85.13                 | 1486.84                 | 242.93                   |
| **Robustness Dispersion** | 0.00278                  | 0.00779               | 0.08690                 | 0.00380                  |
| **Mean Complexity**       | 0.0                      | 0.0                   | 0.0                     | 15.66                    |
| **Code Novelty**          | 0.0                      | 0.0                   | 0.0                     | 0.53                     |

### Conservative Analysis

- **Feasibility:** All methods achieved perfect feasibility (1.0) on held-out instances.
- **Objective Gap:** The Clarke-Wright baseline achieved the lowest objective gap by a clear margin, outperforming the evolved solver (0.0738 vs. 0.1528).
- **Runtime:** Nearest Neighbor was fastest (~43 ms), evolved solver runtime (~243 ms) is moderate, much faster than regret insertion (~1487 ms).
- **Robustness:** The evolved solver showed low robustness dispersion (0.0038), close to nearest neighbor and better than Clarke-Wright and regret insertion.
- **Complexity & Novelty:** Only the evolved solver introduced substantial code novelty and complexity.

### Conclusion

The evolved solver maintained perfect feasibility and showed improved robustness compared to most baselines (except nearest neighbor). However, it did **not clearly beat the best fixed baseline** (Clarke-Wright Savings) in objective gap or runtime, despite introducing novel and more complex strategies. It represents a promising intermediate solution but does not definitively surpass classical heuristics on held-out structural families.
