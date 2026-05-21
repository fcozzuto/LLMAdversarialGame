# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_controller_diversity_failure_replay, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_233037_r
- started_at_local: 2026-05-20 23:30:37
- finished_at_local: 2026-05-21 00:01:01
- duration_hhmm: 00:30
- duration_seconds: 1824.203
- seed_offset: 17000
- replicate_label: r
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1460.617029 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.222318 | 0.150058 | 275.057457 | 0.222318 | 0.093572 | 0.141005 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1536.636057 | 0.076021 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1471.485043 | 0.072798 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.21578 | 0.14352 | 561.677043 | 0.21578 | 0.027632 | 0.09695 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 612.389671 | 0.214311 | 0.045168 | 0.107484 | 0.575945 | 1.98 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.124043 | 0.051783 | 837.051443 | 0.124043 | 0.023034 | 0.060248 | 0.839823 | 2.0325 | True |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 231.024057 | 0.213387 | 0.150269 | 0.173523 | 0.865434 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1460.617029` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.222318`, selector regret `0.150058`, runtime-adjusted gap `0.222318`.
- Family transfer `0.093572` and combined transfer `0.141005`.
- Runtime `275.057457` ms, runtime inflation `-0.811684`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.076021`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1536.636057` ms, runtime inflation `0.052046`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072798`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1471.485043` ms, runtime inflation `0.007441`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.21578`, selector regret `0.14352`, runtime-adjusted gap `0.21578`.
- Family transfer `0.027632` and combined transfer `0.09695`.
- Runtime `561.677043` ms, runtime inflation `-0.615452`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand-2:restart2`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -2, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-conditioned selector over frozen TSP heuristic portfolio using structure descriptors (clusteredness, bottleneck, grid-likeness, corridor/elongation, and nearest-neighbor trap). Static one-shot decision (no online switching).", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.07, "name": "tsp_heuristic_portfolio_instance_adaptive_v1", "nearest_neighbor_trap_heuristic": "nearest_neighbor_multistart", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.045168` and combined transfer `0.107484`.
- Runtime `612.389671` ms, runtime inflation `-0.580732`, mean novelty `0.575945`, and complexity `1.98`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag4:cand1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": 1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler over frozen TSP heuristic portfolio with stagnation-triggered switching and bounded schedule tuning.", "determinism": {"schedule_policy": "fully_deterministic", "seed_policy": "derive_from_instance_hash", "tie_breaker": "lexicographic_by_portfolio_order_then_fixed_param_order"}, "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "det_tsp_hh_oracle_portfolio_v3", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "policy": {"deterministic_selection_order": ["nearest_neighbor_trap", "two_cluster_bottleneck", "corridor", "grid_like", "clustered", "default"], "online_schedule_rules": {"late_stage_refinement_preference": {"policy": "only allow stagnation_switch; avoid additional portfolio cycling; keep current heuristic otherwise.", "trigger_if": "time_budget_used >= (time_budget_trigger + 0.18)"}, "perturbation_escalation": {"escalate_to": {"else": "nearest_neighbor_trap_heuristic", "if_current_heuristic_contains": "two_opt", "then": "two_cluster_bottleneck_heuristic"}, "temperature_tuning": {"acceptance_bias": "acceptance_bias", "temperature_scale": "temperature_scale"}, "trigger_if": "failed_perturbation_count >= failed_perturbation_threshold AND time_budget_used >= time_budget_trigger"}, "stagnation_switch": {"offsets": {"candidate_limit_offset": "candidate_limit_offset if grid_likeness >= 0.25 else 0", "restart_offset": "restart_offset if time_budget_used >= 0.35 else 1"}, "switch_to": "stagnation_switch_heuristic", "trigger_if": "stagnation_length >= stagnation_threshold OR (recent_improvement_rate < low_improvement_threshold AND accepted_swaps == 0)"}}, "restart_budgeting": {"candidate_list_bias": "candidate_limit_offset if grid_likeness >= 0.25 else 0", "max_restarts": "1 + (restart_offset if stagnation_length >= 2 else 0)"}, "tests": {"clustered": {"heuristic": "clustered_heuristic", "use_if": "clustering-score >= 0.42 OR structure_class == 'clustered'"}, "corridor": {"heuristic": "corridor_heuristic", "use_if": "corridor_score >= 0.44 AND grid_likeness <= 0.18"}, "grid_like": {"heuristic": "grid_like_heuristic", "use_if": "grid_likeness >= 0.28 OR convex_hull_ratio <= 0.82"}, "nearest_neighbor_trap": {"heuristic": "nearest_neighbor_trap_heuristic", "use_if": "nearest-neighbor-trap-score >= 0.25 OR nn_distance_cv >= 0.62"}, "two_cluster_bottleneck": {"heuristic": "two_cluster_bottleneck_heuristic", "use_if": "bottleneck-score >= 0.50 OR structure_class == 'two_cluster_bottleneck'"}}, "tie_breaking": {"prefer_longer_horizon_when_time_rich": "if time_budget_used < time_budget_trigger then prefer multi-start styles: nearest_neighbor_multistart/annealed_multi_start else prefer cheaper/simpler: farthest_insertion_two_opt/candidate_pruned_two_opt", "prefer_more_specialized": true}}, "portfolio": {"heuristics": ["nearest_neighbor_trap_heuristic", "two_cluster_bottleneck_heuristic", "corridor_heuristic", "grid_like_heuristic", "clustered_heuristic", "random_like_heuristic", "default_heuristic"], "tuning_bounds": {"max_candidate_limit_multiplier": 3, "restart_multiplier_bounds": [0, 3], "temperature_multiplier_bounds": [0.6, 1.8]}}, "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.124043`, selector regret `0.051783`, runtime-adjusted gap `0.124043`.
- Family transfer `0.023034` and combined transfer `0.060248`.
- Runtime `837.051443` ms, runtime inflation `-0.426919`, mean novelty `0.839823`, and complexity `2.0325`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:farthest_insertion_two_opt:stag5:cand1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.009, "candidate_limit_offset": 1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic over frozen portfolio with bounded stagnation/candidate/restart/annealing adjustments; interpretable structure-driven selection with diversity-failure safeguards.", "determinism": {"seed_strategy": "deterministic_hash_from_instance_name_and_dimension", "selection_is_pure_function_of_features": true, "ties": "lexicographic_on_heuristic_roles"}, "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "det_bbmi_adaptive_portfolio_v3", "nearest_neighbor_trap_heuristic": "nearest_neighbor_multistart", "policy": {"base_selection": [{"then": "two_cluster_bottleneck_heuristic", "when": ["features.get('bottleneck_score',0.0) >= 0.6", "features.get('two_cluster_bottleneck_score',0.0) >= 0.4"]}, {"then": "clustered_heuristic", "when": ["features.get('clusteredness_score',0.0) >= 0.52", "features.get('grid_likeness',0.0) <= 0.3"]}, {"then": "grid_like_heuristic", "when": ["features.get('grid_likeness',0.0) >= 0.42", "features.get('convex_hull_ratio',0.0) >= 0.84"]}, {"then": "corridor_heuristic", "when": ["features.get('corridor_score',0.0) >= 0.45", "features.get('coordinate_spread_norm',0.0) <= 0.4"]}, {"then": "nearest_neighbor_trap_heuristic", "when": ["features.get('nearest_neighbor_trap_score',0.0) >= 0.3", "features.get('nn_distance_cv',0.0) >= 0.45"]}], "diversity_failure_mode": {"then": {"prefer_generalists_over_specialists": true, "selection_restriction": ["default_heuristic", "grid_like_heuristic", "two_cluster_bottleneck_heuristic"]}, "when": ["context.get('replay_mode','') == 'diversity_failure'", "context.get('failure_archive_size',0) >= 6"]}, "fallback": "default_heuristic", "tie_break": {"deterministic_order": ["default_heuristic", "grid_like_heuristic", "two_cluster_bottleneck_heuristic", "clustered_heuristic", "corridor_heuristic", "nearest_neighbor_trap_heuristic"]}}, "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "schedule": {"stagnation_rule": {"edge_skew_sensitive_bias": {"if_conditions": ["online.get('edge_length_skew_in_current_tour',0.0) >= 0.65"], "then": {"avoid_random_like_thrashing": true, "prefer_two_opt_stability": true}}, "perturbation_escalation": {"if_failed_perturbations": ["online.get('failed_perturbation_count',0) >= failed_perturbation_threshold"], "then": {"random_like_heuristic": "random_like_heuristic", "use_random_like_phase": true}}, "switch_to": "stagnation_switch_heuristic", "trigger_condition": ["online.get('stagnation_length',0) >= stagnation_threshold", "online.get('recent_improvement_rate',0.0) <= low_improvement_threshold"]}, "time_rule": {"then": {"annealing_adjustment": {"acceptance_bias": "acceptance_bias", "temperature_scale": "temperature_scale"}, "candidate_limit_offset": "candidate_limit_offset", "final_refinement_bias": true, "restart_offset": "restart_offset"}, "trigger_condition": ["online.get('time_budget_used',0.0) >= time_budget_trigger"]}}, "stagnation_switch_heuristic": "farthest_insertion_two_opt", "stagnation_threshold": 5, "temperature_scale": 1.25, "time_budget_trigger": 0.68, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `231.024057` ms, runtime inflation `-0.841831`, mean novelty `0.865434`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Summary of TSP Adaptive Heuristic Portfolio Suite Results

| Condition                          | Held-out TSPLIB Gap | Selector Regret vs Oracle | Runtime-adjusted Gap | Runtime Inflation | Pareto Efficient | Transfer Gap | Interpretation Highlights                                                     |
|----------------------------------|---------------------|---------------------------|---------------------|-------------------|------------------|--------------|------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic** (best_tsplib) | **0.07226**          | 0.0                       | 0.07226            | 0.0               | Yes              | 0.031222     | Best *static* fixed heuristic baseline (farthest_insertion_two_opt). No runtime overhead. Interpretable baseline for adaptive selectors. |
| **phase8_oracle_selector** (best_transfer)            | 0.07226              | 0.0 (definition)           | 0.07602            | +5.2%             | No               | 0.026678     | Non-deployable upper bound, sets target for selectors. Slight runtime inflation noted.                  |
| phase8_supervised_ml_selector     | 0.07226              | 0.0                       | 0.07280            | +0.74%            | No               | 0.031222     | Matches best fixed heuristic in held-out gap/runtime-adjusted gap with minimal runtime inflation. Interpretable ML-based control without runtime bloat.      |
| phase8_llm_static_selector        | 0.21578              | 0.144                     | 0.21578            | -61.5%            | No               | 0.09695      | Instance-conditioned static selector with substantial runtime savings but large gap increase, inferior to fixed heuristic baseline on primary endpoint.      |
| **phase8_llm_evolved_controller_diversity_failure_replay** | 0.12404              | 0.052                     | 0.12404            | -42.7%            | Yes              | 0.060248     | Adaptive controller with interpretable, structure-driven rules. Runtime reduced versus fixed heuristics but TSPLIB gap notably worse than fixed baseline. Some selector regret present but significantly lower than naive selectors. Reasonable transfer capability. |
| **phase8_random_portfolio**       | 0.22232              | 0.150                     | 0.22232            | -81.2%            | Yes              | 0.141005     | Naive baseline with poor gap but lowest runtime and Pareto efficient. Highest selector regret.             |
| phase8_llm_evolved_adaptive_controller | 0.21431              | 0.142                     | 0.21431            | -58.1%            | No               | 0.107484     | Complex adaptive controller with runtime savings but worse primary endpoint (TSPLIB gap) than fixed heuristic. Selector regret comparable to diversity-failure replay condition. |
| **phase8_full_solver_evolution**  | 0.21339              | 0.141                     | 0.21339            | -84.2%            | Yes              | 0.173523     | Evolved full solver with highest novelty but poor gap performance; Pareto efficient due to strong runtime reduction. Selector regret high. |

---

### Conservative Interpretation & Prioritized Conclusions

1. **Primary Endpoint (Held-out TSPLIB Gap):**  
   - The best fixed heuristic (`farthest_insertion_two_opt`) achieves the lowest held-out TSPLIB gap (0.07226), matched by the oracle and supervised selectors.  
   - Adaptive controllers reduce runtime significantly but at the cost of doubling or tripling TSPLIB gap (~0.12-0.21).  
   - Naive baselines (random portfolio, full solver evolution) have large gaps, not competitive for primary endpoint.

2. **Selector Regret vs Oracle:**  
   - Both the supervised selector and best fixed heuristic have zero selector regret (oracle-level performance).  
   - Adaptive controllers show modest selector regret (~0.05-0.14), indicating some suboptimal selections relative to the oracle.  
   - Random portfolio has highest regret (~0.15).

3. **Runtime-adjusted Gap & Runtime Inflation:**  
   - Best fixed heuristic runs in ~1460 ms with no inflation, achieving optimal gaps.  
   - Oracle selector modestly inflates runtime (+5%), supervised selector minimal (~+0.7%).  
   - Static LLM selector and adaptive controllers reduce runtime by ~40-60% but lose significant gap performance (trade-off).  
   - Random portfolio and full solver reduce runtime by ~80% but with severely worse gap.

4. **Pareto Efficiency:**  
   - The Pareto front includes best fixed heuristic, random portfolio, diversity-failure replay adaptive controller, and full solver.  
   - Oracle and supervised selectors do not belong to Pareto front likely due to runtime inflation or complexity.

5. **Cross-family Transfer:**  
   - Transfer gaps generally align with main gap results; best fixed heuristic and supervised selector transfer well (~0.03 gap).  
   - Adaptive controllers show moderate transfer gaps (~0.06-0.1), indicating some robustness but not yet matching oracle-level transfer.  
   - Random portfolio and full solver have poor transfer.

6. **Interpretable Instance-adaptive Control:**  
   - The **phase8_llm_evolved_controller_diversity_failure_replay** condition provides a good balance:  
     - Interpretable, deterministic structure-driven adaptive control.  
     - Significant runtime savings (~43%) compared to fixed heuristic.  
     - Moderate increase in held-out gap (0.12 vs 0.07).  
     - Low selector regret relative to oracle (0.05).  
     - Pareto efficient, indicating a meaningful trade-off.  
   - The supervised selector matches oracle-level gap with minimal overhead but is not Pareto efficient and less runtime-efficient.  
   - The purely static LLM selector has too large gap degradation despite runtime gains.

---

### Final Recommendations

- For practical deployment prioritizing best solution quality, **the best single fixed heuristic (`farthest_insertion_two_opt`) or supervised ML selector** are preferred due to oracle-level performance and minimal runtime overhead.  
- If runtime is constrained and interpretable adaptive control is desired, the **evolved adaptive controller with diversity-failure replay** represents a reasonable compromise, offering runtime savings with tolerable TSPLIB gap increase and low selector regret.  
- Avoid overclaiming new algorithm discoveries; improvements are due to **instance-adaptive hyper-heuristic control over known heuristics**.  
- The oracle selector remains a useful theoretical upper bound but is not deployable.  
- Further tuning may focus on closing the gap-runtime trade-off, improving transfer robustness, and refining interpretable adaptation without runtime inflation.
