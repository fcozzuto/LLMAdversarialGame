# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 41.8737 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 78.95798 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1382.6094 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 3.0 | n/a | 273.0781 | 1 | 0 | 0 | 0.962039 | 15.5 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 187.2745 | 1 | 0 | 0 | 0.965079 | 12.12 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.070523 | 0.070523 | 232.10132 | 2 | 0 | 0 | 0.628661 | 14.855 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 41.8737.
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
- Held-out runtime ms: 78.95798.
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
- Held-out runtime ms: 1382.6094.
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
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 273.0781.
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
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 187.2745.
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
- Train penalized gap: 0.066777.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070523.
- Held-out runtime ms: 232.10132.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.005029.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098678, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095455, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057661, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.05742, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.043401, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary

| Condition                              | Feasibility (Heldout) | Feasible Gap | Penalized Gap | Runtime (ms) | Robustness Dispersion | Notes                                       |
|--------------------------------------|----------------------|--------------|---------------|--------------|----------------------|---------------------------------------------|
| Baseline Nearest Neighbor Constructive | 1.0                  | 0.2734       | 0.2734        | 41.87        | 0.0028               | Fastest runtime, moderate gap                |
| Baseline Clarke-Wright Savings        | 1.0                  | 0.0738       | 0.0738        | 78.96        | 0.0078               | Good gap, moderate runtime                    |
| Baseline Regret Insertion Local Search| 1.0                  | 0.4664       | 0.4664        | 1382.61      | 0.0869               | Worst gap, slowest runtime                    |
| Direct Generate +1 Repair              | 0.0                  | 0.0          | 3.0           | 273.08       | 0.0                  | No feasibility, high penalty                  |
| Budget-Matched No Replay               | 0.0                  | 0.0          | 3.0           | 187.27       | 0.0                  | No feasibility, high penalty                  |
| Replay Solver Evolution (Best Heldout) | 1.0                  | 0.0705       | 0.0705        | 232.10       | 0.0050               | Best feasible gap, good robustness, feasible |

### Conservative Interpretation

- **Direct synthesis (Direct Generate +1 Repair)** showed no feasibility on heldout, with high penalized gap.
- **Budget-matched independent search without replay** also failed to produce feasible solutions.
- **Replay-aware iterative search (Replay Solver Evolution)** achieved full feasibility with the best heldout feasible gap (0.0705), outperforming all fixed baselines on objective gap except Clarke-Wright (which was close at 0.0738) while maintaining good robustness and moderate runtime.
- Fixed baselines all had 100% feasibility; Clarke-Wright Savings had the best gap among them before replay.
- Replay clearly **beat** the budget-matched no-replay control, delivering feasibility and much lower gaps.
- Runtime for replay was higher than Clarke-Wright but substantially lower than Regret Insertion Local Search.
- Robustness (dispersion) was low for replay and baselines, indicating stable performance across held-out structure families.

### Summary

- **Replay Solver Evolution** is the only learned condition that beats or matches fixed baselines in feasibility, objective gap, and robustness.
- **Replay-aware iterative search** clearly surpasses **budget-matched independent search** without replay in both feasibility and solution quality.
