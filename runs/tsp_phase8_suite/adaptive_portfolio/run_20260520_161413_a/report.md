# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_static_selector, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_161413_a
- started_at_local: 2026-05-20 16:14:13
- finished_at_local: 2026-05-20 16:46:56
- duration_hhmm: 00:33
- duration_seconds: 1963.222
- seed_offset: 0
- replicate_label: a
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1667.927714 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.195137 | 0.122877 | 536.870029 | 0.195137 | 0.037367 | 0.095493 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1678.000271 | 0.072696 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1681.478314 | 0.072847 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.229271 | 0.157011 | 258.545014 | 0.229271 | 0.043202 | 0.111754 | 0.0 | 0.62 | True |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 431.301657 | 0.214311 | 0.024801 | 0.094621 | 0.0 | 2.0175 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.086887 | 0.014627 | 2831.301143 | 0.14749 | 0.000388 | 0.032256 | 0.22521 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.105441 | 0.033181 | 390.821043 | 0.105441 | 0.001007 | 0.039482 | 0.854268 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1667.927714` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.195137`, selector regret `0.122877`, runtime-adjusted gap `0.195137`.
- Family transfer `0.037367` and combined transfer `0.095493`.
- Runtime `536.870029` ms, runtime inflation `-0.678122`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072696`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1678.000271` ms, runtime inflation `0.006039`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072847`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1681.478314` ms, runtime inflation `0.008124`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.229271`, selector regret `0.157011`, runtime-adjusted gap `0.229271`.
- Family transfer `0.043202` and combined transfer `0.111754`.
- Runtime `258.545014` ms, runtime inflation `-0.84499`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:farthest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": 2, "clustered_heuristic": "farthest_insertion_two_opt", "corridor_heuristic": "farthest_insertion_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive frozen-portfolio selector. Prefers farthest_insertion_two_opt as generalist; uses pruning for NN-trap risk, and restart-heavy edge_preserving_restart for stagnation-style recovery; corridor/grid/bottleneck mapped to farthest_ins", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.05, "name": "tsp_frozen_portfolio_instance_rule_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.45, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.024801` and combined transfer `0.094621`.
- Runtime `431.301657` ms, runtime inflation `-0.741415`, mean novelty `0.0`, and complexity `2.0175`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.004, "candidate_limit_offset": 3, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller selecting from frozen heuristic portfolio with bounded online scheduling switches.", "deterministic_randomization": {"mapping_fields": ["number of cities", "coordinate spread", "distance_mean_norm", "distance_cv", "mst_length_norm"], "method": "implicit_seed_from_instance_id"}, "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.07, "name": "tsp_hh_deterministic_interpretable_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "online_schedule_adjustments": {"candidate_pruning_tuning": {"candidate_limit_offset": "candidate_limit_offset", "trigger": "if using candidate-list-capable backbone (detected by heuristic name in {candidate_pruned_two_opt})"}, "late_phase_strategy": {"parameters": {"acceptance_bias": "acceptance_bias", "temperature_scale": "temperature_scale"}, "then_heuristic": "annealed_multi_start", "trigger": "time budget used >= time_budget_trigger AND accepted swaps is low"}, "stagnation_switch": {"perturbation_backoff": {"failed_perturbation_threshold": "failed_perturbation_threshold", "offsets": {"restart_offset": "restart_offset"}}, "then_heuristic": "edge_preserving_restart", "trigger": "stagnation length >= stagnation_threshold AND recent improvement rate < low_improvement_threshold"}}, "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "selection_policy": {"priority_order": ["nn_trap", "two_cluster_bottleneck", "corridor", "clustered", "grid_like", "default"], "rules": {"clustered": {"condition": "clustering score and cluster separation", "heuristic": "cheapest_insertion_two_opt", "op": ">=", "threshold": 0.52}, "corridor": {"condition": "corridor score / elongated structure", "heuristic": "limited_three_opt", "op": ">=", "threshold": 0.46}, "default": {"heuristic": "farthest_insertion_two_opt"}, "grid_like": {"condition": "grid-likeness", "heuristic": "farthest_insertion_two_opt", "op": ">=", "threshold": 0.3}, "nn_trap": {"condition": "nearest-neighbor-trap score", "heuristic": "annealed_multi_start", "op": ">=", "threshold": 0.22}, "two_cluster_bottleneck": {"condition": "bottleneck / two-cluster score", "heuristic": "farthest_insertion_two_opt", "op": ">=", "threshold": 0.55}}}, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.086887`, selector regret `0.014627`, runtime-adjusted gap `0.14749`.
- Family transfer `0.000388` and combined transfer `0.032256`.
- Runtime `2831.301143` ms, runtime inflation `0.697496`, mean novelty `0.22521`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:farthest_insertion_two_opt:stag5:cand-1:restart1`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selection with conservative switching tuned for transfer under diversity-failure replay mode.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "cheapest_insertion_two_opt", "low_improvement_threshold": 0.12, "name": "interpretable_instance_adaptive_tsp_controller_v3", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "farthest_insertion_two_opt", "stagnation_threshold": 5, "temperature_scale": 1.0, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.105441`, selector regret `0.033181`, runtime-adjusted gap `0.105441`.
- Family transfer `0.001007` and combined transfer `0.039482`.
- Runtime `390.821043` ms, runtime inflation `-0.765685`, mean novelty `0.854268`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
**Summary of TSP Adaptive Heuristic Portfolio Suite Evaluation**

| Condition Name                          | Held-out TSPLIB Gap | Selector Regret vs Oracle | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes on Interpretability & Transfer |
|---------------------------------------|---------------------|---------------------------|---------------------|-------------------|--------------|------------------|--------------------------------------|
| **phase8_best_single_fixed_heuristic** (Farthest Insertion 2-opt) | **0.07226**          | 0.0                       | 0.07226             | 0.0               | 0.03122      | Yes              | Strong baseline; top TSPLIB gap, no runtime penalty, zero selector regret; simple and interpretable, static heuristic. |
| phase8_oracle_selector                 | 0.07226              | 0.0                       | 0.07270             | 0.006             | 0.02668      | No               | Oracle baseline (upper bound) matches best fixed heuristic in TSPLIB gap and selector regret; small runtime increase; non-deployable. |
| phase8_supervised_ml_selector          | 0.07226              | 0.0                       | 0.07285             | 0.008             | 0.03122      | No               | Matches best fixed heuristic in TSPLIB gap and regret; slight runtime inflation; adaptive but no clear gain over fixed. |
| phase8_llm_static_selector             | 0.22927              | 0.157                     | 0.22927             | -0.845            | 0.112        | Yes              | Lower runtime but large TSPLIB gap and regret; deterministic, interpretable ruleset but underperforms strongly on gap. |
| phase8_llm_evolved_adaptive_controller | 0.21431              | 0.142                     | 0.21431             | -0.741            | 0.095        | No               | Adaptive with interpretable instance-aware rules; better than static LLM selector but inferior gap to single-best; moderate runtime reduction; some interpretability. |
| phase8_llm_evolved_controller_diversity_failure_replay | 0.08689              | 0.015                     | 0.14749             | 0.697             | 0.032        | No               | Adaptive with diversity failure replay; improved regret, somewhat closer gap to oracle/fixed heuristic; higher runtime inflation (~70%); more complex controller. |
| phase8_full_solver_evolution           | 0.10544              | 0.033                     | 0.10544             | -0.766            | 0.039        | Yes              | Full solver evolution with some code novelty; intermediate gaps and regret; runtime improvement; balances complexity and performance well. |
| phase8_random_portfolio                | 0.19514              | 0.123                     | 0.19514             | -0.678            | 0.095        | Yes              | Random portfolio baseline; poor TSPLIB gap and regret despite low runtime; interpretable but ineffective. |

---

### Conservative Interpretation and Prioritized Conclusions

1. **Primary Endpoint (Held-out TSPLIB Gap):**  
   - The **best single fixed heuristic (farthest_insertion_two_opt)** achieves the lowest TSPLIB gap (~7.2%), which matches the oracle selector (upper bound).  
   - None of the adaptive or static selectors improve meaningfully on this baseline.  
   - Adaptive controllers trade increased complexity for modest or no TSPLIB gap improvements and generally incur runtime penalties or inflated regret.

2. **Selector Regret vs Oracle Portfolio:**  
   - The oracle and best fixed heuristic have zero selector regret, demonstrating this fixed heuristic's optimality in this setting.  
   - Adaptive controllers present non-negligible regret (0.0146–0.157), indicating missed gains from oracle selections.

3. **Runtime-Adjusted Gap & Runtime Inflation:**  
   - Adaptive controllers reduce runtime (up to ~70% less than fixed) but increase gap substantially (>0.14).  
   - The best fixed heuristic runs longer (~1.6s) but yields the best quality gap and zero regret, balancing quality and time.  
   - The diversity failure replay controller trades runtime inflation (~70% higher) for reduced regret but still underperforms the fixed heuristic in absolute gap.

4. **Pareto Efficiency:**  
   - The best fixed heuristic, full solver evolution, LLM static selector, and random portfolio lie on the Pareto front.  
   - Adaptive solutions (evolved controllers) are not Pareto efficient due to worse trade-offs between gap and runtime.  
   - Pareto fronts highlight that the simple fixed heuristic is most competitive overall.

5. **Cross-Family Transfer:**  
   - Transfer gaps for the best fixed heuristic and oracle remain low (~0.03 or less), indicating robust generalization.  
   - Adaptive controllers exhibit higher transfer gaps (up to ~0.11), signifying some generalization weaknesses under cross-family conditions.

6. **Interpretability and Instance-Adaptive Control:**  
   - Adaptive controllers with interpretable rules (phase8_llm_evolved_* controllers) provide instance-adaptive decisions but do not substantially close the gap to the oracle or best fixed heuristic.  
   - Runtime savings are possible at the cost of solution quality and increased complexity.  
   - Static selectors with deterministic heuristic preferences (LLM static selector) show poor gap performance but high interpretability and runtime efficiency.  
   - No new heuristics discovered: all methods control known heuristics.

---

### Final Recommendation

- Retain or prioritize the **best single fixed heuristic (farthest_insertion_two_opt)** as a strong and interpretable baseline for deployment due to its best held-out TSPLIB gap, zero selector regret, and balanced runtime.  
- Adaptive and complex controllers provide proof-of-concept for interpretable instance-adaptive selection but currently fail to improve beyond the fixed heuristic baseline in terms of final gap or regret without runtime penalty.  
- Further tuning or innovation is needed to achieve meaningful TSPLIB gap improvement with adaptive control without excessive runtime inflation.  
- Oracle selector remains a valuable benchmark but is not deployable.  
- Focus next phase on improving adaptive selector quality and transfer robustness, especially reducing selector regret and transfer gap while preserving runtime efficiency.
