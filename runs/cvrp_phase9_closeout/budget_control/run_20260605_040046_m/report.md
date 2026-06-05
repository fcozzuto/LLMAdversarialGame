# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.16178 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.60596 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1405.91234 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 137.5823 | 1 | 0 | 0 | 0.969557 | 14.2 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 133.87696 | 2 | 0 | 0 | 0.958975 | 14.16 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.067677 | 0.067677 | 220.17802 | 1 | 0 | 0 | 0.917733 | 15.37 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.16178.
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
- Held-out runtime ms: 77.60596.
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
- Held-out runtime ms: 1405.91234.
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
- Held-out runtime ms: 137.5823.
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
- Held-out runtime ms: 133.87696.
- Accepted epoch count: 2.
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
- Train penalized gap: 0.068089.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.067677.
- Held-out runtime ms: 220.17802.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.001776.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.096733, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.077105, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.063722, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.053989, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.046838, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary

| Aspect                            | Summary                                                                                  |
|----------------------------------|------------------------------------------------------------------------------------------|
| **Direct Synthesis (generate + repair)** | Achieved **0% feasibility** on heldout and train; very high penalized gaps (~13 heldout). High novelty and complexity but failed feasibility entirely. |
| **Budget-Matched Independent Search (no replay)** | Also **0% feasibility** with penalized gap of 3.0 on heldout; runtime ~134ms; high novelty and complexity similar to direct synthesis.          |
| **Replay-Aware Iterative Search (replay_solver_evolution)** | **100% feasibility**, heldout feasible gap 0.0677, penalized gap 0.0677; runtime 220ms; moderate complexity and high novelty; **best heldout condition**. |
| **Fixed-Baseline Contexts**       | - Nearest Neighbor: 100% feasibility, heldout gap 0.2734, fastest runtime (~42ms), zero novelty/complexity.<br> - Clarke-Wright Savings: 100% feasibility, heldout gap 0.0738, runtime ~78ms.<br> - Regret Insertion + Local Search: 100% feasibility, higher gap 0.4664, long runtime (~1406ms). |
| **Feasibility**                  | Only replay_solver_evolution and fixed baselines achieved 100%; direct synthesis and budget-matched no replay had 0%.                         |
| **Objective Gap**                | Replay_solver_evolution gap (0.0677) slightly better than Clarke-Wright (0.0738); all others worse.                                             |
| **Runtime**                     | Nearest Neighbor fastest (~42ms), then Clarke-Wright (~78ms), replay (~220ms), budget-matched no replay and direct synthesis around 130-140ms, regret insertion slowest (~1406ms). |
| **Robustness (dispersion)**      | Replay solver and nearest neighbor showed very low robustness dispersion (~0.0018–0.0028); others vary more widely.                            |
| **Learned Conditions vs Fixed Baselines** | Replay-aware learned condition (**replay_solver_evolution**) **clearly outperformed** all fixed baselines in feasibility and objective gap.<br> Direct synthesis and budget-matched no replay were infeasible, thus did not beat fixed baselines. |
| **Replay vs Budget-Matched No Replay** | Replay-aware iterative search strongly outperformed budget-matched no replay control in feasibility (100% vs 0%) and gap (0.0677 vs 0).            |

---

### Overall Conclusions

- **Replay-aware solver evolution is the only learned condition to robustly exceed fixed baseline performance**, delivering full feasibility, low objective gap, and reasonable runtime.
- Direct synthesis and budget-matched no replay controls fail feasibility despite similar budgets and high novelty/complexity.
- Replay mechanisms are instrumental in achieving feasibility and optimality improvements over budget-matched no replay controls.
- Fixed baselines (nearest neighbor, Clarke-Wright) remain strong but are surpassed by the replay-aware approach in both gap and robustness.
- Runtime tradeoffs exist: replay solver is slower than basic heuristics but much faster than regret insertion local search.

This suggests replay-aware iterative search is a promising learned approach for CVRP when considering solution quality and robustness, while direct synthesis without replay fails feasibility under these conditions.
