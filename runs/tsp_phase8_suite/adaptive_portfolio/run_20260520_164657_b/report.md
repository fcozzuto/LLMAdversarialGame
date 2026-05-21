# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_164657_b
- started_at_local: 2026-05-20 16:46:57
- finished_at_local: 2026-05-20 17:26:44
- duration_hhmm: 00:40
- duration_seconds: 2386.581
- seed_offset: 1000
- replicate_label: b
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1472.465143 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.18258 | 0.11032 | 445.345514 | 0.18258 | 0.085372 | 0.121185 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1483.437971 | 0.072798 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1563.561671 | 0.07673 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.214311 | 0.142051 | 471.443086 | 0.214311 | 0.053836 | 0.112958 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.084733 | 0.012473 | 4200.622143 | 0.241725 | 0.021201 | 0.044607 | 0.0 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.120261 | 0.048001 | 10916.496586 | 0.891586 | 0.090132 | 0.101232 | 0.181687 | 0.69 | False |
| phase8_full_solver_evolution | full_solver | none | 0.203742 | 0.131482 | 291.650157 | 0.203742 | 0.011221 | 0.08215 | 0.0 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1472.465143` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.18258`, selector regret `0.11032`, runtime-adjusted gap `0.18258`.
- Family transfer `0.085372` and combined transfer `0.121185`.
- Runtime `445.345514` ms, runtime inflation `-0.697551`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072798`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1483.437971` ms, runtime inflation `0.007452`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07673`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1563.561671` ms, runtime inflation `0.061867`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.053836` and combined transfer `0.112958`.
- Runtime `471.443086` ms, runtime inflation `-0.679827`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:limited_three_opt:candidate_pruned_two_opt:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-conditioned selector over a frozen portfolio; picks backbone + refinement family based on structure descriptors (grid/bottleneck/cluster/corridor/trap) with conservative shared schedule tuning knobs.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "tsp_hh_static_interpretable_selector_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "candidate_pruned_two_opt", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.241725`.
- Family transfer `0.021201` and combined transfer `0.044607`.
- Runtime `4200.622143` ms, runtime inflation `1.852782`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag3:cand2:restart2`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "candidate_pruned_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller selecting from a frozen TSP heuristic portfolio with bounded stagnation-triggered schedule tuning.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "cheapest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "tsphh_portfolio_interpretable_v1", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.12, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.891586`.
- Family transfer `0.090132` and combined transfer `0.101232`.
- Runtime `10916.496586` ms, runtime inflation `6.413756`, mean novelty `0.181687`, and complexity `0.69`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag2:cand0:restart2`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": 0, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller using frozen heuristic portfolio. Structure-gated backbone selection (cluster/grid/bottleneck/corridor/trap) with stagnation-aware switching and bounded schedule tuning to improve held-out transfer.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.06, "name": "tsp_hh_oracle_portfolio_interpretable_epoch4_deterministic", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 2, "temperature_scale": 1.15, "time_budget_trigger": 0.45, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.203742`, selector regret `0.131482`, runtime-adjusted gap `0.203742`.
- Family transfer `0.011221` and combined transfer `0.08215`.
- Runtime `291.650157` ms, runtime inflation `-0.801931`, mean novelty `0.0`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

#### Primary Endpoint: Held-out TSPLIB Gap
- **Best Single Fixed Heuristic ("farthest_insertion_two_opt")** achieves the lowest held-out TSPLIB gap: **0.07226**.
- The **Oracle Selector** matches this gap at **0.07226**, serving as an unattainable upper bound.
- Other adaptive or learned selectors (e.g., supervised ML, LLM static/adaptive controllers) have notably worse gaps (≥0.0767 and up to 0.2143), failing to improve upon the best fixed heuristic baseline on held-out TSPLIB.

#### Selector Regret vs. Oracle Portfolio
- The best fixed heuristic has zero selector regret (by definition).
- The supervised ML selector also reaches zero regret, closely matching the best heuristic.
- Adaptive controllers show some selector regret (e.g., 0.0125 for evolved adaptive controller, 0.048 for replay), indicating they mispredict or inefficiently select heuristics relative to the oracle.
- The static and random portfolio selectors have higher selector regret (≥0.11), reflecting less effective adaptation.

#### Runtime-Adjusted Gap & Runtime Inflation
- The best single fixed heuristic baseline has no runtime inflation and moderate runtime-adjusted gap (0.0723).
- The oracle selector nearly matches this runtime-adjusted gap with negligible inflation (+0.75%).
- The supervised ML selector incurs slight runtime inflation (~6%) with slightly worse gap.
- The adaptive controllers incur substantial runtime inflation (e.g., 185% for evolved adaptive, 641% for replay), with larger runtime-adjusted gaps (0.24 to 0.89), indicating expensive overheads that diminish practical benefit.
- The static LLM selector and random portfolio have negative runtime inflation (faster than baseline) but much worsened runtime-adjusted gaps due to poorer solution quality.

#### Pareto Efficiency
- Pareto-efficient conditions (in terms of gap and complexity) are:
  - Best Single Fixed Heuristic
  - Full Solver Evolution (gap 0.20, runtime-inflation -80%)
  - Random Portfolio (gap 0.18, runtime-inflation -70%)
- Adaptive selectors are **not** Pareto efficient here, due to high runtime inflation and modest quality improvements.

#### Cross-Family Transfer (Transfer Gap)
- Best fixed and supervised selectors have transfer gaps ~0.031, indicating moderate robustness across instance families.
- Adaptive controllers show higher but still moderate transfer gaps (0.04 – 0.10).
- Oracle selector transfer gap is lowest (0.027), as expected.
- The random and static selectors show the largest transfer gaps (0.11 – 0.12), consistent with poorer generalization.

---

### Summary & Recommendations

- The **best single fixed heuristic ("farthest_insertion_two_opt") provides a strong, interpretable baseline** with excellent held-out TSPLIB gap, zero selector regret, no runtime inflation, and Pareto efficiency.
- The **oracle selector confirms this baseline is near-optimal**, justifying conservative claims that high adaptivity or hyper-heuristic control has limited room to improve held-out gap.
- **Supervised ML selector matches held-out performance closely but with mild runtime inflation**; it demonstrates that learning-based control can approach best fixed heuristic performance without excessive overhead, supporting interpretable instance-adaptive selection.
- **Adaptive controllers deliver moderate quality improvements within family but incur large runtime overheads and higher selector regret**, undermining practical benefits on held-out TSPLIB; careful tuning needed before deployment.
- **Static selectors and random portfolios are generally inferior**, with larger gaps and higher regret; they offer less interpretable or instance-adaptive control.
- This phase supports hyper-heuristic control focused on **interpretable, bounded adaptation over known heuristics**, rather than discovery of new heuristics.
- Further work should prioritize **runtime-efficient adaptive control that closely matches or improves on the best fixed heuristic in held-out benchmarks** before claims of deployment-ready adaptivity.

---

**In conclusion**, the current portfolio suite’s best static heuristic and supervised selectors show promise for interpretable instance-adaptive control with conservative runtime cost. More aggressive adaptation, while improving some metrics, introduces excessive runtime inflation and selector regret on held-out TSPLIB tasks, limiting practical gains.
