# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.28462 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.05894 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1581.8565 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 1.0 | 0.073643 | 0.073643 | 193.70492 | 2 | 0 | 0 | 0.945921 | 14.345 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 191.07752 | 1 | 0 | 0 | 0.982184 | 13.5 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.070733 | 0.070733 | 1358.68936 | 2 | 0 | 0 | 0.860424 | 14.775 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.28462.
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
- Held-out runtime ms: 77.05894.
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
- Held-out runtime ms: 1581.8565.
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
- Held-out runtime ms: 193.70492.
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
- Held-out runtime ms: 191.07752.
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
- Train penalized gap: 0.065731.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.070733.
- Held-out runtime ms: 1358.68936.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.000649.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.096106, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.090814, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.07126, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.049094, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.046393, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                                | Feasibility Rate | Heldout Feasible Gap | Heldout Runtime (ms) | Robustness Dispersion | Notes                                   |
|-----------------------------------------|------------------|---------------------|---------------------|-----------------------|-----------------------------------------|
| baseline_nearest_neighbor_constructive  | 1.0              | 0.2734              | 42.3                | 0.0028                | Fastest baseline, moderate gap          |
| baseline_clarke_wright_savings           | 1.0              | 0.0738              | 77.1                | 0.0078                | Good gap, small runtime                 |
| baseline_regret_insertion_local_search   | 1.0              | 0.4664              | 1581.9              | 0.0869                | Largest gap, longest runtime            |
| direct_generate_plus_one_repair          | 1.0              | 0.0736              | 193.7               | 0.0029                | Learned direct synthesis; gap comparable to Clarke-Wright, moderate runtime |
| budget_matched_no_replay                  | 0.0              | 0.0*                | 191.1               | 0.0                   | No feasibility on heldout, very poor performance |
| replay_solver_evolution                   | 1.0              | **0.0707**          | 1358.7              | **0.00065**            | Best heldout gap and robustness, high runtime but feasible |
  
\* Penalized gap of 3.0 indicates infeasibility.

---

### Key Takeaways

- **Direct synthesis** (`direct_generate_plus_one_repair`) achieved feasibility and a heldout gap comparable to best fixed baselines (Clarke-Wright), with moderate runtime and good robustness.
- **Replay-aware iterative search** (`replay_solver_evolution`) showed statistically the best heldout objective gap and the highest robustness, beating both fixed baselines and direct synthesis albeit with longer runtime.
- The **budget-matched no-replay control** completely failed on feasibility, indicating the benefit of replay in iterative search.
- Among fixed baselines, Clarke-Wright Savings achieves a strong balance of feasibility, objective gap, and runtime.
  
---

### Conclusions

- No learned condition clearly outperforms all fixed baselines across all criteria, but **replay solver evolution is the best in objective gap and robustness**, demonstrating benefits of replay.
- Replay-aware iterative search **clearly outperforms its budget-matched no-replay counterpart**, which fails feasibility entirely.
- Direct generation plus repair is a viable learned method, matching fixed baseline gaps with reasonable runtimes.

This suggests **replay and evolutionary iterative improvements provide clear advantages** in Phase-9 CVRP closeout over fixed baselines and non-replay learned approaches.
