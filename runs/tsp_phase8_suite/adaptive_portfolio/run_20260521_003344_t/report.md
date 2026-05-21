# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_oracle_selector.

## Run Metadata
- run_name: run_20260521_003344_t
- started_at_local: 2026-05-21 00:33:44
- finished_at_local: 2026-05-21 01:05:43
- duration_hhmm: 00:32
- duration_seconds: 1919.015
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1486.861357 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.187272 | 0.115012 | 3647.311786 | 0.459383 | 0.080217 | 0.119659 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1473.207443 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | True |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1730.919671 | 0.084121 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.214311 | 0.142051 | 485.304986 | 0.214311 | 0.048232 | 0.109419 | 0.0 | 2.36 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.084733 | 0.012473 | 4204.717843 | 0.239618 | 0.001913 | 0.032426 | 0.450543 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.21578 | 0.14352 | 588.777071 | 0.21578 | 0.129601 | 0.161351 | 0.623204 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 211.4116 | 0.213387 | 0.150269 | 0.173523 | 0.913819 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1486.861357` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.187272`, selector regret `0.115012`, runtime-adjusted gap `0.459383`.
- Family transfer `0.080217` and combined transfer `0.119659`.
- Runtime `3647.311786` ms, runtime inflation `1.453027`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1473.207443` ms, runtime inflation `-0.009183`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.084121`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1730.919671` ms, runtime inflation `0.164143`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.048232` and combined transfer `0.109419`.
- Runtime `485.304986` ms, runtime inflation `-0.673604`, mean novelty `0.0`, and complexity `2.36`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.0, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic one-shot hyper-heuristic selector over a frozen portfolio; instance-conditioned structure rules with bounded schedule tuning.", "failed_perturbation_threshold": 2, "fallback_rules": [{"then": "nearest_neighbor_multistart", "when": {"dimension_max": 70}}, {"then": "farthest_insertion_two_opt", "when": {"distance_cv_min": 0.55}}, {"then": "candidate_pruned_two_opt", "when": {"distance_cv_max": 0.35}}], "grid_like_heuristic": "candidate_pruned_two_opt", "instance_rules": [{"then": "edge_preserving_restart", "when": {"bottleneck_score_min": 0.6, "two_cluster_bottleneck_score_min": 0.58}}, {"then": "cluster_first_local_search", "when": {"cluster_separation_min": 0.4, "clustering_score_min": 0.45}}, {"then": "candidate_pruned_two_opt", "when": {"grid_likeness_min": 0.35}}, {"then": "limited_three_opt", "when": {"corridor_score_min": 0.45}}, {"then": "annealed_multi_start", "when": {"nearest_neighbor_trap_score_min": 0.25, "nn_distance_cv_max": 0.35}}, {"then": "annealed_multi_start", "when": {"nearest_neighbor_trap_score_min": 0.22}}], "low_improvement_threshold": 0.08, "name": "tsp_hh_oracle_portfolio_one_shot_deterministic_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.239618`.
- Family transfer `0.001913` and combined transfer `0.032426`.
- Runtime `4204.717843` ms, runtime inflation `1.827915`, mean novelty `0.450543`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:farthest_insertion_two_opt:annealed_multi_start:stag3:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -1, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler over a frozen TSP heuristic portfolio; selects interpretable backbone based on structure descriptors and triggers a controlled diversification switch on stagnation/failure.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "interpretable_instance_adaptive_tsp_hh_v4", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.2, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.21578`, selector regret `0.14352`, runtime-adjusted gap `0.21578`.
- Family transfer `0.129601` and combined transfer `0.161351`.
- Runtime `588.777071` ms, runtime inflation `-0.604013`, mean novelty `0.623204`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand-3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": -3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler/tuner over frozen TSP heuristic portfolio with interpretable switches based on structure scores and online stagnation (diversity_failure replay-hardened).", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.1, "name": "interpretable_portfolio_controller_v2", "nearest_neighbor_trap_heuristic": "nearest_neighbor_multistart", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.2, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `211.4116` ms, runtime inflation `-0.857814`, mean novelty `0.913819`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
```markdown
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

#### Primary Endpoint: Held-out TSPLIB Gap
- The **best single fixed heuristic** (`farthest_insertion_two_opt`) achieves a TSPLIB gap of **0.07226**, matching the **oracle selector** performance exactly.
- The **supervised ML selector** also matches this TSPLIB gap (0.07226), but with slightly higher runtime (1731 ms vs. ~1473 ms oracle).
- The **LLM-evolved adaptive controller** shows a slightly higher gap (0.08473) with significant runtime inflation (~4205 ms) compared to oracle and fixed heuristic.
- Other adaptive or static selectors have notably worse TSPLIB gaps (≥0.21), with lower or comparable runtimes.

#### Selector Regret vs. Oracle Portfolio
- **Oracle selector** has zero regret (by definition).
- **Best single fixed heuristic** also has zero measured selector regret—indicating no regret since it is a fixed heuristic.
- **Supervised ML selector** has zero regret, suggesting it effectively approaches oracle choice.
- **LLM adaptive controllers** show small positive regret (0.0125 for evolved adaptive, ~0.14 for others), indicating imperfect adaptation.
  
#### Runtime-Adjusted Gap and Runtime Inflation
- Oracle and best fixed heuristic yield the minimal runtime-adjusted gap (0.07226) with near-zero or slight negative runtime inflation.
- Supervised ML selector incurs moderate runtime inflation (+16%) with a slightly higher runtime-adjusted gap (0.0841).
- The best LLM adaptive controller has a higher runtime-adjusted gap (0.24) and substantial runtime inflation (+183%)—runtime inflation is not negligible.
- Other adaptive or full solver controllers have runtime-adjusted gaps around 0.21 but with negative runtime inflation (faster). However, their actual TSPLIB gaps are much larger, indicating worse solution quality despite faster runtimes.

#### Pareto Efficiency
- Only the **oracle selector** and **full solver evolution** are marked Pareto efficient.
- The full solver evolution has worse TSPLIB gap but minimal runtime and low complexity.
- Oracle selector achieves best TSPLIB gap with moderate runtime.
- Best fixed heuristic is not Pareto efficient here, but closely matches oracle gap with minimal runtime.

#### Cross-Family Transfer
- Transfer gaps (performance loss on out-of-family instances) are lowest for oracle (~0.027) and best fixed heuristic (~0.031), indicating good generalization.
- The best adaptive controller transfer gap is small (~0.032), but worse controllers or full solver have substantially larger transfer gaps (~0.16–0.17+), reflecting poorer generalization.

---

### Summary & Recommendations

- The **best single fixed heuristic (`farthest_insertion_two_opt`) already achieves held-out TSPLIB gaps matching the oracle selector**, suggesting limited room for improvement from adaptation in terms of final solution quality.
- The **oracle selector serves as a strong upper bound** but is not deployable; fixed heuristic or supervised ML selectors closely approximate it with modest runtime costs.
- **Adaptive controllers studied show interpretable instance-adaptive control with some success but with increased runtime and selector regret**, without surpassing the fixed heuristic baseline on held-out TSPLIB.
- **Runtime inflation is a critical trade-off; adaptive controllers often incur substantial runtime increases without commensurate quality improvement**, limiting their practical advantage.
- **Static and ML selectors that approach oracle performance without excessive runtime inflation are preferable for deployment.**
- Claims of new algorithmic discovery should be avoided—results support **effective hyper-heuristic controller design over known heuristics**, highlighting interpretability and controlled adaptation rather than breakthrough heuristics.
- Cross-family transfer performance aligns with TSPLIB gap trends, reinforcing robustness of fixed and oracle selectors.

---

### Key Data Points:

| Condition                          | TSPLIB Gap | Runtime ms | Runtime-Adjusted Gap | Selector Regret | Runtime Inflation | Pareto Efficient | Transfer Gap |
|----------------------------------|------------|------------|---------------------|-----------------|-------------------|------------------|--------------|
| phase8_best_single_fixed_heuristic | 0.07226    | 1487       | 0.07226             | 0.0             | 0.0               | No               | 0.03122      |
| phase8_oracle_selector            | 0.07226    | 1473       | 0.07226             | 0.0             | -0.009            | Yes              | 0.02668      |
| phase8_supervised_ml_selector     | 0.07226    | 1731       | 0.08412             | 0.0             | +0.164            | No               | 0.03122      |
| phase8_llm_evolved_adaptive_controller | 0.08473    | 4205       | 0.23962             | 0.01247         | +1.828            | No               | 0.03243      |
| phase8_full_solver_evolution      | 0.21339    | 211        | 0.21339             | 0.14113         | -0.858            | Yes              | 0.17352      |

---

### Conclusion

- For deployable hyper-heuristic control of TSP portfolios, **the best fixed heuristic or supervised ML selectors best balance interpretability, near-oracle quality, and runtime efficiency.**
- **LLM-based adaptive controllers demonstrate interpretable adaptation but suffer from excessive runtime and modest quality gains, limiting practical appeal at this stage.**
- Further improvement should focus on reducing runtime inflation or improving selector regret without sacrificing interpretability.
```
