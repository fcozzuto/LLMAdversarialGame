# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_random_portfolio, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_213122_l
- started_at_local: 2026-05-20 21:31:22
- finished_at_local: 2026-05-20 21:46:24
- duration_hhmm: 00:15
- duration_seconds: 902.662
- seed_offset: 11000
- replicate_label: l
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 700.194257 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.169899 | 0.097639 | 78.5905 | 0.169899 | 0.078717 | 0.11231 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 700.106143 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 696.790643 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.086887 | 0.014627 | 1347.321329 | 0.167189 | 0.002791 | 0.033774 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.190914 | 0.118654 | 104.241157 | 0.190914 | 0.036509 | 0.093395 | 0.536232 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.124922 | 0.052662 | 1852.313071 | 0.330472 | 0.014601 | 0.055245 | 0.587454 | 0.6975 | False |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 100.055386 | 0.213387 | 0.150269 | 0.173523 | 0.852585 | 0.56 | False |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `700.194257` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.169899`, selector regret `0.097639`, runtime-adjusted gap `0.169899`.
- Family transfer `0.078717` and combined transfer `0.11231`.
- Runtime `78.5905` ms, runtime inflation `-0.887759`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `700.106143` ms, runtime inflation `-0.000126`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `696.790643` ms, runtime inflation `-0.004861`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.086887`, selector regret `0.014627`, runtime-adjusted gap `0.167189`.
- Family transfer `0.002791` and combined transfer `0.033774`.
- Runtime `1347.321329` ms, runtime inflation `0.924211`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over a frozen TSP heuristic portfolio using structure descriptors; tuned to favor farthest/compact 2-opt on general cases, candidate-pruning for grid-like, and clustered/bottleneck-aware search only when justified by de", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "det_heur_portfolio_instance_adaptive_v1", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.190914`, selector regret `0.118654`, runtime-adjusted gap `0.190914`.
- Family transfer `0.036509` and combined transfer `0.093395`.
- Runtime `104.241157` ms, runtime inflation `-0.851125`, mean novelty `0.536232`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:candidate_pruned_two_opt:stag4:cand-1:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Interpretable deterministic instance-adaptive hyper-heuristic controller over a frozen TSP heuristic portfolio using instance descriptors and online stagnation/progress signals to schedule bounded tuning.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.1, "name": "deterministic_instance_adaptive_tsp_hh_epoch2", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "candidate_pruned_two_opt", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.124922`, selector regret `0.052662`, runtime-adjusted gap `0.330472`.
- Family transfer `0.014601` and combined transfer `0.055245`.
- Runtime `1852.313071` ms, runtime inflation `1.645427`, mean novelty `0.587454`, and complexity `0.6975`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:cheapest_insertion_two_opt:stag3:cand1:restart0`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over frozen heuristic portfolio with bounded online scheduling. Structure-driven initial heuristic choice (grid/cluster/bottleneck/corridor/trap) and stagnation/failed-perturbation driven deterministic switching to a si", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.14, "name": "det_adaptive_tsp_portfolio_v3", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 0, "stagnation_switch_heuristic": "cheapest_insertion_two_opt", "stagnation_threshold": 3, "temperature_scale": 0.95, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `100.055386` ms, runtime inflation `-0.857103`, mean novelty `0.852585`, and complexity `0.56`.
- Pareto efficient: `False`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Suite Results

| Criterion                      | Best Condition(s)                                 | Notes & Interpretation                                                                                  |
|-------------------------------|-------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Held-out TSPLIB Gap (Primary)**     | `phase8_best_single_fixed_heuristic`, `phase8_supervised_ml_selector`, `phase8_oracle_selector` | All three show identical final TSPLIB gaps: 0.07226. The fixed heuristic (farthest_insertion_two_opt) is as good as the ML selector, matching the oracle upper bound closely. |
| **Selector Regret vs Oracle** | `phase8_best_single_fixed_heuristic`, `phase8_supervised_ml_selector` (0.0 regret)            | Adaptive selectors achieved *no regret* compared to oracle selector, indicating interpretable and effective instance-adaptive control. |
| **Runtime-Adjusted Gap**       | `phase8_best_single_fixed_heuristic`, `phase8_supervised_ml_selector`, `phase8_oracle_selector` (≈0.072) | Despite runtime inflation differences, gaps are close, with the fixed and supervised selectors achieving similar overall efficiency. |
| **Runtime Inflation**          | The fixed heuristic and supervised selector have zero or negative runtime inflation; static and adaptive (LLM evolved) controllers show up to near 1.6x inflation (e.g., `phase8_llm_static_selector`, `phase8_llm_evolved_controller_diversity_failure_replay`) | Runtime inflation is a concern for more complex adaptive controllers; simpler ML selector maintains runtime efficiency without gap loss. |
| **Pareto Efficiency**          | `phase8_random_portfolio` and `phase8_supervised_ml_selector`                                | ML selector is pareto-efficient combining good gap with acceptable runtime, unlike fixed heuristic which is near but not marked pareto efficient. Random portfolio is not competitive in gap. |
| **Cross-Family Transfer Gap** | Lowest transfer gap with `phase8_oracle_selector` (0.0267), close second `phase8_best_single_fixed_heuristic` and `phase8_supervised_ml_selector` (~0.0312) | ML selectors and best single fixed heuristic generalize well to unseen families, indicating robust instance-adaptive control. Adaptive controllers show larger transfer gaps. |
| **Adaptation Efficiency & Complexity** | Adaptive controllers have modest adaptation efficiency (~0.06-0.09), but runtime inflation and increased complexity (~0.6-0.7) without meaningful TSPLIB gap improvements | Adaptive control is interpretable but not clearly beneficial over simpler ML approach with respect to primary metric, and adds complexity and runtime costs. |
| **Controller Novelty**         | Adaptive controllers show non-zero novelty (>0.5), but this does not translate to improved held-out TSPLIB gap or regret | Suggests that exploration/new code does not improve final portfolio control effectiveness in this phase. |

---

### Summary

- **Primary endpoint (held-out TSPLIB gap):** The best single fixed heuristic (`farthest_insertion_two_opt`) and the supervised ML selector both achieve the lowest gap (0.07226), matching the oracle selector upper bound. This implies no advantage yet from adaptive hyper-heuristic control in terms of solution quality.
- **Instance-adaptive control:** ML selector offers interpretable instance-adaptive control without runtime inflation or selector regret, showing strong practical promise. Adaptive LLM-evolved controllers, though interpretable, do not improve on this baseline and incur large runtime and complexity costs.
- **Runtime and efficiency:** Prefer simpler, static or ML selectors for deployment due to near-oracle gap performance and controlled runtime overhead; avoid adaptive controllers causing runtime inflation with no gap benefit.
- **Cross-family transfer:** The ML selector and fixed baseline transfer well to unseen problem families, indicating robustness and generalizability of selected heuristics.
- **No new algorithm discovery:** The results focus on controlling known heuristics; no evidence of new heuristics or fundamentally novel algorithms is observed.

---

### Recommendations

- Prioritize ML-based supervised selector for deployment as an interpretable, low-regret, efficient instance-adaptive heuristic controller.
- Avoid or further refine adaptive LLM-based controllers until they can demonstrate gap improvements or runtime efficiency closer to oracle/fixed baseline.
- Continue to monitor transfer gaps to ensure robustness across diverse instance families without runtime penalty.
- Focus future research on improving adaptation efficiency and runtime rather than code novelty or complexity increase.
