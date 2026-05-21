# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_full_solver_evolution`.
- Best combined transfer gap: `phase8_full_solver_evolution`.
- Lowest selector regret: `phase8_full_solver_evolution`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_random_portfolio, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260521_000102_s
- started_at_local: 2026-05-21 00:01:02
- finished_at_local: 2026-05-21 00:33:43
- duration_hhmm: 00:33
- duration_seconds: 1960.041
- seed_offset: 18000
- replicate_label: s
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1481.613257 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.141534 | 0.069274 | 295.251714 | 0.141534 | 0.065695 | 0.093636 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1506.255043 | 0.073462 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1475.330914 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.21578 | 0.14352 | 439.288357 | 0.21578 | 0.133367 | 0.16373 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.084733 | 0.012473 | 4081.4391 | 0.233416 | 0.015088 | 0.040747 | 0.146159 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.084733 | 0.012473 | 4085.646214 | 0.233657 | 0.014551 | 0.040407 | 0.494316 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.072172 | -8.8e-05 | 461.409171 | 0.072172 | 0.0 | 0.02659 | 0.785065 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1481.613257` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.141534`, selector regret `0.069274`, runtime-adjusted gap `0.141534`.
- Family transfer `0.065695` and combined transfer `0.093636`.
- Runtime `295.251714` ms, runtime inflation `-0.800723`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.073462`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1506.255043` ms, runtime inflation `0.016632`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1475.330914` ms, runtime inflation `-0.00424`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.21578`, selector regret `0.14352`, runtime-adjusted gap `0.21578`.
- Family transfer `0.133367` and combined transfer `0.16373`.
- Runtime `439.288357` ms, runtime inflation `-0.703507`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:edge_preserving_restart:candidate_pruned_two_opt:stag4:cand-2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -2, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "cluster_first_local_search", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-conditioned frozen-portfolio selector tuned for general EUC_2D structure with bottleneck and grid/corridor awareness.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.07, "name": "tsp_hh_oracle_compass_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "candidate_pruned_two_opt", "stagnation_threshold": 4, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.233416`.
- Family transfer `0.015088` and combined transfer `0.040747`.
- Runtime `4081.4391` ms, runtime inflation `1.754726`, mean novelty `0.146159`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:limited_three_opt:annealed_multi_start:stag4:cand-2:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Interpretable instance-adaptive scheduler over a frozen heuristic portfolio with conservative stagnation and perturbation control.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "deterministic_instance_adaptive_tsp_hh_v3", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.35, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.233657`.
- Family transfer `0.014551` and combined transfer `0.040407`.
- Runtime `4085.646214` ms, runtime inflation `1.757566`, mean novelty `0.494316`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:limited_three_opt:edge_preserving_restart:stag3:cand-3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.012, "candidate_limit_offset": -3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "cluster_first_local_search", "default_heuristic": "farthest_insertion_two_opt", "description": "Interpretable instance-adaptive frozen-portfolio controller with earlier diversification and conservative specialization under diversity-failure replay.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "deterministic_instance_adaptive_tsp_hh_v3", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 2, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.35, "time_budget_trigger": 0.45, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.072172`, selector regret `-8.8e-05`, runtime-adjusted gap `0.072172`.
- Family transfer `0.0` and combined transfer `0.02659`.
- Runtime `461.409171` ms, runtime inflation `-0.688577`, mean novelty `0.785065`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

| Metric                         | phase8_best_single_fixed_heuristic | phase8_oracle_selector | phase8_supervised_ml_selector | phase8_llm_evolved_adaptive_controller | phase8_full_solver_evolution |
|-------------------------------|------------------------------------|-----------------------|-------------------------------|----------------------------------------|------------------------------|
| **Held-out TSPLIB gap**        | 0.07226                            | 0.07226               | 0.07226                       | 0.08473                               | **0.07217**                  |
| **Selector regret vs oracle** | 0.0                               | 0.0                   | 0.0                           | 0.01247                              | **-8.8e-05**                 |
| **Runtime-adjusted gap**       | 0.07226                            | 0.07346               | 0.07226                       | 0.23342                              | **0.07217**                  |
| **Runtime inflation**          | 0.0                               | 0.01663               | -0.00424                     | 1.75                                 | **-0.69**                   |
| **Final transfer gap**         | 0.03122                           | 0.02668              | 0.03122                      | 0.04075                             | **0.02659**                  |
| **Pareto efficient**           | No                                | No                    | Yes                          | No                                   | Yes                         |
| **Mean complexity**            | 0.0                               | 0.0                   | 0.0                           | 0.62                                 | 0.76                        |

---

### Key Points

1. **Primary Endpoint (Held-out TSPLIB gap):**  
   - The *phase8_full_solver_evolution* condition achieves the lowest held-out gap (0.07217), marginally better than the oracle selector and best single heuristic (both 0.07226).  
   - This suggests it closely approximates oracle performance on TSPLIB instances, the main evaluation criterion.

2. **Selector Regret vs Oracle:**  
   - *phase8_full_solver_evolution* also shows negligible negative regret (-8.8e-05), effectively matching oracle selector performance in selection quality.  
   - Adaptive controllers have small positive regret, indicating slightly worse than oracle but still relatively close.

3. **Runtime-Adjusted Gap & Runtime Inflation:**  
   - *phase8_full_solver_evolution* has runtime-adjusted gap comparable to best single heuristic and supervised ML selector but with **substantial runtime reduction (–69%)** relative to oracle selector, indicating efficient performance without runtime inflation.   
   - Adaptive controllers show notably higher runtime inflation (~1.75x) and significantly worse runtime-adjusted gaps (~0.23), which limits their deployability despite their adaptivity.

4. **Pareto Efficiency:**  
   - *phase8_full_solver_evolution*, the supervised ML selector, and the random portfolio lie on the Pareto frontier balancing solution quality and runtime metrics.  
   - Static or adaptive selectors that approach oracle accuracy without excessive runtime inflation are prioritized; here, *phase8_full_solver_evolution* best meets this.

5. **Cross-Family Transfer (Transfer Gap):**  
   - *phase8_full_solver_evolution* exhibits the lowest transfer gap (0.02659), indicating better generalization across TSP families compared to others, including adaptive controllers and best fixed heuristic.

6. **Adaptation & Controller Interpretability:**  
   - Adaptive controllers show modest adaptation efficiency but suffer in runtime cost and final TSPLIB gap.  
   - *phase8_full_solver_evolution*, although more complex (complexity = 0.76), provides interpretable instance-adaptive hyper-heuristic control with strong performance and low runtime inflation.  
   - No novel algorithms discovered; improvements stem from effective hyper-heuristic control over known heuristics.

---

### Summary

- **The *phase8_full_solver_evolution* condition is the most balanced and effective approach**, achieving the best held-out TSPLIB gap with minimal selector regret vs oracle and significant runtime efficiency gains.  
- It maintains Pareto efficiency, strong cross-family generalization, and interpretable, instance-adaptive portfolio control without excessive runtime inflation.  
- Adaptive controllers provide interesting adaptation but at the cost of higher runtimes and worse overall TSPLIB gaps, limiting their practical advantage.  
- The static supervised ML selector is competitive but does not surpass the *full_solver_evolution* in transfer or runtime efficiency.  
- The oracle selector remains a theoretical upper bound; *phase8_full_solver_evolution* closely approximates it and can be considered the leading deployable strategy.

---

### Recommendation

Prioritize the *phase8_full_solver_evolution* approach as the best instance-adaptive hyper-heuristic control for TSP given its balance of solution quality, runtime efficiency, and cross-family transfer, without claiming novel heuristic discovery. Further refinement should focus on maintaining interpretability while controlling runtime inflation in adaptive controllers.
