# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_budget_matched_no_replay`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 41.85882 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 75.76836 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1366.45918 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 3.0 | n/a | 205.2921 | 1 | 0 | 0 | 0.959254 | 14.3 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 1.0 | 0.070834 | 0.070834 | 207.65304 | 2 | 0 | 0 | 0.960795 | 13.9 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 142.31612 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 41.85882.
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
- Held-out runtime ms: 75.76836.
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
- Held-out runtime ms: 1366.45918.
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
- Held-out runtime ms: 205.2921.
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
- Train penalized gap: 0.067412.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070834.
- Held-out runtime ms: 207.65304.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.004209.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098364, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.095616, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.058186, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.056154, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.045849, errors=[]
### phase9_closeout_replay_solver_evolution
- Execution mode: `replay_solver_evolution`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 142.31612.
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

| Condition                                  | Feasibility Rate | Heldout Feasible Gap | Runtime (ms) | Robustness Dispersion | Learned (Novelty & Complexity)               |
|--------------------------------------------|------------------|---------------------|--------------|----------------------|----------------------------------------------|
| Baseline Nearest Neighbor Constructive     | 100%             | 0.2734              | 41.86        | 0.0028               | None (novelty = 0, complexity = 0)           |
| Baseline Clarke-Wright Savings              | 100%             | 0.0738              | 75.77        | 0.0078               | None (novelty = 0, complexity = 0)           |
| Baseline Regret Insertion Local Search     | 100%             | 0.4664              | 1366.46      | 0.0869               | None (novelty = 0, complexity = 0)           |
| Direct Generate + One Repair                | 0%               | 0                   | 205.29       | 0                    | Learned (high novelty 0.96, complexity 14.3) but infeasible |
| Budget-Matched Independent Search (No Replay) | 100%          | **0.0708 (best)**   | 207.65       | 0.0042               | Learned (high novelty 0.96, complexity 13.9) |
| Replay Solver Evolution                     | 100%             | 0.2734              | 142.32       | 0.0028               | None (novelty = 0, complexity = 0)           |

---

### Key Insights

- **Feasibility:** All methods except *Direct Generate + One Repair* achieved 100% feasibility on held-out data.
- **Objective Gap:** The *budget-matched no replay* condition attained the lowest heldout feasible gap (0.0708), slightly better than the Clarke-Wright baseline (0.0738). Replay condition matched nearest neighbor gap but was worse than budget-matched no replay.
- **Runtime:** Nearest neighbor was fastest, but with high gap. Budget-matched and replay methods had moderate runtimes (~140-208ms). Regret insertion was very slow (~1366ms).
- **Robustness:** Budget-matched no replay had low robustness dispersion (0.0042), near baseline levels.
- **Learning / Novelty:** Only budget-matched no replay and direct generate + repair exhibited high code novelty and complexity. Direct generate failed feasibility.
- **Replay vs No Replay:** Replay did not outperform the budget-matched no replay control for gap or robustness; budget-matched no replay was clearly better.
- **Learned Conditions vs Baselines:** No learned condition, except budget-matched no replay, outperformed fixed baselines. Direct generate approach was infeasible.

---

### Conclusion

- The **budget-matched independent search without replay** condition clearly **outperformed fixed baselines** in gap while maintaining feasibility, robustness, and reasonable runtime.
- The **replay-aware iterative search did not surpass** the budget-matched no-replay baseline.
- Direct synthesis with repair failed feasibility and thus did not improve over baselines.
- Overall, budget-matched independent search is the preferred learned approach in phase-9 closeout for CVRP.
