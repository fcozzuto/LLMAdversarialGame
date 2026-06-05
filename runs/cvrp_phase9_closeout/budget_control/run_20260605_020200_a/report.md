# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 73.12826 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.9822 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1306.26666 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 3.0 | n/a | 225.9288 | 1 | 0 | 0 | 0.975 | 13.99 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 1.0 | 7.513251 | 7.513251 | 330.62868 | 1 | 0 | 0 | 0.973976 | 13.8 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 142.37906 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 73.12826.
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
- Held-out runtime ms: 77.9822.
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
- Held-out runtime ms: 1306.26666.
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
- Held-out runtime ms: 225.9288.
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
- Train feasibility rate: 1.0.
- Train penalized gap: 6.033943.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 7.513251.
- Held-out runtime ms: 330.62868.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 2.149073.
- Worst held-out instances:
  - X-n190-k8: feasible=True, penalized gap=18.523086, errors=[]
  - X-n275-k28: feasible=True, penalized gap=6.395152, errors=[]
  - X-n223-k34: feasible=True, penalized gap=4.616341, errors=[]
  - X-n176-k26: feasible=True, penalized gap=4.558103, errors=[]
  - X-n247-k50: feasible=True, penalized gap=3.473574, errors=[]
### phase9_closeout_replay_solver_evolution
- Execution mode: `replay_solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 142.37906.
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

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                              | Feasibility | Heldout Feasible Gap | Runtime (ms) | Robustness Dispersion | Notes                                                 |
|--------------------------------------|-------------|---------------------|--------------|----------------------|-------------------------------------------------------|
| Baseline Clarke-Wright Savings       | 100%        | **0.0738**          | 78           | 0.0078               | Best heldout condition overall                         |
| Baseline Nearest Neighbor Constructive | 100%        | 0.2734              | 73           | 0.0028               | Faster, but larger gap than Clarke-Wright             |
| Baseline Regret Insertion Local Search | 100%        | 0.4664              | 1306         | 0.087                | Much slower, worse gap, less robust                    |
| Direct Generate + One Repair          | 0%          | -                   | 226          | 0                    | Zero feasibility, penalized gap=3.0 (failed approach) |
| Budget-Matched No Replay              | 100%        | 7.5133              | 331          | 2.1491               | Feasible but very large gap and low robustness         |
| Replay Solver Evolution               | 100%        | 0.2734              | 142          | 0.0028               | Better than budget-matched no replay; gap equals N.N.  |

### Key Findings

- **Direct synthesis (Direct Generate + One Repair)** failed completely on feasibility and objective.
- **Budget-matched independent search without replay** had good feasibility but showed very poor objective gaps (worst gap of 7.5) and high robustness dispersion, indicating low reliability.
- **Replay-aware iterative search (Replay Solver Evolution)** maintained full feasibility, improved robustness, and significantly better objective gap (0.2734) compared to no-replay control, but did **not** beat Clarke-Wright baseline.
- The **fixed-baseline Clarke-Wright Savings method** clearly outperformed all learned methods in objective gap (0.0738) and matched 100% feasibility.
- The **Nearest Neighbor baseline** was faster and robust but with a larger gap.
- The **Regret Insertion Local Search baseline** was slow, less robust, and had worse objective quality.

### Conclusion

- No learned condition clearly improved upon the best fixed baseline (Clarke-Wright Savings).
- Replay-aware iterative search outperformed the budget-matched no-replay learned approach in gap, robustness, and runtime.
- Fixed baselines remain strong baselines for phase-9 CVRP closeout.
