# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_175541_d
- started_at_local: 2026-05-20 17:55:41
- finished_at_local: 2026-05-20 18:25:17
- duration_hhmm: 00:30
- duration_seconds: 1775.739
- seed_offset: 3000
- replicate_label: d
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1454.958643 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.218775 | 0.146515 | 310.9475 | 0.218775 | 0.082909 | 0.132965 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1558.234271 | 0.077389 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1493.702814 | 0.074184 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.120261 | 0.048001 | 7173.831929 | 0.59296 | 0.001723 | 0.045395 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 383.137643 | 0.214311 | 0.023867 | 0.09403 | 0.0 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.214732 | 0.142472 | 545.303743 | 0.214732 | 0.027988 | 0.096788 | 0.548632 | 0.755 | False |
| phase8_full_solver_evolution | full_solver | none | 0.156335 | 0.084075 | 383.862343 | 0.156335 | 0.001014 | 0.058238 | 0.717957 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1454.958643` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.218775`, selector regret `0.146515`, runtime-adjusted gap `0.218775`.
- Family transfer `0.082909` and combined transfer `0.132965`.
- Runtime `310.9475` ms, runtime inflation `-0.786284`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.077389`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1558.234271` ms, runtime inflation `0.070982`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.074184`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1493.702814` ms, runtime inflation `0.026629`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.59296`.
- Family transfer `0.001723` and combined transfer `0.045395`.
- Runtime `7173.831929` ms, runtime inflation `3.930609`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic one-shot portfolio selector using instance-structure cues; base is farthest-insertion + 2-opt, with specialized fallbacks for clustered/bottleneck and edge-preserving recovery.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.06, "name": "static_instance_adaptive_farthest_base", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.023867` and combined transfer `0.09403`.
- Runtime `383.137643` ms, runtime inflation `-0.736668`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 3, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "cluster_first_local_search", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selection among frozen TSP heuristics with online stagnation/restart tuning (interpretable structural triggers).", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "det_adaptive_frozen_portfolio_v1", "nearest_neighbor_trap_heuristic": "edge_preserving_restart", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.214732`, selector regret `0.142472`, runtime-adjusted gap `0.214732`.
- Family transfer `0.027988` and combined transfer `0.096788`.
- Runtime `545.303743` ms, runtime inflation `-0.62521`, mean novelty `0.548632`, and complexity `0.755`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:farthest_insertion_two_opt:edge_preserving_restart:stag2:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.004, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler over frozen portfolio. Strong generalist baseline is farthest-insertion + 2-opt. Grid-like instances switch to candidate-pruned 2-opt. Strong nearest-neighbor trap risk uses multi-start NN (less thrashy than annealed).", "failed_perturbation_threshold": 1, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.09, "name": "det_adaptive_tsp_frozen_portfolio_epoch3", "nearest_neighbor_trap_heuristic": "nearest_neighbor_multistart", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 2, "temperature_scale": 1.1, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.156335`, selector regret `0.084075`, runtime-adjusted gap `0.156335`.
- Family transfer `0.001014` and combined transfer `0.058238`.
- Runtime `383.862343` ms, runtime inflation `-0.73617`, mean novelty `0.717957`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Portfolio Suite Results

| Metric                           | Notes / Priority                                                                              |
|---------------------------------|----------------------------------------------------------------------------------------------|
| **Primary: Held-out TSPLIB Gap** | - Best performance by **phase8_best_single_fixed_heuristic** (gap 0.07226).                   |
|                                 | - Several adaptive selectors (including **phase8_supervised_ml_selector**) match this gap.   |
|                                 | - Oracle selector (upper bound) also at 0.07226 gap but with higher runtime (not deployable).|
| **Selector Regret vs Oracle**    | - Best fixed heuristic & supervised selector show zero selector regret (match oracle gap).  |
|                                 | - Adaptive controllers show substantial selector regret (~0.08–0.14), indicating imperfect adaptation.   |
| **Runtime-Adjusted Gap**          | - Best single fixed heuristic achieves 0.07226 gap with no runtime inflation.                 |
|                                 | - Oracle’s runtime-adjusted gap slightly higher (0.0774) with moderate (7%) runtime inflation.|
|                                 | - Adaptive controllers have higher runtime-adjusted gaps (~0.15–0.21), but with reduced runtime inflation (mostly negative, i.e., faster). |
|                                 | - Static LLM instance-adaptive selector suffers from large runtime inflation (~4x slower) and worsened TSPLIB gap (0.12). |
| **Pareto Efficiency**             | - Pareto-efficient: best fixed heuristic, full solver evolution, evolved adaptive controller, and random portfolio.  |
|                                 | - Oracle and LLM static selector are *not* Pareto efficient due to runtime or gap trade-offs.|
| **Cross-Family Transfer Gaps**   | - Best fixed heuristic and supervised selector show low transfer gaps (~0.03).                |
|                                 | - Adaptive controllers show higher transfer gaps (~0.06–0.09), reflecting some generalization challenges. |
| **Interpretable Instance-Adaptive Control** | - Adaptive controllers embody interpretable rules/triggers (e.g., stagnation thresholds, instance-structure cues).  |
|                                 | - However, they do not significantly close the gap to oracle or fixed heuristic baseline.   |
|                                 | - They offer runtime savings (negative runtime inflation) but at cost of increased final gap and regret.|
| **Summary Points**               | - The strong baseline is a fixed heuristic: *farthest_insertion_two_opt*.                    |
|                                 | - Learned/adaptive selectors approximate oracle TSPLIB gap without outperforming baseline.  |
|                                 | - Runtime overheads vary: some adaptive methods reduce runtime modestly but accept higher gaps. |
|                                 | - LLM static selector is expensive runtime-wise and yields higher gaps; not Pareto optimal. |
|                                 | - No novel heuristics discovered; control over known heuristics is consistent with design goals. |

---

### Final Conservative Conclusion

The best single fixed heuristic (farthest_insertion + 2-opt) remains a strong, Pareto-efficient baseline with the lowest held-out TSPLIB gap and zero selector regret. Adaptive/selective portfolio methods show interpretable instance-adaptive control, trading some accuracy for runtime efficiency, but do not surpass the fixed heuristic's gap or approach the oracle selector closely enough to justify runtime or gap costs. LLM-based static adaptation incurs excessive runtime inflation and worsened gaps. Overall, the results underscore the challenge of improving upon a robust fixed heuristic baseline via adaptive control, emphasizing careful trade-offs between solution quality, runtime, and generalization across TSP families without claiming new algorithmic improvements.
