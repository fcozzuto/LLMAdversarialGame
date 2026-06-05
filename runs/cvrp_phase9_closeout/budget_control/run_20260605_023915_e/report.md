# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_direct_generate_plus_one_repair`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.36386 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.84996 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1421.75094 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 1.0 | 0.073643 | 0.073643 | 195.1683 | 2 | 0 | 0 | 0.761107 | 12.115 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 198.23672 | 2 | 0 | 0 | 0.961836 | 14.385 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 142.62986 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 43.36386.
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
- Held-out runtime ms: 76.84996.
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
- Held-out runtime ms: 1421.75094.
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
- Train penalized gap: 0.069472.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.073643.
- Held-out runtime ms: 195.1683.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.002874.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.099117, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.096475, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.067432, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057708, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.047481, errors=[]
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 198.23672.
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
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 142.62986.
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
### Phase-9 CVRP Closeout Suite Summary (conservative)

| Aspect                            | Details                                                                                              |
|----------------------------------|-----------------------------------------------------------------------------------------------------|
| **Conditions Evaluated (6 total)** | Baselines: Nearest Neighbor, Clarke-Wright Savings, Regret Insertion Local Search; Learned: Direct Generate + One Repair, Budget-matched No Replay, Replay Solver Evolution |
| **Direct Synthesis**              | *Direct Generate + One Repair* achieved 100% feasibility with a heldout feasible gap of 0.0736, close to Clarke-Wright baseline (0.0738) but with higher runtime (~195 ms vs. 77 ms) and higher solution complexity/novelty |
| **Budget-Matched Independent Search** | *Budget-matched No Replay* failed to produce feasible solutions on heldout data (0% feasibility, penalized gap 3.0), despite longer runtime (~198 ms) |
| **Replay-Aware Iterative Search** | *Replay Solver Evolution* maintained 100% feasibility but with higher feasible gap (0.2734), similar to Nearest Neighbor baseline, showing no improvement |
| **Fixed-Baseline Context**        | Clarke-Wright Savings baseline provided best tradeoff among baselines: 100% feasibility, 0.0738 gap, 77 ms runtime;<br>Regret Insertion had slower runtime (1422 ms) and worse gap (0.4664) |
| **Feasibility**                  | All conditions except Budget-Matched No Replay maintained perfect (100%) feasibility on heldout data |
| **Objective Gap**                | Best gap: Direct Generate + One Repair (0.0736) marginally better than Clarke-Wright (0.0738), both far better than Nearest Neighbor and Regret Insertion |
| **Runtime**                     | Clarke-Wright fastest among good solutions (~77 ms), Direct Generate slower (~195 ms), Regret Insertion slowest (~1422 ms) |
| **Robustness**                  | Low dispersion (~0.0027-0.0078) for best solutions indicating consistent performance; Budget-Matched No Replay had zero feasibility indicating poor robustness |
| **Learned Condition vs Fixed Baselines** | *Direct Generate + One Repair* learned condition closely matched and slightly improved over Clarke-Wright baseline gap, with higher novelty/complexity but no clear dominance|
| **Replay vs Budget-Matched No Replay** | Replay (Solver Evolution) maintained feasibility but did not improve gap over baselines; budget-matched no replay failed feasibility—thus replay clearly beats no-replay budget-matched control in feasibility and robustness |

---

### Summary Conclusion
- The learned *Direct Generate + One Repair* condition matches Clarke-Wright baseline feasibility and objective gap but at increased runtime and complexity; no learned condition clearly outperforms all fixed baselines.
- Replay-aware iterative search maintains feasibility and robustness, outperforming the budget-matched no-replay control which fails feasibility entirely.
- Baselines Clarke-Wright and Nearest Neighbor remain strong context points, with Regret Insertion dominated by longer runtime and worse gaps.
