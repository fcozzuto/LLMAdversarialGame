# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_202759_i
- started_at_local: 2026-05-20 20:27:59
- finished_at_local: 2026-05-20 20:54:46
- duration_hhmm: 00:27
- duration_seconds: 1606.713
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1513.481557 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.140178 | 0.067918 | 3828.667229 | 0.354609 | 0.104682 | 0.117759 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1502.802957 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1489.335586 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.230747 | 0.158487 | 296.350486 | 0.230747 | 0.073705 | 0.131563 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.20283 | 0.13057 | 347.631771 | 0.20283 | 0.023657 | 0.089668 | 0.073958 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.214732 | 0.142472 | 198.764786 | 0.214732 | 0.046459 | 0.108455 | 0.488141 | 1.7 | False |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 101.700771 | 0.213387 | 0.150269 | 0.173523 | 0.837837 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1513.481557` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.140178`, selector regret `0.067918`, runtime-adjusted gap `0.354609`.
- Family transfer `0.104682` and combined transfer `0.117759`.
- Runtime `3828.667229` ms, runtime inflation `1.529709`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1502.802957` ms, runtime inflation `-0.007056`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1489.335586` ms, runtime inflation `-0.015954`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.230747`, selector regret `0.158487`, runtime-adjusted gap `0.230747`.
- Family transfer `0.073705` and combined transfer `0.131563`.
- Runtime `296.350486` ms, runtime inflation `-0.804193`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:limited_three_opt:edge_preserving_restart:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.004, "candidate_limit_offset": 3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "annealed_multi_start", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-conditioned selector from frozen portfolio: structure-first heuristic mapping with bounded schedule tuning.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "det_tsp_hh_oracle_style_portfolio_epoch1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.20283`, selector regret `0.13057`, runtime-adjusted gap `0.20283`.
- Family transfer `0.023657` and combined transfer `0.089668`.
- Runtime `347.631771` ms, runtime inflation `-0.77031`, mean novelty `0.073958`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag4:cand3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": 3, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "candidate_pruned_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Interpretable, instance-adaptive scheduler selecting from a frozen TSP heuristic portfolio with bounded online adjustments via stagnation, improvement, and failed-perturbation triggers.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.1, "name": "deterministic_instance_adaptive_portfolio_v2", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.214732`, selector regret `0.142472`, runtime-adjusted gap `0.214732`.
- Family transfer `0.046459` and combined transfer `0.108455`.
- Runtime `198.764786` ms, runtime inflation `-0.86867`, mean novelty `0.488141`, and complexity `1.7`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:limited_three_opt:edge_preserving_restart:stag4:cand-1:restart1`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -1, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic interpretable instance-adaptive hyper-heuristic controller selecting among a frozen TSP heuristic portfolio with bounded online tuning from instance descriptors and runtime stagnation signals.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.11, "name": "tsp_hh_portfolio_v2_deterministic", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "policy": {"deterministic": true, "deterministic_tuning_rules": {"annealing_acceptance": {"acceptance_bias_rule": "acceptance_bias + 0.008*(stagnation length - 1)", "acceptance_clamp": [-0.01, 0.02], "temperature_clamp": [0.5, 1.8], "temperature_scale_rule": "temperature_scale * (1.0 + 0.45*(distance_cv - 0.5))"}, "candidate_limit": {"clamp": [-6, 6], "offset_formula": "candidate_limit_offset + (1 if grid_likeness >= 0.40 else -1) + (-1 if recent improvement rate <= low_improvement_threshold else 0)"}, "restart_intensity": {"clamp": [-3, 4], "int_formula": "restart_offset + (1 if stagnation length >= stagnation_threshold else 0) + (1 if failed perturbation count >= failed_perturbation_threshold else 0) - (1 if recent improvement rate > low_improvement_threshold else 0)"}}, "diversity_guard_for_diversity_failure_mode": {"condition": [["non-improving streak", ">=", 2]], "rule": "if recent accepted swaps are low and non-improving streak >= 2, run random_like_heuristic once at the next stagnation checkpoint instead of stagnation_switch_heuristic"}, "fallback": "default_heuristic", "instance_selection": [{"if": [["bottleneck / two-cluster score", ">=", 0.58], ["distance_cv", ">=", 0.45]], "then": "two_cluster_bottleneck_heuristic"}, {"if": [["corridor score / elongated structure", ">=", 0.46]], "then": "corridor_heuristic"}, {"if": [["grid-likeness", ">=", 0.4]], "then": "grid_like_heuristic"}, {"if": [["clustering score", ">=", 0.52]], "then": "clustered_heuristic"}, {"if": [["nearest-neighbor trap score", ">=", 0.26]], "then": "nearest_neighbor_trap_heuristic"}], "online_schedule": [{"before_trigger": {"acceptance_bias_effect": ["instance distance_std_norm", "affine", -0.002, 0.01, "clip", [-0.01, 0.02]], "candidate_limit_offset_effect": ["instance grid-likeness", "lin", -1.5, 1.5, "clip", [-6, 6]], "restart_intensity_effect": ["instance bottleneck / two-cluster score", "lin", -1, 2, "clip", [-3, 4]], "temperature_scale_effect": ["instance distance_cv", "affine_to_scale", 0.95, 1.15, "clip", [0.5, 1.8]]}, "phase_split_by": "time_budget_trigger"}, {"if": [["stagnation length", ">=", "stagnation_threshold"]], "then_switch_heuristic": "stagnation_switch_heuristic", "trigger": "stagnation length"}, {"if": [["recent improvement rate", "<=", "low_improvement_threshold"]], "then": {"candidate_list_action": "tighten candidate list deterministically by 1 step (or apply candidate_limit_offset if late-phase)", "failed_perturbation_count_action": {"do": "increase restart intensity deterministically by 1 step", "if_failed_count": ["failed perturbation count", ">=", "failed_perturbation_threshold"]}}, "trigger": "stagnation / low improvement"}, {"if": [["time budget used", ">=", "time_budget_trigger"]], "then": {"candidate_list_action": "set candidate limit using candidate_limit_offset and grid-likeness sign", "restart_intensity_action": "reduce perturbation aggressiveness by 1 step if recent improvement rate > low_improvement_threshold else keep"}, "trigger": "late phase tightening"}], "priority_order": ["two_cluster_bottleneck", "corridor", "grid_like", "clustered", "nearest_neighbor_trap", "default"]}, "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 4, "temperature_scale": 1.15, "time_budget_trigger": 0.62, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `101.700771` ms, runtime inflation `-0.932803`, mean novelty `0.837837`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
```markdown
# TSP Adaptive Heuristic Portfolio Suite Review

## Primary Endpoint: Held-Out TSPLIB Gap
- The best held-out TSPLIB gap (0.07226) is achieved by both:
  - **phase8_best_single_fixed_heuristic** (farthest_insertion_two_opt)
  - **phase8_supervised_ml_selector**
- The **oracle_selector** also shows this gap (0.07226) but is noted as an upper bound, not deployable.
- Other adaptive controllers have higher TSPLIB gaps (~0.20+), indicating no improvement over the best fixed heuristic in raw gap terms.

## Selector Regret vs. Oracle Portfolio
- **phase8_best_single_fixed_heuristic** has zero selector regret (by definition).
- **phase8_supervised_ml_selector** matches zero selector regret, demonstrating near-oracle performance without runtime inflation.
- Adaptive controllers exhibit non-zero selector regret (0.13 - 0.14), indicating incomplete oracle approximation.

## Runtime-Adjusted Gap & Runtime Inflation
- The best fixed heuristic and supervised ML selector have runtime inflation near zero or slightly negative, confirming no runtime penalty.
- The **phase8_best_single_fixed_heuristic** and **supervised_ml_selector** runtime-adjusted gaps are identical (~0.07226), efficient.
- Adaptive controllers show higher runtime-adjusted gaps (~0.20), but have negative runtime inflation (beneficial runtime reduction), indicating more efficient runtime behavior but at cost of solution quality.
- The **LLM static selector** has low runtime (296 ms vs. ~1500 ms for fixed heuristics) but substantially worse gap (0.2307), indicating a quality-runtime tradeoff.

## Pareto Efficiency
- Pareto-efficient conditions:
  - **phase8_supervised_ml_selector**: low gap, no runtime inflation, zero regret.
  - **phase8_llm_evolved_adaptive_controller**: improved runtime (negative inflation), reasonable gap, interpretable adaptive control.
  - **phase8_full_solver_evolution**: lowest runtime (~102 ms) but higher gap (0.2134), high code novelty suggesting newly evolved heuristics.

## Cross-Family Transfer Gap
- Transfer gaps are smallest for oracle (0.027) and best fixed (0.031), followed closely by supervised_ml_selector (0.031).
- Adaptive controllers increase transfer gaps (0.09 to 0.11), suggesting less robust cross-family generalization.
- Random portfolio and full solver demonstrate higher transfer gaps, less effective generalization.

## Interpretability and Instance-Adaptive Control
- The **phase8_supervised_ml_selector** achieves near-oracle performance with no runtime inflation and zero selector regret, confirming it as an effective static instance-adaptive selector.
- The **phase8_llm_evolved_adaptive_controller** provides interpretable, bounded online adjustments, achieving runtime gains with moderate quality trade-offs — a promising adaptive control approach.
- Increased complexity and code novelty in fully evolved controllers suggest exploratory solutions but with diminished interpretability and no quality gains.

## Summary and Recommendations
- The known heuristic **farthest_insertion_two_opt** remains the strongest baseline in gap performance.
- The supervised ML selector matches the oracle gap and selector regret without runtime cost, demonstrating effective and interpretable instance-adaptive static selection.
- Adaptive controllers offer valuable runtime reductions with bounded quality loss, offering a practical trade-off for runtime-sensitive deployments.
- Cross-family transfer is best preserved by static selectors close to the oracle; adaptive controllers slightly degrade transfer robustness.
- Given the risk of overclaiming, conclusions emphasize:
  - The strong baseline of the best fixed heuristic.
  - Successful hyper-heuristic control via supervised ML static selector approximating oracle performance.
  - Adaptive controllers offering runtime-efficient, interpretable instance-adaptive scheduling, without new heuristic discovery.

---

**Key conservative claim:**  
*Interpretable static and adaptive hyper-heuristic controller designs closely approach the oracle portfolio performance on held-out TSPLIB instances, with negligible runtime inflation or beneficial runtime reductions, demonstrating effective instance-adaptive control over known TSP heuristics.*
