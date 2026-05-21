# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_llm_static_selector.

## Run Metadata
- run_name: run_20260520_195202_h
- started_at_local: 2026-05-20 19:52:02
- finished_at_local: 2026-05-20 20:27:58
- duration_hhmm: 00:36
- duration_seconds: 2156.549
- seed_offset: 7000
- replicate_label: h
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1463.164843 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.189641 | 0.117381 | 1493.831657 | 0.193616 | 0.038767 | 0.094352 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1490.476029 | 0.073609 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1521.140557 | 0.075123 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.229271 | 0.157011 | 273.494286 | 0.229271 | 0.068101 | 0.127479 | 0.0 | 0.62 | True |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 391.322871 | 0.214311 | 0.045168 | 0.107484 | 0.772579 | 2.1175 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.120261 | 0.048001 | 7723.547714 | 0.634817 | 0.001857 | 0.045479 | 0.722823 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.07918 | 0.00692 | 509.750157 | 0.07918 | 0.010298 | 0.035675 | 0.548573 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1463.164843` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.189641`, selector regret `0.117381`, runtime-adjusted gap `0.193616`.
- Family transfer `0.038767` and combined transfer `0.094352`.
- Runtime `1493.831657` ms, runtime inflation `0.020959`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.073609`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1490.476029` ms, runtime inflation `0.018666`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.075123`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1521.140557` ms, runtime inflation `0.039624`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.229271`, selector regret `0.157011`, runtime-adjusted gap `0.229271`.
- Family transfer `0.068101` and combined transfer `0.127479`.
- Runtime `273.494286` ms, runtime inflation `-0.81308`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic, instance-conditioned frozen-portfolio selector that favors farthest-insertion+2opt generally, then switches to cluster/bottleneck/grid/corridor aware constructions. Includes bounded online-style tuning parameters for the selected schedule but no", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "det_tsp_portfolio_oracle_approach_static_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.045168` and combined transfer `0.107484`.
- Runtime `391.322871` ms, runtime inflation `-0.73255`, mean novelty `0.772579`, and complexity `2.1175`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag3:cand1:restart0`.
- Controller rule summary: {"acceptance_bias": 0.007, "candidate_limit_offset": 1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler over a frozen heuristic portfolio with bounded online switching and interpretable tuning offsets.", "failed_perturbation_threshold": 3, "finalization_policy": {"determinism": "All choices are deterministic functions of instance descriptors and current online state; no random sampling is performed by this controller.", "rule": "At the end of budget, or after any controller switch, do only one final compact refinement consistent with the currently selected heuristic; do not allow additional controller-level switches in the same decision step."}, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.09, "name": "tsp_hh_oracle_portfolio_transfer_v3", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 0, "selection_rules": {"initial_construction_choice": [{"choose": "edge_preserving_restart", "when": "bottleneck_score >= 0.58 or two_cluster_bottleneck_score >= 0.48"}, {"choose": "cluster_first_local_search", "when": "clustering_score >= 0.56 and cluster_separation >= 0.30 and convex_hull_ratio >= 0.88"}, {"choose": "candidate_pruned_two_opt", "when": "grid_likeness >= 0.30"}, {"choose": "limited_three_opt", "when": "corridor_score >= 0.45 or elongated_structure >= 0.44"}, {"choose": "annealed_multi_start", "when": "nearest_neighbor_trap_score >= 0.34 or nn_distance_cv >= 0.68"}, {"choose": "farthest_insertion_two_opt", "when": "True"}], "instance_condition_tuning": [{"action": "candidate_limit_offset = clamp(candidate_limit_offset + 2, -6, 6) to tighten pruning for grid-like structure.", "when": "grid_likeness >= 0.30"}, {"action": "candidate_limit_offset = clamp(candidate_limit_offset + 1, -6, 6) to avoid over-pruning on non-grid instances.", "when": "grid_likeness < 0.14 and candidate_limit_offset < 1"}, {"action": "restart_offset = clamp(restart_offset + 1, -3, 4) to increase restart pressure on bottleneck/two-cluster layouts.", "when": "bottleneck_score >= 0.60"}, {"action": "restart_offset = clamp(restart_offset - 1, -3, 4) to reduce excessive restart churn on well-mixed instances.", "when": "bottleneck_score < 0.35"}, {"action": "temperature_scale = clamp(temperature_scale * 0.98, 0.5, 1.8); acceptance_bias = clamp(acceptance_bias + 0.001, -0.01, 0.02) to stabilize on well-shaped clustered instances.", "when": "clustering_score >= 0.56 and convex_hull_ratio >= 0.88"}, {"action": "temperature_scale = clamp(temperature_scale * 1.10, 0.5, 1.8); acceptance_bias = clamp(acceptance_bias + 0.003, -0.01, 0.02) to broaden acceptance under higher distance variance.", "when": "distance_cv >= 0.52 and distance_mean_norm >= 0.25"}, {"action": "candidate_limit_offset = clamp(candidate_limit_offset + 1, -6, 6) to exploit stable nearest-neighbor structure.", "when": "nn_distance_variance_norm <= 0.0012"}, {"action": "temperature_scale = clamp(temperature_scale * 1.06, 0.5, 1.8); acceptance_bias = clamp(acceptance_bias + 0.001, -0.01, 0.02) to escape trap-like layouts.", "when": "nearest_neighbor_trap_score >= 0.34"}, {"action": "acceptance_bias = clamp(acceptance_bias + 0.001, -0.01, 0.02) to nudge exploration during mild stagnation.", "when": "stagnation_length >= 2 and edge_length_skew <= 0.55"}], "online_scheduling_choice": [{"phase": "early", "rule": "if time_budget_used < time_budget_trigger: keep current heuristic; only allow its built-in local improvement (no controller switch unless failed perturbation triggers)."}, {"phase": "failed_perturbation_escape", "rule": "if failed_perturbation_count >= failed_perturbation_threshold: switch to random_like_heuristic (one switch max per decision step)."}, {"phase": "stagnation_recovery", "rule": "if stagnation_length >= stagnation_threshold and recent_improvement_rate <= low_improvement_threshold and edge_length_skew <= 0.66: switch to stagnation_switch_heuristic."}, {"phase": "time_pressure", "rule": "if time_budget_used >= time_budget_trigger and (recent_improvement_rate <= low_improvement_threshold or non_improving_streak >= stagnation_threshold - 1) and edge_length_skew <= 0.62: switch to random_like_heuristic."}, {"phase": "extreme_skew_protection", "rule": "if edge_length_skew > 0.66: do not switch heuristics; keep current heuristic for stability."}]}, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.12, "time_budget_trigger": 0.65, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.634817`.
- Family transfer `0.001857` and combined transfer `0.045479`.
- Runtime `7723.547714` ms, runtime inflation `4.278659`, mean novelty `0.722823`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand-3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.0, "candidate_limit_offset": -3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic controller selecting from a frozen portfolio using structure cues (cluster/grid/bottleneck/corridor/trap) and conservative online switching under stagnation and perturbation failure; biases toward farthest-insert", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "deterministic_instance_adaptive_tsp_hh_v5", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.25, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.07918`, selector regret `0.00692`, runtime-adjusted gap `0.07918`.
- Family transfer `0.010298` and combined transfer `0.035675`.
- Runtime `509.750157` ms, runtime inflation `-0.651611`, mean novelty `0.548573`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
```markdown
# TSP Adaptive Heuristic Portfolio Suite - Conservative Result Interpretation

## Primary Endpoint: Held-out TSPLIB Gap

- The best held-out TSPLIB gap (0.07226) is achieved by the **best single fixed heuristic** ("farthest_insertion_two_opt").
- The **oracle selector** achieves the same TSPLIB gap (0.07226), marking this as a performance upper bound.
- The **supervised ML selector** also reaches 0.07226 gap but with slightly higher runtime inflation.
- Adaptive controllers yield higher TSPLIB gaps (e.g., 0.214 for the "llm_evolved_adaptive_controller") than the best fixed heuristic, indicating performance degradation from adaptive selection on this metric.

## Selector Regret vs Oracle Portfolio

- Best single fixed heuristic and supervised ML selectors show zero selector regret, matching the oracle on TSPLIB gap.
- Adaptive controllers show notable selector regret (0.142 for "llm_evolved_adaptive_controller"), implying suboptimal heuristic choices compared to oracle.
- Random portfolios show the highest selector regret (0.117 initially), which aligns with poor TSPLIB gap results.

## Runtime-Adjusted Gap & Runtime Inflation

- The best fixed heuristic and oracle selector show similar runtime-adjusted gaps (~0.073) with negligible runtime inflation.
- Adaptive controllers reduce runtime (runtime inflation negative, e.g. −0.73 for "llm_evolved_adaptive_controller") but at cost of increased gap (0.214).
- One adaptive variant ("llm_evolved_controller_diversity_failure_replay") shows large runtime inflation (4.28) and worse adjusted gap (0.635), which is not Pareto efficient.
- The static selector ("llm_static_selector") runs very fast (273 ms, much lower than ~1500 ms for fixed heuristic) but incurs higher gap (0.229) and negative runtime inflation (−0.81), showing efficiency in speed but worse solution quality.

## Pareto Efficiency and Complexity

- Pareto efficient conditions include:
  - Best single fixed heuristic (simple, no adaptation, best gap)
  - Full solver evolution (moderate gap 0.079, reduced runtime)
  - LLM evolved adaptive controller (higher gap but substantial runtime reduction)
  - LLM static selector (fastest runtime, higher gap)
- Adaptive controllers have moderate complexity (0.62) and interpretable tuning rules, indicating structured instance-adaptive control.

## Cross-Family Transfer Performance

- Transfer gaps are lowest for oracle selector (0.0267) and best single heuristic (0.0312), supporting robust cross-family transfer.
- Adaptive controllers show higher transfer gap (0.107 - 0.127), indicating some loss of generality or robustness.
- Random portfolio and static selector have higher transfer gaps, consistent with poorer control policies.

---

## Summary and Recommendations

- **Best single fixed heuristic ("farthest_insertion_two_opt") remains the strongest performer on held-out TSPLIB gap, matching oracle selector without runtime overhead.**
- **Adaptive selectors, especially the evolved LLM adaptive controller, provide notable runtime savings (roughly 2-4x speedup) but currently at a significant cost in solution quality (larger TSPLIB gap and selector regret).**
- The **static LLM-based selector is very fast but yields high gap**, making it Pareto efficient only where runtime dominates.
- Adaptive controllers demonstrate interpretable instance-adaptive scheduling with well-defined selection and tuning rules; however, their gap-to-runtime tradeoff suggests further tuning or hybrid strategies may be needed.
- Cross-family transfer favors fixed heuristics and oracle-like selectors; adaptive controllers show some vulnerability here.
- No new algorithm discoveries are evident; improvements stem from hyper-heuristic control over known heuristics.
- Deployment should prioritize either best fixed heuristic for quality or adaptive controllers if runtime constraints dominate and some quality loss is acceptable.

---

### Interpretation Priorities Addressed:

| Criterion                  | Best Single Fixed | Oracle Selector | LLM Evolved Adaptive Controller | LLM Static Selector | Random Portfolio  |
|----------------------------|-------------------|-----------------|---------------------------------|---------------------|-------------------|
| Held-out TSPLIB gap        | **0.07226 (best)**| 0.07226         | 0.214 (worse)                   | 0.229 (worse)       | 0.189 (worse)     |
| Selector regret vs oracle  | 0                 | 0 (oracle)      | 0.142 (notable regret)           | 0.157 (high regret) | 0.117             |
| Runtime-adjusted gap       | ~0.072            | 0.0736          | 0.214 (higher)                  | 0.229 (higher)      | 0.193             |
| Runtime inflation          | 0                 | +0.019          | −0.73 (faster)                  | −0.81 (faster)      | +0.02             |
| Pareto efficiency          | Yes               | No              | Yes                            | Yes                 | No                |
| Cross-family transfer gap  | 0.031             | 0.027           | 0.107                          | 0.127               | 0.094             |

---

### Final Conservative Conclusion

- The frozen best single heuristic presents a baseline with the best held-out performance and no runtime inflation.
- The oracle selector validates this baseline as an upper bound but is not deployable.
- The adaptive LLM evolved controller shows promise in runtime savings with clear instance-adaptive control but needs improvement to approach oracle performance without excessive gap.
- Static and random portfolios underperform on gap and have weaker transfer.
- Future work should focus on improving instance-adaptive selection accuracy and preserving solution quality while maintaining runtime benefits.

```
