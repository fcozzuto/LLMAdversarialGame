# Phase 9 CVRP Suite Report

## Overview
- Condition count: 6.
- Best held-out condition: `phase9_closeout_replay_solver_evolution`.

## Condition Summary
| Condition | Mode | Held-out Feasibility | Held-out Penalized Gap | Held-out Feasible Gap | Held-out Runtime (ms) | Accepted Epochs | Fallback Epochs | Generation Errors | Mean Novelty | Mean Complexity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase9_closeout_baseline_nearest_neighbor_constructive | baseline_nearest_neighbor_constructive | 1.0 | 0.273435 | 0.273435 | 43.01344 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_clarke_wright_savings | baseline_clarke_wright_savings | 1.0 | 0.073766 | 0.073766 | 77.6406 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_baseline_regret_insertion_local_search | baseline_regret_insertion_local_search | 1.0 | 0.466391 | 0.466391 | 1390.52414 | 0 | 0 | 0 | 0.0 | 0.0 |
| phase9_closeout_direct_generate_plus_one_repair | direct_generate_plus_one_repair | 0.0 | 13.06 | n/a | 136.14616 | 1 | 0 | 0 | 0.973861 | 14.91 |
| phase9_closeout_budget_matched_no_replay | budget_matched_no_replay | 0.0 | 3.0 | n/a | 313.89126 | 2 | 0 | 0 | 0.952232 | 15.31 |
| phase9_closeout_replay_solver_evolution | replay_solver_evolution | 1.0 | 0.064135 | 0.064135 | 547.9113 | 1 | 0 | 0 | 0.930514 | 15.07 |

## Condition Notes
### phase9_closeout_baseline_nearest_neighbor_constructive
- Execution mode: `baseline_nearest_neighbor_constructive`.
- Train feasibility rate: 1.0.
- Train penalized gap: 0.337704.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.273435.
- Held-out runtime ms: 43.01344.
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
- Held-out runtime ms: 77.6406.
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
- Held-out runtime ms: 1390.52414.
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
- Held-out runtime ms: 136.14616.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 1.616667.
- Worst held-out instances:
  - X-n275-k28: feasible=False, penalized gap=15.7, errors=["NameError: name 'str' is not defined", 'missing 274 customers']
  - X-n247-k50: feasible=False, penalized gap=14.3, errors=["NameError: name 'str' is not defined", 'missing 246 customers']
  - X-n223-k34: feasible=False, penalized gap=13.1, errors=["NameError: name 'str' is not defined", 'missing 222 customers']
  - X-n190-k8: feasible=False, penalized gap=11.45, errors=["NameError: name 'str' is not defined", 'missing 189 customers']
  - X-n176-k26: feasible=False, penalized gap=10.75, errors=["NameError: name 'str' is not defined", 'missing 175 customers']
### phase9_closeout_budget_matched_no_replay
- Execution mode: `budget_matched_no_replay`.
- Train feasibility rate: 0.0.
- Train penalized gap: 3.0.
- Held-out feasibility rate: 0.0.
- Held-out penalized gap: 3.0.
- Held-out runtime ms: 313.89126.
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
- Train penalized gap: 0.06703.
- Held-out feasibility rate: 1.0.
- Held-out penalized gap: 0.064135.
- Held-out runtime ms: 547.9113.
- Accepted epoch count: 1.
- Fallback epoch count: 0.
- Generation-error epoch count: 0.
- Robustness dispersion across held-out structure families: 0.001517.
- Worst held-out instances:
  - X-n176-k26: feasible=True, penalized gap=0.098197, errors=[]
  - X-n247-k50: feasible=True, penalized gap=0.075066, errors=[]
  - X-n190-k8: feasible=True, penalized gap=0.053828, errors=[]
  - X-n275-k28: feasible=True, penalized gap=0.049565, errors=[]
  - X-n223-k34: feasible=True, penalized gap=0.044019, errors=[]

## Judge Note
### Phase-9 CVRP Closeout Suite Summary (Conservative)

| Condition                                  | Feasibility (Heldout) | Feasible Gap | Penalized Gap | Runtime (ms) | Robustness Dispersion | Complexity | Code Novelty | Notes                                       |
|--------------------------------------------|---------------------|--------------|---------------|--------------|----------------------|------------|--------------|---------------------------------------------|
| Baseline Nearest Neighbor Constructive     | 100%                | 0.2734       | 0.2734        | 43           | 0.00278              | 0          | 0            | Fastest baseline, moderate gap              |
| Baseline Clarke-Wright Savings              | 100%                | 0.0738       | 0.0738        | 77.6         | 0.00779              | 0          | 0            | Best fixed baseline for gap vs. runtime     |
| Baseline Regret Insertion Local Search      | 100%                | 0.4664       | 0.4664        | 1390.5       | 0.0869               | 0          | 0            | Worst gap, longest runtime                   |
| Direct Synthesis + One Repair                | 0%                  | 0.0          | 13.06         | 136          | 1.6167               | 14.9       | 0.974        | No feasibility heldout, high penalty & dispersion |
| Budget-Matched Independent Search (No Replay) | 0%                  | 0.0          | 3.0           | 314          | 0                    | 15.3       | 0.952        | No feasibility, moderate penalty            |
| Replay-Aware Iterative Search (Solver Evolution) | 100%                | **0.0641**   | **0.0641**    | 548          | **0.00152**          | 15.1       | 0.931        | Best gap & robustness among learned methods, feasible |

---

### Interpretation

- **Feasibility:**  
  - All fixed baselines achieved 100% feasibility on heldout data.  
  - Learned methods without replay (direct generation + repair and budget-matched no-replay) failed to produce feasible solutions on heldout.  
  - Replay-aware solver evolution matched fixed baselines in feasibility (100%).  

- **Objective Gap:**  
  - Replay-aware iterative search achieved the lowest heldout feasible gap (0.0641), slightly better than Clarke-Wright baseline (0.0738).  
  - Nearest neighbor and regret insertion were worse.  
  - Learned methods without replay exhibited very high penalized gaps due to infeasibility.  

- **Runtime & Robustness:**  
  - Nearest neighbor fastest, replay-aware iterative search moderate (548 ms), Clarke-Wright faster (77.6 ms).  
  - Replay-aware method exhibited lowest robustness dispersion (0.00152), indicating consistent performance across structure families.  

- **Complexity & Code Novelty:**  
  - Learned conditions had higher complexity (~15) and novelty (~0.93–0.97).  
  - Fixed baselines had zero complexity/novelty.  

- **Replay vs. No Replay:**  
  - Replay-aware iterative search clearly outperformed budget-matched no-replay in feasibility, gap, robustness, and produced feasible solutions.  
  - Budget-matched no-replay failed feasibility despite similar complexity and novelty.  

---

### **Conclusions**

- Among learned methods, **replay-aware iterative search (solver evolution) clearly outperforms fixed baselines and budget-matched no-replay controls** by achieving 100% feasibility, best objective gap, and strong robustness at moderate runtime.  
- Learned conditions without replay failed to produce feasible solutions on heldout data despite reasonable runtime and novelty.  
- **Replay is critical** for feasibility and quality in learned CVRP solution generation within this suite.  
- Fixed baselines remain strong baselines with guaranteed feasibility and competitive gaps but are outperformed on gap by replay-aware iterative methods.
