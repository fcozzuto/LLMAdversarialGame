# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_llm_evolved_adaptive_controller`.
- Best combined transfer gap: `phase8_llm_evolved_adaptive_controller`.
- Lowest selector regret: `phase8_llm_evolved_adaptive_controller`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_random_portfolio, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_224252_p
- started_at_local: 2026-05-20 22:42:52
- finished_at_local: 2026-05-20 22:59:07
- duration_hhmm: 00:16
- duration_seconds: 974.878
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 699.734114 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.160733 | 0.088473 | 195.759071 | 0.160733 | 0.136539 | 0.145452 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 699.788357 | 0.072266 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 699.511157 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.216874 | 0.144614 | 165.082929 | 0.216874 | 0.024668 | 0.095481 | 0.0 | 1.4 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.067008 | -0.005252 | 2049.241129 | 0.19624 | 8.9e-05 | 0.024743 | 0.611081 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.214311 | 0.142051 | 264.935986 | 0.214311 | 0.023657 | 0.093898 | 0.489403 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 99.585957 | 0.213387 | 0.150269 | 0.173523 | 0.92146 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `699.734114` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.160733`, selector regret `0.088473`, runtime-adjusted gap `0.160733`.
- Family transfer `0.136539` and combined transfer `0.145452`.
- Runtime `195.759071` ms, runtime inflation `-0.720238`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072266`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `699.788357` ms, runtime inflation `7.8e-05`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `699.511157` ms, runtime inflation `-0.000319`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.216874`, selector regret `0.144614`, runtime-adjusted gap `0.216874`.
- Family transfer `0.024668` and combined transfer `0.095481`.
- Runtime `165.082929` ms, runtime inflation `-0.764078`, mean novelty `0.0`, and complexity `1.4`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over frozen TSP heuristic portfolio with bounded schedule-tuning parameters; prefers bottleneck/cluster-aware methods only when descriptors justify it.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "instance_adaptive_rules": [{"use": "grid_like_heuristic", "when": {"grid_likeness_gte": 0.6}}, {"use": "two_cluster_bottleneck_heuristic", "when": {"bottleneck_score_gte": 0.62}}, {"use": "clustered_heuristic", "when": {"clusteredness_score_gte": 0.42}}, {"use": "corridor_heuristic", "when": {"corridor_score_gte": 0.5}}, {"use": "nearest_neighbor_trap_heuristic", "when": {"nearest_neighbor_trap_score_gte": 0.26}}], "low_improvement_threshold": 0.08, "name": "tsp_frozen_portfolio_instance_adaptive_v1", "nearest_neighbor_trap_heuristic": "edge_preserving_restart", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.15, "tie_breaker": {"deterministic_slope": {"key": "distance_cv", "prefer_lower": true}, "prefer": ["default_heuristic"]}, "time_budget_trigger": 0.45, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.067008`, selector regret `-0.005252`, runtime-adjusted gap `0.19624`.
- Family transfer `8.9e-05` and combined transfer `0.024743`.
- Runtime `2049.241129` ms, runtime inflation `1.9286`, mean novelty `0.611081`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:farthest_insertion_two_opt:stag4:cand-2:restart2`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive HH controller over frozen TSP portfolio; selects structure-matched specialist heuristics and uses conservative stagnation/low-improvement retuning to avoid thrashing.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "tsp_hh_oracle_style_portfolio_controller_v4", "nearest_neighbor_trap_heuristic": "edge_preserving_restart", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "farthest_insertion_two_opt", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.023657` and combined transfer `0.093898`.
- Runtime `264.935986` ms, runtime inflation `-0.621376`, mean novelty `0.489403`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cheapest_insertion_two_opt:farthest_insertion_two_opt:annealed_multi_start:stag4:cand3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": 3, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "candidate_pruned_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over a frozen TSP heuristic portfolio using interpretable structure scores (cluster/bottleneck/grid/corridor/trap) plus an online stagnation trigger to switch from mostly 2-opt refinement to restart/annealed diversifica", "failed_perturbation_threshold": 3, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "tsp_heuristic_hyperheuristic_oracle_proxy_v2", "nearest_neighbor_trap_heuristic": "edge_preserving_restart", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.2, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `99.585957` ms, runtime inflation `-0.85768`, mean novelty `0.92146`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

| Metric                       | phase8_llm_evolved_adaptive_controller | phase8_supervised_ml_selector | phase8_best_single_fixed_heuristic | phase8_random_portfolio | phase8_full_solver_evolution |
|------------------------------|----------------------------------------|-------------------------------|------------------------------------|-------------------------|------------------------------|
| **Held-out TSPLIB gap**       | **0.0670** (best, lower is better)     | 0.0723                        | 0.0723                             | 0.1607                  | 0.2134                       |
| Selector Regret vs Oracle     | -0.00525 (negative, meaning slightly better) | 0.0                           | 0.0                               | 0.0885                   | 0.1411                       |
| Runtime-Adjusted Gap          | 0.1962                                 | 0.0723                        | 0.0723                             | 0.1607                  | 0.2134                       |
| Runtime Inflation             | 1.93 (substantial runtime increase)    | -0.0003 (no inflation)        | 0.0                               | -0.72 (runtime reduced)  | -0.86 (runtime reduced)      |
| Transfer Gap Cross-Family     | 0.0247 (lowest)                         | 0.0312                        | 0.0312                             | 0.1455                  | 0.1735                       |
| Pareto Efficient             | Yes                                    | Yes                          | No                                | Yes                     | Yes                         |
| Adaptation Efficiency         | 0.0235 (modest adaptation)              | 0.0                           | 0.0                               | 0.0                      | -0.0347 (negative)           |

---

### Key Points

- **Primary endpoint (Held-out TSPLIB gap):**  
  The **phase8_llm_evolved_adaptive_controller** achieves the best performance with a gap of 0.0670, outperforming the static supervised ML selector (0.0723) and best single heuristic baseline (0.0723). This indicates meaningful improvement in solution quality on unseen TSPLIB instances.

- **Selector regret vs oracle portfolio:**  
  The oracle selector is an upper bound; the evolved adaptive controller has slightly negative selector regret (-0.00525), effectively matching or slightly surpassing the oracle's performance (likely due to statistical variation). This suggests highly effective instance-adaptive control.

- **Runtime-adjusted gap / inflation:**  
  The evolved adaptive controller incurs a significant runtime inflation (~1.93x) compared to others. While it improves solution quality, this comes at a substantial runtime cost. The static ML selector achieves similar held-out gap with zero runtime inflation, offering a better runtime-quality tradeoff.

- **Pareto efficiency:**  
  The evolved adaptive controller, supervised ML selector, random portfolio, and full solver evolution are Pareto efficient. However, random portfolio and full solver evolution yield substantially worse solution quality.

- **Cross-family transfer:**  
  The evolved adaptive controller exhibits the best transfer gap (0.0247), indicating strong generalization across heterogeneous TSP families.

- **Adaptation efficiency:**  
  Evolved adaptive controller shows small positive adaptation efficiency (0.0235), indicating limited but present benefit from adaptation versus static selection. Static selectors have zero adaptation.

- **Interpretability & control:**  
  The evolved adaptive controller uses interpretable, structure-based heuristic selection with conservative stagnation triggers, avoiding thrashing—a promising approach to hyper-heuristic control rather than discovering new heuristics.

---

### Summary and Recommendations

- The **phase8_llm_evolved_adaptive_controller** shows the best held-out TSPLIB gap and selector regret near zero, demonstrating effective and interpretable instance-adaptive hyper-heuristic control that closely approaches oracle portfolio performance.

- However, this improvement comes with almost doubling average runtime, which may limit deployability unless runtime budgets are flexible.

- The **phase8_supervised_ml_selector** achieves competitive TSPLIB gap with no runtime inflation, representing a strong static adaptive baseline.

- The best single fixed heuristic already provides a reasonable baseline, but adaptive controllers outperform it in held-out generalization and transfer.

- Adaptive control with minimal runtime inflation remains a key goal; future work should explore runtime-quality trade-offs further.

- No new heuristics were discovered; all gains derive from improved adaptive control over a frozen heuristic portfolio, as intended.

---

**Conservative conclusion:** The evolved adaptive controller effectively improves held-out TSP solution quality by leveraging interpretable instance features to select heuristics adaptively. It closes the gap with the oracle portfolio but at notable runtime cost. Static supervised selectors offer a compelling compromise with similar quality and better efficiency. The framework shows promising cross-family generalization and interpretable control, meriting further investigation to optimize runtime performance.
