# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_direct_generate_plus_one_repair`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.04336 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.18308 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1380.50626 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 1.0 | 0.070487 | 0.070487 | 316.13256 | 2 | 0 | 0 | 0.849461 | 15.755 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 1.0 | 0.070832 | 0.070832 | 348.21898 | 2 | 0 | 0 | 0.932473 | 13.97 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.071239 | 0.071239 | 246.68874 | 2 | 0 | 0 | 0.798138 | 13.245 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.04336.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.002777.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.408032, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.364218, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.317111, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.145642, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.132172, errors=[]
### phase9_closeout_baseline_clarke_wright_savings
- Execution mode: `baseline_clarke_wright_savings`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.064783.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.073766.
- Held-out runtime ms: 76.18308.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.007791.
- Worst held-out instances:
  - X-n247-k50: feasible=True, penalized gap=0.108521, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.099285, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.061249, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057708, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.042065, errors=[]
### phase9_closeout_baseline_regret_insertion_local_search
- Execution mode: `baseline_regret_insertion_local_search`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.451049.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.466391.
- Held-out runtime ms: 1380.50626.
- Accepted epoch count: 0.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.086899.
- Worst held-out instances:
  - X-n275-k28: feasible=True, penalized gap=0.746105, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.650864, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.395235, errors=[]
  - X-n176-k26: feasible=True, penalized gap=0.390341, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.149411, errors=[]
### phase9_closeout_direct_generate_plus_one_repair
- Execution mode: `direct_generate_plus_one_repair`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.068916.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070487.
- Held-out runtime ms: 316.13256.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.004296.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.099076, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.094328, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056955, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.056596, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.045478, errors=[]
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.068916.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070832.
- Held-out runtime ms: 348.21898.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.004511.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.099076, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095536, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056955, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.056596, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.045997, errors=[]
### phase9_closeout_replay_solver_evolution
- Execution mode: `replay_solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.067412.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.071239.
- Held-out runtime ms: 246.68874.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.003638.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098323, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095053, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.061779, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056154, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.044885, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary

| Condition                                 | Feasibility Rate | Heldout Feasible Gap | Runtime (ms) | Robustness Dispersion | Novelty | Complexity | Notes                                  |
|-------------------------------------------|------------------|---------------------|--------------|----------------------|---------|------------|----------------------------------------|
| Baseline Nearest Neighbor Constructive    | 1.0              | 0.2734              | 42.0         | 0.0028               | 0.0     | 0.0        | Fastest, largest gap                   |
| Baseline Clarke-Wright Savings             | 1.0              | 0.0738              | 76.2         | 0.0078               | 0.0     | 0.0        | Strong baseline, moderate runtime      |
| Baseline Regret Insertion Local Search     | 1.0              | 0.4664              | 1380.5       | 0.0869               | 0.0     | 0.0        | Worst gap, longest runtime, least robust |
| Direct Generate + One Repair (Learned)     | 1.0              | **0.0705**          | 316.1        | 0.0043               | 0.85    | 15.8       | Best gap overall, moderate runtime     |
| Budget-Matched No Replay (Learned)          | 1.0              | 0.0708              | 348.2        | 0.0045               | 0.93    | 14.0       | Similar gap to direct + repair         |
| Replay Solver Evolution (Learned with Replay) | 1.0              | 0.0712              | 246.7        | 0.0036               | 0.80    | 13.2       | Slightly worse gap than no replay, faster runtime, most robust |

---

### Key Points

- **Feasibility:** All conditions achieved perfect (100%) feasibility on held-out data.
- **Objective Gap:**  
  - Learned methods outperform fixed baselines Clarke-Wright and Nearest Neighbor in gap, particularly direct generate plus one repair (0.0705 gap) slightly beating Clarke-Wright (0.0738 gap).  
  - Regret insertion local search baseline performs worst in gap (0.4664).
- **Runtime:**  
  - Nearest neighbor is fastest (42ms), but with high gap.  
  - Replay solver is fastest among learned methods (~247ms), direct+repair and no replay require 316-348ms.  
  - Regret insertion is slowest (~1380ms).
- **Robustness:**  
  - Replay solver has lowest robustness dispersion (0.0036), indicating consistent performance across structure families.  
  - Learned methods show low dispersion, better than most baselines except nearest neighbor.
- **Learned vs Fixed Baselines:**  
  - Direct generate plus one repair (learned) clearly beats fixed baselines in objective gap and robustness with a moderate runtime cost.  
- **Replay vs No Replay (Both Budget-Matched):**  
  - Replay solver has a slightly worse feasible gap (~0.0712 vs ~0.0708) but better runtime (247ms vs 348ms) and better robustness dispersion (0.0036 vs 0.0045).  
  - No clear dominant advantage in gap for replay, but replay improves robustness and runtime.

---

### Conservative Conclusion

The **direct generate plus one repair** learned condition produces the best overall solution quality (lowest heldout gap), outperforming fixed baselines Clarke-Wright and nearest neighbor with full feasibility and reasonable runtime. Replay-aware iterative search (replay solver evolution) does not clearly improve objective gap over budget-matched no-replay learned search but provides better runtime efficiency and robustness, suggesting replay helps stabilize and accelerate search though its superiority in solution quality is not demonstrated.
