# Phase 9 Closeout Budget-Control CVRP Aggregate Report

## Overview
- Run count: 20.
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Means
| Condition | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity | Robustness Dispersion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 78.329757 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.007791 |
| phase9_closeout_baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.786892 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.002777 |
| phase9_closeout_baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1439.817186 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.086899 |
| phase9_closeout_budget_matched_no_replay | 0.15 | 2.932746 | 0.382746 | 229.661432 | 1.5 | 0.0 | 0.0 | 0.955648 | 13.80875 | 0.10789 |
| phase9_closeout_direct_generate_plus_one_repair | 0.25 | 5.286402 | 0.018402 | 275.998501 | 1.35 | 0.0 | 0.0 | 0.922332 | 14.901 | 0.485845 |
| phase9_closeout_replay_solver_evolution | 1.0 | 0.171114 | 0.171114 | 446.706369 | 1.0 | 0.0 | 0.0 | 0.390074 | 7.344867 | 0.003097 |

## Paired Comparisons
### savings_vs_nearest_neighbor
- Candidate: `phase9_closeout_baseline_clarke_wright_savings` versus reference `phase9_closeout_baseline_nearest_neighbor_constructive` across 20 paired runs.
- Held-out penalized-gap delta: -0.199669 (95% CI -0.199669 to -0.199669).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### insertion_vs_savings
- Candidate: `phase9_closeout_baseline_regret_insertion_local_search` versus reference `phase9_closeout_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 0.392625 (95% CI 0.392625 to 0.392625).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### direct_vs_clarke_wright
- Candidate: `phase9_closeout_direct_generate_plus_one_repair` versus reference `phase9_closeout_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 5.212636 (95% CI 3.054197 to 7.517502).
- Held-out feasibility-rate delta: -0.75 (95% CI -0.9 to -0.55).
### budget_matched_vs_clarke_wright
- Candidate: `phase9_closeout_budget_matched_no_replay` versus reference `phase9_closeout_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 2.85898 (95% CI 2.3404 to 3.456763).
- Held-out feasibility-rate delta: -0.85 (95% CI -1.0 to -0.7).
### replay_vs_clarke_wright
- Candidate: `phase9_closeout_replay_solver_evolution` versus reference `phase9_closeout_baseline_clarke_wright_savings` across 20 paired runs.
- Held-out penalized-gap delta: 0.097348 (95% CI 0.055994 to 0.138558).
- Held-out feasibility-rate delta: 0.0 (95% CI 0.0 to 0.0).
### direct_vs_budget_matched
- Candidate: `phase9_closeout_direct_generate_plus_one_repair` versus reference `phase9_closeout_budget_matched_no_replay` across 20 paired runs.
- Held-out penalized-gap delta: 2.353656 (95% CI 0.113058 to 4.737403).
- Held-out feasibility-rate delta: 0.1 (95% CI -0.15 to 0.35).
### replay_vs_budget_matched
- Candidate: `phase9_closeout_replay_solver_evolution` versus reference `phase9_closeout_budget_matched_no_replay` across 20 paired runs.
- Held-out penalized-gap delta: -2.761632 (95% CI -3.369777 to -2.201586).
- Held-out feasibility-rate delta: 0.85 (95% CI 0.7 to 1.0).
### replay_vs_direct
- Candidate: `phase9_closeout_replay_solver_evolution` versus reference `phase9_closeout_direct_generate_plus_one_repair` across 20 paired runs.
- Held-out penalized-gap delta: -5.115288 (95% CI -7.451608 to -2.946446).
- Held-out feasibility-rate delta: 0.75 (95% CI 0.55 to 0.9).
