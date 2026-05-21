# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_llm_evolved_controller_diversity_failure_replay, phase8_llm_static_selector, phase8_random_portfolio, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_192410_g
- started_at_local: 2026-05-20 19:24:10
- finished_at_local: 2026-05-20 19:52:00
- duration_hhmm: 00:28
- duration_seconds: 1670.934
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1475.563671 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.171446 | 0.099186 | 374.948486 | 0.171446 | 0.083075 | 0.115633 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1531.473886 | 0.074998 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1452.551343 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.229271 | 0.157011 | 270.031986 | 0.229271 | 0.043202 | 0.111754 | 0.0 | 0.62 | True |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 333.649571 | 0.214311 | 0.045346 | 0.107596 | 0.36801 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.201354 | 0.129094 | 319.0006 | 0.201354 | 0.024368 | 0.089574 | 0.702736 | 1.7375 | True |
| phase8_full_solver_evolution | full_solver | none | 0.125551 | 0.053291 | 440.231957 | 0.125551 | 0.001014 | 0.046896 | 0.755521 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1475.563671` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.171446`, selector regret `0.099186`, runtime-adjusted gap `0.171446`.
- Family transfer `0.083075` and combined transfer `0.115633`.
- Runtime `374.948486` ms, runtime inflation `-0.745895`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.074998`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1531.473886` ms, runtime inflation `0.037891`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1452.551343` ms, runtime inflation `-0.015596`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.229271`, selector regret `0.157011`, runtime-adjusted gap `0.229271`.
- Family transfer `0.043202` and combined transfer `0.111754`.
- Runtime `270.031986` ms, runtime inflation `-0.816997`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:farthest_insertion_two_opt:farthest_insertion_two_opt:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 2, "clustered_heuristic": "farthest_insertion_two_opt", "corridor_heuristic": "farthest_insertion_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over frozen portfolio. Biases toward farthest-insertion + 2-opt as default; swaps to NN-trap-safe candidate pruning and occasional annealing/multi-start for instability descriptors.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "det_static_selector_farthest_insertion_priority", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.0, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.045346` and combined transfer `0.107596`.
- Runtime `333.649571` ms, runtime inflation `-0.773883`, mean novelty `0.36801`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:edge_preserving_restart:annealed_multi_start:stag4:cand3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": 3, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Interpretable instance-adaptive selection among a frozen heuristic portfolio with bounded online schedule adjustments driven by stagnation, improvement rate, perturbation failures, and time-budget usage.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "deterministic_instance_adaptive_frozen_portfolio_v4", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.35, "time_budget_trigger": 0.68, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.201354`, selector regret `0.129094`, runtime-adjusted gap `0.201354`.
- Family transfer `0.024368` and combined transfer `0.089574`.
- Runtime `319.0006` ms, runtime inflation `-0.783811`, mean novelty `0.702736`, and complexity `1.7375`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand2:restart2`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": 2, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller over a frozen TSP heuristic portfolio. Structure-conditioned selection with bounded schedule tuning and an interpretable stagnation/failed-perturbation switch.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "deterministic_instance_adaptive_structure_switch_portfolio_v2", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "selection_rules": {"base_by_structure": [{"if": "bottleneck_score >= 0.55 or two_cluster_bottleneck_score >= 0.55", "then": "two_cluster_bottleneck_heuristic"}, {"if": "clusteredness_score >= 0.54 and convex_hull_ratio >= 0.85", "then": "clustered_heuristic"}, {"if": "grid_likeness >= 0.22 and distance_cv >= 0.45", "then": "grid_like_heuristic"}, {"if": "corridor_score >= 0.46 and coordinate_spread_norm >= 0.2", "then": "corridor_heuristic"}, {"if": "nearest_neighbor_trap_score >= 0.30 and nn_distance_cv >= 0.55", "then": "nearest_neighbor_trap_heuristic"}, {"if": "True", "then": "default_heuristic"}], "bounded_schedule_tuning": {"acceptance_bias_rule": "acceptance_bias if recent_improvement_rate <= low_improvement_threshold else 0.0", "candidate_limit_offset_rule": "candidate_limit_offset if (grid_likeness >= 0.22 or corridor_score >= 0.46) else 0", "restart_offset_rule": "restart_offset if stagnation_length >= stagnation_threshold else 0", "temperature_scale_rule": "temperature_scale if (structure_class == 'mixed' and recent_improvement_rate <= low_improvement_threshold) else 1.0"}, "deterministic_priority_hint": ["Diversity_failure mode: if recent_improvement_rate <= low_improvement_threshold and time_budget_used >= time_budget_trigger, prefer random_like_heuristic once; otherwise keep the base rule to avoid thrashing."], "final_resolve_logic": ["step1: choose base via base_by_structure", "step2: if online_stagnation_switch triggers, output stagnation_switch_heuristic", "step3: else if (time_budget_used >= time_budget_trigger and recent_improvement_rate <= low_improvement_threshold) then output random_like_heuristic else keep base", "step4: if time_budget_emphasis overrides, use that result (unless overridden by step2)."], "online_stagnation_switch": [{"if": "stagnation_length >= stagnation_threshold and recent_improvement_rate <= low_improvement_threshold", "then": "stagnation_switch_heuristic"}, {"if": "failed_perturbation_count >= failed_perturbation_threshold and time_budget_used <= time_budget_trigger", "then": "stagnation_switch_heuristic"}, {"if": "True", "then": "base"}], "time_budget_emphasis": [{"if": "time_budget_used >= time_budget_trigger and (grid_likeness >= 0.22 or corridor_score >= 0.46)", "then": "candidate_pruned_two_opt"}, {"if": "time_budget_used >= time_budget_trigger and (bottleneck_score >= 0.55 or two_cluster_bottleneck_score >= 0.55)", "then": "farthest_insertion_two_opt"}, {"if": "time_budget_used >= time_budget_trigger and distance_cv >= 0.55", "then": "nearest_neighbor_multistart"}, {"if": "True", "then": "base"}]}, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.125551`, selector regret `0.053291`, runtime-adjusted gap `0.125551`.
- Family transfer `0.001014` and combined transfer `0.046896`.
- Runtime `440.231957` ms, runtime inflation `-0.701652`, mean novelty `0.755521`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of Phase 8 TSP Heuristic Portfolio Results

| Condition                                 | Final Held-Out TSPLIB Gap | Selector Regret vs Oracle | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes Summary                                                                                                    |
|-------------------------------------------|---------------------------|---------------------------|---------------------|-------------------|--------------|------------------|------------------------------------------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic**   | **0.07226**               | 0.0                       | 0.07226             | 0.0               | 0.031222     | No               | Best held-out TSPLIB gap (primary endpoint). Uses static single heuristic (farthest_insertion_two_opt). Zero runtime inflation and selector regret (oracle baseline). No adaptive selection. |
| **phase8_oracle_selector**                 | 0.07226                   | 0.0                       | 0.074998            | 0.037891          | 0.026678     | No               | Oracle selector upper bound confirms best fixed heuristic performance on TSPLIB gap. Slight runtime inflation. Not deployable but useful for benchmarking selector regret.           |
| phase8_supervised_ml_selector              | 0.07226                   | 0.0                       | 0.07226             | -0.015596         | 0.031222     | Yes              | Static (non-adaptive) learned selector matches best fixed heuristic gap exactly, slightly faster. Interpretable instance-adaptive control is limited but computationally efficient. |
| phase8_full_solver_evolution                | 0.125551                  | 0.053291                  | 0.125551            | -0.701652         | 0.046896     | Yes              | Adaptive full solver evolved controller reduces family gap substantially but TSPLIB performance worse than best fixed. Runtime improved but with some selector regret.                |
| phase8_llm_evolved_controller_diversity_failure_replay | 0.201354               | 0.129094                  | 0.201354            | -0.783811         | 0.089574     | Yes              | Interpretable adaptive controller with diversity failure replay shows moderate TSPLIB gap and regret, runtime savings, and improves cross-family transfer relative to random baseline. |
| phase8_llm_evolved_adaptive_controller      | 0.214311                  | 0.142051                  | 0.214311            | -0.773883         | 0.107596     | Yes              | Interpretable instance-adaptive controller with bounded online schedule adjustments yields decent runtime tradeoff but noticeably higher gaps and regrets than static selectors.         |
| phase8_llm_static_selector                   | 0.229271                  | 0.157011                  | 0.229271            | -0.816997         | 0.111754     | Yes              | Deterministic instance-adaptive static selector with bias towards farthest_insertion_two_opt shows highest regret and gap among Pareto points, but substantial runtime savings.          |
| phase8_random_portfolio                       | 0.171446                  | 0.099186                  | 0.171446            | -0.745895         | 0.115633     | Yes              | Random portfolio selection is Pareto efficient but has clearly worse gaps than best fixed or adaptive selectors, with substantial runtime reduction.                                    |

---

### Summary Observations

- **Primary endpoint (held-out TSPLIB gap)** is lowest (best) and tied at ~0.07226 by the **best single fixed heuristic (farthest_insertion_two_opt)**, the **oracle selector** (upper bound), and the **supervised ML static selector**.

- **Selector regret** is zero only for best single fixed heuristic, supervised ML selector, and oracle selector; adaptive controllers incur higher regret up to ~0.14–0.16, indicating suboptimal adaptive control.

- **Runtime inflation** is minimal or negative (improvement over baseline) for all except oracle (slight inflation). Adaptive controllers achieve significant runtime reduction (roughly 70–80%) but at expense of increased TSPLIB gap and regret.

- **Pareto efficiency** includes adaptive controllers and several static selectors, indicating tradeoffs between runtime and solution quality.

- **Cross-family transfer gaps** are lowest (~0.03) for best fixed and supervised ML selectors; adaptive controllers have moderately higher transfer gaps (~0.09-0.11) but still better than random portfolio (~0.11).

- Adaptive controllers provide **interpretable instance-adaptive control** with structured heuristics switching and schedule tuning. However, they do **not approach the oracle or best fixed heuristic TSPLIB gap**, and improvements come primarily as runtime savings rather than solution quality.

- No evidence of new algorithmic heuristics; results confirm effective **hyper-heuristic control over known heuristics**.

---

### Conservative Conclusion and Recommendations

1. The **best single fixed heuristic (farthest_insertion_two_opt)** remains the strongest baseline on held-out TSPLIB gap without runtime overhead.

2. The **oracle selector** validates the ceiling performance; static selectors that approach oracle gap without sizable runtime inflation (e.g., supervised ML selector) offer promising interpretable instance-adaptive control.

3. Adaptive controllers yield meaningful **runtime advantages with moderate quality tradeoffs**, indicating practical value when fast approximate solutions are acceptable with transparent control policies.

4. Further tuning to reduce selector regret and TSPLIB gap in adaptive controllers is needed before matching best fixed heuristic.

5. Random portfolio strategy is inferior both in gap and regret compared to learned or adaptive selectors, confirming benefit of adaptive hyper-heuristics.

**Overall**, the phase 8 evaluation confirms that instance-adaptive hyper-heuristic control can effectively trade off between solution quality and runtime, but the **best fixed heuristic remains a strong, simple baseline for held-out TSPLIB performance**. Interpretability and bounded adaptation in evolved controllers show good promise but require refinement to approach oracle-like solution quality.
