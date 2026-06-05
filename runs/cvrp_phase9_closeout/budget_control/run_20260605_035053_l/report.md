# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_baseline_clarke_wright_savings`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 42.12758 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 76.89182 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1910.16218 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 1.0 | 0.074405 | 0.074405 | 255.19108 | 2 | 0 | 0 | 0.937227 | 14.955 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 248.82992 | 2 | 0 | 0 | 0.961677 | 14.14 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.273435 | 0.273435 | 142.37444 | 0 | 0 | 0 | 0.0 | 0.0 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 42.12758.
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
- Held-out runtime ms: 76.89182.
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
- Held-out runtime ms: 1910.16218.
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
- Train penalized gap: 0.079232.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.074405.
- Held-out runtime ms: 255.19108.
- Accepted epoch count: 2.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.001657.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.099452, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.09508, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.067432, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.057708, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.052353, errors=[]
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 248.82992.
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
- Held-out runtime ms: 142.37444.
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

| Aspect                       | Summary                                                                                       |
|------------------------------|-----------------------------------------------------------------------------------------------|
| **Direct Synthesis**          | `phase9_closeout_direct_generate_plus_one_repair` achieved 100% feasibility with a 0.0744 feasible gap on heldout, close to best baseline, moderate runtime (~255 ms), and high novelty (~0.94). Complexity moderate (≈15). |
| **Budget-Matched Independent Search** | `phase9_closeout_budget_matched_no_replay` failed feasibility completely (0%), penalized gap fixed at 3.0, despite similar runtime to direct synthesis (~249 ms), high novelty (0.96), moderate complexity (~14). No useful solutions found. |
| **Replay-Aware Iterative Search** | `phase9_closeout_replay_solver_evolution` had full feasibility (100%) but a large feasible gap (0.273), runtime ~142 ms, zero novelty and complexity, effectively matching nearest neighbor baseline in quality but worse than Clarke-Wright. Demonstrated no gap improvement vs no-replay.  |
| **Fixed-Baseline Context**    | Baselines showed consistent full feasibility. Clarke-Wright savings baseline was best with lowest heldout feasible gap (0.0738) but longer runtime (~77 ms). Nearest neighbor had higher gap (0.273), faster runtime (~42 ms), and regret insertion local search was slow (~1910 ms) with worst gaps (~0.466). |
| **Feasibility**               | All except budget-matched no-replay found 100% feasible solutions on heldout.                  |
| **Objective Gap**             | Best gap: Clarke-Wright (0.0738), direct synthesis close (0.0744), others notably worse.       |
| **Runtime**                   | Nearest neighbor fastest (~42 ms), Clarke-Wright (~77 ms), replay solver (~142 ms), direct synthesis (~255 ms), budget-matched no-replay (~249 ms), regret insertion very slow (~1910 ms). |
| **Robustness** (Dispersion)   | Low dispersion (best robustness) in direct synthesis (≈0.0017), slightly higher for Clarke-Wright (≈0.0078) and regret insertion. |
| **Learned Condition vs Fixed Baselines** | No learned approach clearly outperformed the best fixed baseline (Clarke-Wright). Direct generate + repair matched gap closely but was slower. |
| **Replay vs No-Replay**       | Replay-aware search improved feasibility and reduced gap compared to no-replay search (which failed feasibility), but did not reach best baseline quality or outperform direct synthesis. |

---

### Key Conclusions

- Clarke-Wright savings baseline remains top performer in objective gap and feasibility with moderate runtime.
- Direct generate plus one repair learned method closely matches Clarke-Wright’s objective gap with perfect feasibility, albeit slower and more complex.
- Budget-matched no-replay search failed feasibility and produced invalid solutions.
- Replay-aware solver improves over no-replay in feasibility and quality but does not exceed fixed baseline or direct synthesis.
- No learned or replay method clearly beats Clarke-Wright baseline in gap or combined metrics under this evaluation.
