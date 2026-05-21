# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_controller_diversity_failure_replay.

## Run Metadata
- run_name: run_20260520_222400_o
- started_at_local: 2026-05-20 22:24:00
- finished_at_local: 2026-05-20 22:42:52
- duration_hhmm: 00:19
- duration_seconds: 1131.434
- seed_offset: 14000
- replicate_label: o
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 702.170743 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.19294 | 0.12068 | 1752.028029 | 0.481416 | 0.074127 | 0.1179 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 704.727914 | 0.072523 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 716.268414 | 0.073711 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.120261 | 0.048001 | 3584.457971 | 0.613911 | 0.001857 | 0.045479 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.120261 | 0.048001 | 5351.889486 | 0.91662 | 0.090132 | 0.101232 | 0.076586 | 0.62 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.201598 | 0.129338 | 137.508014 | 0.201598 | 0.045212 | 0.102828 | 0.0 | 0.62 | True |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 101.469429 | 0.213387 | 0.150269 | 0.173523 | 0.849625 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `702.170743` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.19294`, selector regret `0.12068`, runtime-adjusted gap `0.481416`.
- Family transfer `0.074127` and combined transfer `0.1179`.
- Runtime `1752.028029` ms, runtime inflation `1.49516`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072523`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `704.727914` ms, runtime inflation `0.003642`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.073711`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `716.268414` ms, runtime inflation `0.020077`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.613911`.
- Family transfer `0.001857` and combined transfer `0.045479`.
- Runtime `3584.457971` ms, runtime inflation `4.104824`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cheapest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand-2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -2, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over frozen TSP heuristic portfolio; chooses structure-appropriate construction/refinement with conservative online tuning knobs.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "deterministic_instance_adaptive_oracleish_baseline", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.91662`.
- Family transfer `0.090132` and combined transfer `0.101232`.
- Runtime `5351.889486` ms, runtime inflation `6.62192`, mean novelty `0.076586`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.007, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector/scheduler over frozen TSP heuristics with structure-triggered switching and bounded parameter offsets.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "interp_adaptive_tsp_hh_v2", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.12, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.201598`, selector regret `0.129338`, runtime-adjusted gap `0.201598`.
- Family transfer `0.045212` and combined transfer `0.102828`.
- Runtime `137.508014` ms, runtime inflation `-0.804167`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller selecting from frozen TSP heuristic portfolio using structure descriptors and online stagnation signals to schedule bounded escape/exploit behavior.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "interpretable_instance_adaptive_hh_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `101.469429` ms, runtime inflation `-0.855492`, mean novelty `0.849625`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

| Condition                                  | Held-out TSPLIB gap | Selector regret vs oracle | Runtime-adjusted gap | Runtime inflation | Transfer gap | Pareto efficient | Comments                                                                                     |
|--------------------------------------------|---------------------|---------------------------|---------------------|-------------------|--------------|------------------|----------------------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic**     | **0.07226**         | 0.0                       | 0.07226             | 0.0               | 0.031222     | Yes              | Best baseline on held-out TSPLIB. Simple fixed heuristic (farthest_insertion_two_opt) with zero added runtime or regret. Strong static baseline. |
| **phase8_oracle_selector**                  | 0.07226             | 0.0                       | 0.07252             | 0.0036            | 0.026678     | No               | Oracle selector is an upper bound, matches best_fixed in TSPLIB gap, negligible runtime inflation. Not deployable but useful reference.         |
| **phase8_supervised_ml_selector**           | 0.07226             | 0.0                       | 0.07371             | 0.0201            | 0.031222     | No               | Matches best TSPLIB gap, minor selector regret and slight runtime inflation.                |
| **phase8_llm_static_selector**               | 0.12026             | 0.048                     | 0.61391             | 4.10              | 0.04548      | No               | Worse held-out gap and large runtime inflation (~4x). Higher regret. Despite instance-adaptive mechanism, runtime cost is high and gap is larger. |
| **phase8_llm_evolved_adaptive_controller**   | 0.12026             | 0.048                     | 0.91662             | 6.62              | 0.101232     | No               | Adaptive controller has highest runtime inflation and worst runtime adjusted gap. Selector regret moderate; held-out gaps not improved over fixed baseline.      |
| **phase8_llm_evolved_controller_diversity_failure_replay** | 0.20160      | 0.1293                    | 0.20160             | -0.80             | 0.102828     | Yes              | Lower runtime (~-0.8 runtime inflation) but much worse held-out gap and high selector regret vs oracle. Still pareto because of low runtime.                |
| **phase8_random_portfolio**                   | 0.19294             | 0.121                     | 0.48142             | 1.50              | 0.11790      | No               | Poor held-out gap and high regret relative to oracle. Significant runtime inflation; not pareto.         |
| **phase8_full_solver_evolution**              | 0.21339             | 0.141                     | 0.21339             | -0.86             | 0.17352      | Yes              | Worse held-out gap and regret; lowest runtime (negative runtime inflation). Pareto due to runtime saving but less effective on TSPLIB gaps.|

---

### Summary & Prioritized Conclusions

- **Primary endpoint (held-out TSPLIB gap):**  
  The **best performer** is the *phase8_best_single_fixed_heuristic* with gap 0.07226, matching the oracle selector's gap. This shows that the simple fixed heuristic `farthest_insertion_two_opt` is difficult to beat on this metric.

- **Selector regret vs oracle:**  
  The oracle selector sets a zero regret baseline. The *supervised ML selector* matches the oracle's held-out gap without selector regret and only minor runtime inflation, suggesting effective instance-adaptive control.

- **Runtime-adjusted gap & inflation:**  
  The fixed heuristic and oracle selector show the best tradeoff, with low runtime and gaps. Adaptive controllers and static LLM-based selectors inflate runtime substantially (up to ~6.6x), harming their practical deployability.

- **Pareto efficiency:**  
  Pareto-optimal conditions include the fixed heuristic, a low-runtime evolved controller with diversity failure replay, and a full solver evolution with low runtime cost. However, none improve upon or match the fixed heuristic's held-out gap with reasonable runtime.

- **Cross-family transfer:**  
  Transfer gaps are lowest for the fixed heuristic and oracle selector (~0.03), increasing for adaptive controllers (~0.10+), indicating less generalizable control learned by evolution or LLM approaches.

- **Interpretability & adaptive control claims:**  
  While adaptive controllers show some interpretable structure-triggered switching, their runtime inflation and worse performance vs fixed suggest limited practical benefit at this phase. The supervised ML selector approximates oracle performance without excessive runtime increase, offering a more interpretable and deployable instance-adaptive control baseline, rather than discovering new heuristics.

---

### Recommendations

- Emphasize the strong baseline of the fixed heuristic and supervised ML selector in matching oracle-level gaps with manageable runtime, highlighting stable and interpretable instance-adaptive control.

- Be cautious claiming benefits of LLM static or evolved adaptive controllers: they incur excessive runtime inflation and do not improve held-out gaps or regret substantially.

- Use oracle selector as a performance upper bound only, not a deployable baseline.

- Future work should focus on reducing runtime inflation in adaptive controllers while maintaining or improving held-out gap and selector regret.

---

**In brief:**

> The fixed heuristic *farthest_insertion_two_opt* remains the best held-out TSPLIB solution baseline, closely matched by the supervised ML selector with negligible selector regret and small runtime inflation. Oracle selector establishes a gap lower bound but is impractical. Adaptive controllers and LLM-driven selectors introduce excessive runtime inflation without gap improvement, limiting their practical instance-adaptive utility in this phase.
