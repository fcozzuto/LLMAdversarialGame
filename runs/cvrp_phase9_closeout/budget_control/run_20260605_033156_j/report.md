# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.50932 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 75.74116 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1334.9248 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 135.71366 | 1 | 0 | 0 | 0.964856 | 13.74 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 273.08588 | 2 | 0 | 0 | 0.945758 | 13.085 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 139.52028 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.50932.
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
- Held-out runtime ms: 75.74116.
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
- Held-out runtime ms: 1334.9248.
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
- Held-out runtime ms: 135.71366.
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
- Held-out runtime ms: 273.08588.
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
- Held-out runtime ms: 139.52028.
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

| Aspect                        | Summary                                                                                           |
|-------------------------------|---------------------------------------------------------------------------------------------------|
| **Direct Synthesis**           | "direct_generate_plus_one_repair" showed 0% feasibility and very high penalized gap (~13.06), with high complexity (13.74) and low robustness. |
| **Budget-Matched Independent Search** | "budget_matched_no_replay" also had 0% feasibility and moderate penalized gap (3.0) at runtime 273 ms, complexity 13.1, no robustness dispersion (0). |
| **Replay-Aware Iterative Search** | "replay_solver_evolution" achieved 100% feasibility but had heldout gap of 0.273, similar to lowest baseline gaps but no superiority in objective gap. Runtime 140 ms, zero complexity/novelty, low robustness dispersion. |
| **Fixed-Baseline Context**     | Baselines tested: nearest_neighbor, clarke_wright_savings, and regret_insertion_local_search. Clarke-Wright savings had best heldout gap (0.0738), 100% feasibility, moderate runtime (76 ms), and low robustness dispersion. Other baselines had higher gaps or runtimes. |
| **Feasibility**               | Only fixed baselines and replay-based search guaranteed 100% feasibility on heldout data; learned or budget-matched no-replay failed feasibility completely. |
| **Objective Gap**              | Clarke-Wright baseline had the lowest feasible gap (0.0738), outperforming learned and replay variants. Replay (0.2734) matched nearest_neighbor baseline gap, worse than Clarke-Wright. |
| **Runtime**                   | Baselines ranged from ~43 ms (nearest_neighbor) to 1335 ms (regret_insertion). Replay at 140 ms was faster than regret local search but slower than Clarke-Wright. Learned methods were slower or infeasible. |
| **Robustness Across Held-Out Families** | Clarke-Wright and nearest_neighbor showed low robustness dispersion (~0.003-0.008). Replay solver had similar robustness. Learned methods exhibited high complexity and novelty but low robustness. |
| **Learned Conditions vs. Fixed Baselines** | None of the learned or replay-aware conditions clearly outperformed the best fixed baseline (Clarke-Wright savings) on objective gap or feasibility. Learned methods failed feasibility on held-out instances. |
| **Replay vs. Budget-Matched No-Replay Control** | Replay (100% feasibility, gap 0.273) outperformed budget-matched no-replay (0% feasibility, gap undefined) in feasibility and objective reliability, but neither surpassed baselines. |

---

**Overall conclusion:**  
The fixed Clarke-Wright savings baseline remains the best performing method in the phase-9 CVRP closeout suite on feasibility, objective gap, runtime, and robustness. Replay-aware iterative search improved feasibility relative to budget-matched no-replay learned search but did not beat the best fixed baseline. Direct synthesis and budget-matched independent searches failed to produce feasible solutions reliably.
