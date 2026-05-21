# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_llm_static_selector, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_182519_e
- started_at_local: 2026-05-20 18:25:19
- finished_at_local: 2026-05-20 18:55:09
- duration_hhmm: 00:30
- duration_seconds: 1790.296
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1478.632943 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.238028 | 0.165768 | 204.906786 | 0.238028 | 0.060063 | 0.125629 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1515.764186 | 0.074075 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1622.641086 | 0.079298 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.229271 | 0.157011 | 265.383486 | 0.229271 | 0.045605 | 0.113271 | 0.0 | 0.62 | True |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.214311 | 0.142051 | 506.734 | 0.214311 | 0.023333 | 0.093693 | 0.426878 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.203034 | 0.130774 | 302.534086 | 0.203034 | 0.063338 | 0.114805 | 0.811584 | 1.19 | False |
| phase8_full_solver_evolution | full_solver | none | 0.165894 | 0.093634 | 301.039157 | 0.165894 | 0.010006 | 0.067438 | 0.0 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1478.632943` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.238028`, selector regret `0.165768`, runtime-adjusted gap `0.238028`.
- Family transfer `0.060063` and combined transfer `0.125629`.
- Runtime `204.906786` ms, runtime inflation `-0.861421`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.074075`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1515.764186` ms, runtime inflation `0.025112`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.079298`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1622.641086` ms, runtime inflation `0.097393`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.229271`, selector regret `0.157011`, runtime-adjusted gap `0.229271`.
- Family transfer `0.045605` and combined transfer `0.113271`.
- Runtime `265.383486` ms, runtime inflation `-0.820521`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.005, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-conditioned frozen-portfolio selector targeting farthest-insertion + 2-opt for general performance, with structure-aware fallbacks for clustered/grid/bottleneck/corridor and nearest-neighbor traps. Heuristic-specific schedule tuning uses", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "det_tsp_hh_oracle_portfolio_like_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.1, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.023333` and combined transfer `0.093693`.
- Runtime `506.734` ms, runtime inflation `-0.657296`, mean novelty `0.426878`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:farthest_insertion_two_opt:farthest_insertion_two_opt:nearest_neighbor_multistart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": 2, "clustered_heuristic": "farthest_insertion_two_opt", "corridor_heuristic": "farthest_insertion_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive portfolio router with stagnation-triggered switching and bounded schedule tuning over the frozen heuristic set.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.1, "name": "tsp_hh_controller_deterministic_structure_switching_v3", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.2, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.203034`, selector regret `0.130774`, runtime-adjusted gap `0.203034`.
- Family transfer `0.063338` and combined transfer `0.114805`.
- Runtime `302.534086` ms, runtime inflation `-0.795396`, mean novelty `0.811584`, and complexity `1.19`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:limited_three_opt:stag4:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.004, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "candidate_pruned_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive frozen-portfolio controller using structure-aware heuristic role mapping and a conservative stagnation switch to avoid diversity-collapse during replay.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "cheapest_insertion_two_opt", "low_improvement_threshold": 0.12, "name": "tsp_hh_frozen_portfolio_v4_deterministic_instance_adaptive", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "limited_three_opt", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.68, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.165894`, selector regret `0.093634`, runtime-adjusted gap `0.165894`.
- Family transfer `0.010006` and combined transfer `0.067438`.
- Runtime `301.039157` ms, runtime inflation `-0.796407`, mean novelty `0.0`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Suite Results

#### Primary Endpoint: Held-Out TSPLIB Gap
- **Best performance:**  
  - *phase8_best_single_fixed_heuristic* achieves the lowest held-out TSPLIB gap (0.07226).  
  - *phase8_oracle_selector* matches this TSPLIB gap (0.07226) but is not deployable (oracle upper bound).  
- **Adaptive & static selectors:**  
  - *phase8_llm_evolved_adaptive_controller* shows moderately higher TSPLIB gap (0.21431), about 3x worse than the best fixed heuristic.  
  - *phase8_llm_static_selector* has even higher gap (0.22927).  
  - *phase8_full_solver_evolution* intermediate at (0.16589).  
- **Random portfolio* is substantially worse (0.23803).

#### Selector Regret vs Oracle Portfolio
- Oracle selector has zero regret (by definition).  
- *Best single fixed heuristic* has zero regret (it is fixed).  
- Adaptive controllers and static selector incur positive selector regret (~0.13–0.16), indicating imperfect adaptivity relative to oracle.  
- *phase8_full_solver_evolution* shows lower regret (0.0936) than adaptive controllers but worse gap than fixed heuristic.

#### Runtime-Adjusted Gap and Runtime Inflation
- The best single fixed heuristic has runtime-adjusted gap 0.07226 with **no runtime inflation** (baseline).  
- Oracle selector's runtime inflation is marginal (2.5%), maintaining similar runtime-adjusted gap (~0.074).  
- Adaptive controller (*phase8_llm_evolved_adaptive_controller*), while having higher gap, reduces runtime compared to baseline (~-65.7% runtime inflation), resulting in moderate runtime-adjusted gap (0.2143).  
- Static selector and random portfolio get lower runtime (negative runtime inflation >80%) but at cost of much worse gap (~0.23 and 0.24).  
- *phase8_full_solver_evolution* balances runtime inflation (-79.6%) with moderate gap (0.1659).

#### Pareto Efficiency
- Pareto-efficient conditions include:  
  - *phase8_best_single_fixed_heuristic* (best gap, zero inflation)  
  - *phase8_full_solver_evolution* (good gap/runtime tradeoff)  
  - *phase8_llm_evolved_adaptive_controller* (adaptive, runtime savings)  
  - *phase8_llm_static_selector* (static selector, runtime savings at cost of gap)  
  - *phase8_random_portfolio* (runtime efficient but poor gap)  
- Oracle selector is **not Pareto efficient**, likely due to higher runtime inflation without gap improvement over best fixed heuristic.

#### Cross-Family Transfer Gap
- Transfer gaps (generalization from training families to held-out TSPLIB) are smallest for:  
  - Oracle selector (0.0267)  
  - Best single fixed heuristic (0.0312)  
- Adaptive controllers exhibit higher transfer gaps (~0.09–0.11) indicating less robust cross-family generalization.  
- Static and random selectors have highest transfer gaps (0.11+).

---

### Summary and Recommendations

- The **best single fixed heuristic (farthest_insertion_two_opt)** remains a strong baseline with best held-out TSPLIB gap (0.07226), zero selector regret, no runtime inflation, and good transfer gap; it is Pareto efficient.
- The **oracle selector**, while an idealized upper bound, matches this gap with slight runtime inflation and thus serves as a useful performance ceiling.
- **Adaptive controllers** (*phase8_llm_evolved_adaptive_controller*) achieve meaningful runtime reduction (>60% runtime savings) but with increased TSPLIB gap (~0.21) and moderate selector regret (~0.14). This indicates runtime-performance tradeoffs in instance-adaptive hyper-heuristic control.
- The **static selector** achieves large runtime gains but at considerable accuracy loss (gap ~0.23) and selector regret (~0.16), limiting interpretability and practical appeal.
- **Cross-family transfer robustness** is best approached by fixed heuristics and oracle selectors, while adaptive controllers lag behind, suggesting limitations in generalization.
- No condition unambiguously outperforms the best single fixed heuristic on the primary endpoint without runtime cost inflation.
- Thus, current results support emphasizing **interpretable instance-adaptive control that approaches the oracle/benchmark gap without excessive runtime inflation**, rather than claims of discovering new heuristics.
- Future work might focus on narrowing the gap of adaptive selectors while preserving their runtime efficiency and cross-family robustness.

---

### Concise key points:

| Condition                          | TSPLIB Gap | Runtime-Adjusted Gap | Runtime Inflation | Selector Regret | Transfer Gap | Pareto Efficient | Notes                                             |
|----------------------------------|------------|---------------------|-------------------|-----------------|--------------|------------------|---------------------------------------------------|
| phase8_best_single_fixed_heuristic | **0.07226** | 0.07226             | 0.0               | 0.0             | 0.0312       | Yes              | Strong baseline, no runtime cost                  |
| phase8_oracle_selector            | 0.07226    | 0.07407             | +2.5%             | 0.0             | 0.0267       | No               | Ideal upper bound, not deployable                  |
| phase8_llm_evolved_adaptive_controller | 0.21431    | 0.21431             | -65.7%            | 0.142           | 0.0937       | Yes              | Runtime-efficient adaptive control, gap tradeoff |
| phase8_full_solver_evolution      | 0.16589    | 0.16589             | -79.6%            | 0.094           | 0.0674       | Yes              | Balanced runtime/performance                        |
| phase8_llm_static_selector        | 0.22927    | 0.22927             | -82.1%            | 0.157           | 0.1133       | Yes              | Static selector, runtime gain but gap loss         |
| phase8_random_portfolio           | 0.23803    | 0.23803             | -86.1%            | 0.166           | 0.126        | Yes              | Poor gap, no adaptation                             |

---

**Conclusion:**  
The best fixed heuristic remains the conservative choice for TSP on TSPLIB benchmarks. Instance-adaptive hyper-heuristic control shows promise in runtime reduction but requires further tuning to close the performance gap without sacrificing interpretability or transfer robustness.
