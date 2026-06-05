# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.07024 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 74.9565 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1518.02508 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 132.75412 | 1 | 0 | 0 | 0.94602 | 15.45 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 214.52828 | 1 | 0 | 0 | 0.948737 | 13.93 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.065689 | 0.065689 | 358.0752 | 1 | 0 | 0 | 0.884983 | 15.25 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.07024.
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
- Held-out runtime ms: 74.9565.
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
- Held-out runtime ms: 1518.02508.
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
- Train penalized gap: 8.958333.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 13.06.
- Held-out runtime ms: 132.75412.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 1.616667.
- Worst held-out instances:
  - X-n275-k28: feasible=False, penalized gap=15.7, errors=["NameError: name 'isinstance' is not defined", 'missing 274 customers']
  - X-n247-k50: feasible=False, penalized gap=14.3, errors=["NameError: name 'isinstance' is not defined", 'missing 246 customers']
  - X-n223-k34: feasible=False, penalized gap=13.1, errors=["NameError: name 'isinstance' is not defined", 'missing 222 customers']
  - X-n190-k8: feasible=False, penalized gap=11.45, errors=["NameError: name 'isinstance' is not defined", 'missing 189 customers']
  - X-n176-k26: feasible=False, penalized gap=10.75, errors=["NameError: name 'isinstance' is not defined", 'missing 175 customers']
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 214.52828.
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
- Train penalized gap: 0.066626.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.065689.
- Held-out runtime ms: 358.0752.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.001023.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.096733, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.077051, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.056596, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.051871, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.046195, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                             | Feasibility (Heldout) | Objective Gap (Heldout) | Runtime (ms) | Robustness Dispersion | Learned vs. Fixed Baseline | Replay vs. Budget-Matched No-Replay |
|-------------------------------------|----------------------|------------------------|--------------|----------------------|----------------------------|------------------------------------|
| Baseline Nearest Neighbor Constructive | 100%                 | 0.2734                 | 42           | 0.0028               | Baseline                   | N/A                                |
| Baseline Clarke-Wright Savings        | 100%                 | 0.0738                 | 75           | 0.0078               | Baseline                   | N/A                                |
| Baseline Regret Insertion Local Search | 100%                 | 0.4664                 | 1518         | 0.0869               | Baseline                   | N/A                                |
| Direct Generate + One Repair          | 0%                   | N/A (13.06 penalized)  | 133          | 1.617                | No (failed feasibility)    | N/A                                |
| Budget-Matched No Replay              | 0%                   | N/A (3.0 penalized)    | 215          | 0                    | No (failed feasibility)    | Control for replay                 |
| Replay Solver Evolution               | 100%                 | 0.0657                 | 358          | 0.0010               | Yes (beat baseline gaps except regret) | Yes (beat budget-matched no replay) |

#### Key Points:
- **Direct synthesis ("direct_generate_plus_one_repair") failed feasibility (0% feasibility), with very high penalized gap and high complexity/novelty.**
- **Fixed baseline constructive heuristics (nearest neighbor, Clarke-Wright, regret insertion local search) all had 100% feasibility. Clarke-Wright had the best gap (0.0738), albeit slower than nearest neighbor. Regret insertion was slowest and worst gap.**
- **Budget-matched independent search without replay had 0% feasibility, penalized gap of 3.0, runtime 215ms, complexity/novelty high, indicating it failed to produce feasible solutions within budget.**
- **Replay-aware iterative search ("replay_solver_evolution") fully feasible (100%), best objective gap (0.0657) better than Clarke-Wright baseline, and reasonable runtime (358 ms). Robustness (dispersion) minimal, complexity similar to direct and budget-matched no replay.**
- **Replay-aware search clearly outperformed fixed baselines in objective gap except regret insertion local search (which was much slower and worse gap).**
- **Replay-aware search also clearly outperformed the budget-matched no-replay control in feasibility, objective gap, and robustness.**

### Conclusion:
- The **only learned method that clearly beat fixed baselines was the replay-aware iterative search**.
- **Replay-aware iterative search outperformed the budget-matched independent search without replay.**
- Direct synthesis methods failed to deliver feasible solutions.
- The replay approach showed superior feasibility, better objective gap, competitive runtime, and superior robustness on held-out structure families.

---

*Duration of evaluation: ~8 minutes (464.4 seconds)*
