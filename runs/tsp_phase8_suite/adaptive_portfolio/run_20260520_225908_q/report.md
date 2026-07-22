# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_controller_diversity_failure_replay, phase8_oracle_selector, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_225908_q
- started_at_local: 2026-05-20 22:59:08
- finished_at_local: 2026-05-20 23:30:36
- duration_hhmm: 00:31
- duration_seconds: 1888.348
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1523.848843 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.231684 | 0.159424 | 341.8462 | 0.231684 | 0.122775 | 0.162899 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1495.936971 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | True |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1534.294986 | 0.072755 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.121749 | 0.049489 | 7848.204529 | 0.627038 | 0.02542 | 0.06091 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.084733 | 0.012473 | 4105.225943 | 0.228269 | 0.106362 | 0.098393 | 0.860562 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.203607 | 0.131347 | 283.448057 | 0.203607 | 0.137301 | 0.16173 | 0.615425 | 0.62 | True |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 215.216257 | 0.213387 | 0.150269 | 0.173523 | 0.899741 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1523.848843` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.231684`, selector regret `0.159424`, runtime-adjusted gap `0.231684`.
- Family transfer `0.122775` and combined transfer `0.162899`.
- Runtime `341.8462` ms, runtime inflation `-0.775669`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1495.936971` ms, runtime inflation `-0.018317`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072755`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1534.294986` ms, runtime inflation `0.006855`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.121749`, selector regret `0.049489`, runtime-adjusted gap `0.627038`.
- Family transfer `0.02542` and combined transfer `0.06091`.
- Runtime `7848.204529` ms, runtime inflation `4.150251`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag3:cand4:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 4, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Single-shot deterministic TSP hyper-heuristic portfolio selector using instance descriptors to choose among frozen heuristics; includes bounded schedule/tuning knobs for stagnation and time-budget triggers.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "deterministic_instance_adaptive_portfolio_v1", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.228269`.
- Family transfer `0.106362` and combined transfer `0.098393`.
- Runtime `4105.225943` ms, runtime inflation `1.693985`, mean novelty `0.860562`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag4:cand-3:restart2`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": -3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic selector over frozen TSP components with bounded online schedule tuning using only interpretable structure cues plus stagnation/acceptance signals.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "det_adaptive_tsp_hh_cluster_bottleneck_grid_v5", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.203607`, selector regret `0.131347`, runtime-adjusted gap `0.203607`.
- Family transfer `0.137301` and combined transfer `0.16173`.
- Runtime `283.448057` ms, runtime inflation `-0.813992`, mean novelty `0.615425`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag4:cand-1:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic controller selecting from a frozen portfolio and using bounded, interpretable schedule/tuning nudges under stagnation and failure signals.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.09, "name": "det_tsp_hh_oracle_style_portfolio_v2", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.62, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `215.216257` ms, runtime inflation `-0.858768`, mean novelty `0.899741`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

| Condition                                    | Held-out TSPLIB Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes                                                                                              |
|----------------------------------------------|---------------------|-----------------|---------------------|-------------------|--------------|------------------|----------------------------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic**       | **0.07226**         | 0.0             | 0.07226             | 0.0               | 0.03122      | No               | Best TSPLIB gap and zero selector regret (oracle baseline ≈ this). High interpretability as a static choice of `farthest_insertion_two_opt`. No runtime inflation. Serves as a strong static baseline. |
| **phase8_oracle_selector**                    | 0.07226             | 0.0             | 0.07226             | -0.0183           | 0.02668      | Yes              | Oracle upper bound showing minimal family gap and selector regret. Not deployable. Serves as a benchmark. Runtime roughly equal to best single fixed heuristic. |
| **phase8_supervised_ml_selector**             | 0.07226             | 0.0             | 0.07275             | 0.00685           | 0.03122      | No               | Matches best single heuristic TSPLIB gap and selector regret, slight runtime inflation (~0.7%). This indicates that the supervised ML selector effectively approximates oracle/static baseline without excess cost. |
| **phase8_llm_evolved_adaptive_controller**    | 0.08473             | 0.0125          | 0.22827             | 1.69              | 0.09839      | No               | Adaptive controller shows increased TSPLIB gap and selector regret compared to best fixed heuristic; runtime inflation is substantial (1.69x). Adaptation efficiency is negative. Suggests adaptation cost exceeds performance gains in held-out tests. |
| **phase8_llm_evolved_controller_diversity_failure_replay** | 0.20361             | 0.13135         | 0.20361             | -0.814           | 0.16173      | Yes              | Pareto efficient but with significantly worse TSPLIB gap and high selector regret. Runtime reduced (runtime inflation negative), but poor adaptation and transfer performance. Suggests some successful cost saving but at gap cost. |
| **phase8_llm_static_selector**                 | 0.12175             | 0.0495          | 0.62704             | 4.15              | 0.06091      | No               | High runtime inflation (4.15x) with moderate gap increase, indicating poor runtime efficiency despite some adaptive intent. Selector regret nonzero; no improvement over baseline. |
| **phase8_random_portfolio**                     | 0.23168             | 0.15942         | 0.23168             | -0.776            | 0.16290      | Yes              | Pareto efficient but highest TSPLIB gap and regret indicate poor selection quality. Runtime low (negative inflation). Represents a low-cost baseline illustrating cost-quality tradeoffs. |
| **phase8_full_solver_evolution**                | 0.21339             | 0.14113         | 0.21339             | -0.859            | 0.17352      | Yes              | Pareto efficient with moderate runtime savings but high regret and gaps. Indicates evolution approach failed to surpass static baselines or converge to oracle performance. |

---

### Key Takeaways

- **Primary endpoint (Held-out TSPLIB gap):**  
  The **best single fixed heuristic (`farthest_insertion_two_opt`)** achieves the lowest test gap (0.07226), matching the oracle selector, confirming a strong static baseline.

- **Selector regret:**  
  Oracle and best single heuristics have zero regret as expected. Supervised ML selector matches this, showing effective interpretable instance-adaptive control without penalty. Adaptive controllers have positive regret, indicating imperfect adaptation.

- **Runtime-adjusted gap & runtime inflation:**  
  The best-fixed and oracle selectors show minimal runtime inflation (0 to slight negative), indicating no additional overhead. The supervised ML selector has negligible runtime increase (~0.7%), acceptable for deployment. Adaptive controllers induce runtime inflation up to 1.69x or more, which is substantial relative to modest or negative adaptation efficiency.

- **Pareto efficiency:**  
  Pareto fronts mostly include methods with either poor performance or substantial runtime savings but never show adaptive controllers outperforming static or oracle baselines on the primary TSPLIB metric.

- **Cross-family transfer:**  
  Transfer gaps are lowest for the oracle (0.0267) and best single heuristic (0.0312), indicating good generalization. Adaptive controllers have higher transfer gaps (~0.09-0.16), suggesting less robust generalization.

- **Interpretability and control:**  
  The supervised ML selector approximates oracle performance without runtime cost, supporting interpretable instance-adaptive control. Adaptive controllers add complexity and runtime but do not convincingly outperform this baseline, making them less attractive at this phase.

---

### Summary Conclusion

- The current phase shows **no clear benefit from adaptive hyper-heuristic control over the best single fixed heuristic** with respect to held-out TSPLIB gap and runtime-adjusted gap.

- The **oracle selector remains a useful upper bound**, but it is not deployable.

- The **supervised ML selector emerges as a promising adaptive method**, matching oracle-level gap and selector regret with minimal runtime inflation, satisfying criteria for interpretable instance-adaptive control.

- Adaptive controllers increase runtime substantially while degrading or not significantly improving performance, indicating room for further refinement before deployment.

- Pareto efficient points correspond mostly to low-cost oracles/randomized portfolios rather than effective adaptive control.

- Recommendations for next steps: Focus on improving adaptive controllers’ efficiency and robustness to approach the supervised ML selector baseline without excessive runtime inflation or regret. Avoid claiming new algorithmic discoveries; emphasize better hyper-heuristic control within known heuristics.

---

*End of analysis.*
