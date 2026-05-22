# Phase 9 Aggregate Report

## Overview
- Run count: 20.
- Condition count: 4.
- Best held-out condition: `phase9_baseline_clarke_wright_savings`.

## Condition Means
| Condition | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Mean Novelty | Mean Complexity | Robustness Dispersion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 79.571058 | 0.0 | 0.0 | 0.007791 |
| phase9_baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.021087 | 0.0 | 0.0 | 0.002777 |
| phase9_baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1473.485555 | 0.0 | 0.0 | 0.086899 |
| phase9_solver_evolution | 1.0 | 0.182231 | 0.182231 | 821.705886 | 0.471587 | 10.412833 | 0.005237 |

## Paired Comparisons
### savings_vs_nearest_neighbor
- Candidate: `phase9_baseline_clarke_wright_savings` versus reference `phase9_baseline_nearest_neighbor_constructive` across 20 paired runs.
- Held-out penalized-gap delta: -0.199669 (95% CI -0.199669 to -0.199669).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### insertion_vs_savings
- Candidate: `phase9_baseline_regret_insertion_local_search` versus reference `phase9_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 0.392625 (95% CI 0.392625 to 0.392625).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### evolved_vs_nearest_neighbor
- Candidate: `phase9_solver_evolution` versus reference `phase9_baseline_nearest_neighbor_constructive` across 20 paired runs.
- Held-out penalized-gap delta: -0.091204 (95% CI -0.128136 to -0.055417).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### evolved_vs_clarke_wright
- Candidate: `phase9_solver_evolution` versus reference `phase9_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 0.108465 (95% CI 0.071184 to 0.144731).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### evolved_vs_regret_insertion
- Candidate: `phase9_solver_evolution` versus reference `phase9_baseline_regret_insertion_local_search` across 20 paired runs.
- Held-out penalized-gap delta: -0.28416 (95% CI -0.321769 to -0.247706).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
