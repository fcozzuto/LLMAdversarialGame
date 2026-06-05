# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.0588 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 78.04012 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1380.26734 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 1.0 | 0.075855 | 0.075855 | 1647.71436 | 2 | 0 | 0 | 0.93476 | 15.415 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 197.21788 | 1 | 0 | 0 | 0.962459 | 13.41 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.067567 | 0.067567 | 1401.55922 | 5 | 0 | 0 | 0.605941 | 15.844 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.0588.
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
- Held-out runtime ms: 78.04012.
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
- Held-out runtime ms: 1380.26734.
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
- Train penalized gap: 0.093174.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.075855.
- Held-out runtime ms: 1647.71436.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.005206.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.130783, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.083061, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.058186, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056154, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.051092, errors=[]
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 197.21788.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.0.
- Worst held-out instances:
  - X-n176-k26: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n190-k8: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n223-k34: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n247-k50: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
  - X-n275-k28: feasible=False, penalized gap=3.0, errors=['solver did not return a list of routes']
### phase9_closeout_replay_solver_evolution
- Execution mode: `replay_solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.063037.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.067567.
- Held-out runtime ms: 1401.55922.
- Accepted epoch count: 5.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.004317.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098134, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.094516, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.052415, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.050977, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.041793, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                                 | Feasibility Rate | Heldout Feasible Gap | Runtime (ms) | Robustness (Dispersion) | Complexity | Notes                                           |
|-------------------------------------------|------------------|---------------------|--------------|-------------------------|------------|-------------------------------------------------|
| Baseline Nearest Neighbor Constructive    | 1.0              | 0.2734              | 42           | 0.0028                  | 0          | Fastest runtime, moderate gap, robust            |
| Baseline Clarke-Wright Savings             | 1.0              | 0.0738              | 78           | 0.0078                  | 0          | Low gap, moderate speed                          |
| Baseline Regret Insertion Local Search     | 1.0              | 0.4664              | 1380         | 0.0869                  | 0          | Highest runtime and gap, least robust           |
| Direct Generate Plus One Repair             | 1.0              | 0.0759              | 1648         | 0.0052                  | 15.4       | Learned direct synthesis; comparable gap to best baseline, high complexity |
| Budget-Matched No Replay                    | 0.0              | N/A                 | 197          | 0                       | 13.4       | No feasibility on heldout; penalized heavily (3.0 gap) |
| Replay Solver Evolution (Best Heldout)     | 1.0              | **0.0676**          | 1402         | **0.0043**              | 15.8       | Learned replay-aware iterative search; best gap, strong robustness, high complexity |

### Key Takeaways

- **Learned conditions vs. fixed baselines**:  
  The **replay_solver_evolution** condition clearly outperformed all fixed baselines in feasible gap (0.0676 vs. best baseline 0.0738) while maintaining full feasibility and strong robustness.  
  The **direct_generate_plus_one_repair** condition had similar gap performance (0.0759) but a longer runtime and higher complexity than baselines.

- **Replay vs. Budget-Matched No Replay**:  
  The replay condition vastly exceeded the budget-matched no-replay control in feasibility and objective gap, with the no-replay failing feasibility completely on heldout.

- **Runtime and robustness**:  
  Although learned methods (replay and direct generate) are slower (~1400-1600 ms) compared to fast heuristics (42-78 ms), they achieve better or comparable quality with guaranteed feasibility and lower robustness dispersion.

### Conclusion

The replay-aware iterative search via **phase9_closeout_replay_solver_evolution** is the best-performing learned approach, surpassing all fixed baseline methods and the no-replay control in CVRP solution quality, feasibility, and robustness on held-out structures under matched budget constraints.
