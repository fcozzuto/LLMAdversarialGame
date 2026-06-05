# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 41.81978 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.36324 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1396.33112 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 3.0 | n/a | 232.65356 | 1 | 0 | 0 | 0.948791 | 16.25 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 302.03618 | 1 | 0 | 0 | 0.96266 | 14.92 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.069352 | 0.069352 | 2193.00564 | 3 | 0 | 0 | 0.553475 | 15.723333 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 41.81978.
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
- Held-out runtime ms: 76.36324.
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
- Held-out runtime ms: 1396.33112.
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
- Held-out runtime ms: 232.65356.
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
- Held-out runtime ms: 302.03618.
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
- Train penalized gap: 0.061781.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.069352.
- Held-out runtime ms: 2193.00564.
- Accepted epoch count: 3.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.002918.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.097465, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.093363, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.058952, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.052342, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.044637, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Aspect                            | Summary                                                                                                 |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| **Direct synthesis**              | `direct_generate_plus_one_repair` failed feasibility (0% heldout feasible rate) and had very high gaps. |
| **Budget-matched independent search (no replay)** | `budget_matched_no_replay` also failed feasibility (0%) with high penalized gap (3.0).                    |
| **Replay-aware iterative search**| `replay_solver_evolution` achieved perfect feasibility (100%) with the best heldout feasible gap (0.0694), beating baselines in gap but had highest runtime (2193 ms). |
| **Fixed-baseline context**        | Baselines (nearest neighbor, Clarke-Wright, regret insertion) all had 100% feasibility; Clarke-Wright had best gap (0.0738), runtime from 42 to 1396 ms, regret insertion most expensive and worst gap. |
| **Feasibility**                  | Learned conditions without replay had 0% feasibility; with replay achieved 100%. Baselines 100%.        |
| **Objective gap**                | Replay solver evolution gap (0.0694) slightly better than best baseline Clarke-Wright (0.0738).          |
| **Runtime**                     | Baselines fastest nearest neighbor (42 ms) and Clarke-Wright (76 ms); replay approach was slowest (2193 ms). |
| **Robustness across held-out families** | Replay approach had low robustness dispersion (0.0029) similar to baselines, indicating stable performance.    |
| **Learned vs fixed baselines**  | No learned method without replay beat fixed baselines. Replay-aware iterative search slightly outperformed the best fixed baseline gap-wise. |
| **Replay vs no replay control** | Replay clearly outperformed budget-matched no-replay in feasibility and gap.                            |

---

### Conclusions

- The **best heldout condition** was the **replay_solver_evolution**, achieving perfect feasibility and better gap than fixed baselines.
- **Replay mechanism provided a significant advantage** over budget-matched no-replay learning control.
- Learned methods without replay failed to generate feasible solutions.
- Baselines remain competitive in runtime but are slightly worse in gap compared to replay-based learning.
- The replay-aware iterative approach trades off runtime for improved solution quality and robustness.
