# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_llm_evolved_controller_diversity_failure_replay, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_205447_j
- started_at_local: 2026-05-20 20:54:47
- finished_at_local: 2026-05-20 21:09:36
- duration_hhmm: 00:15
- duration_seconds: 889.343
- seed_offset: 9000
- replicate_label: j
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 709.339814 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.193358 | 0.121098 | 1711.242357 | 0.466465 | 0.079247 | 0.121288 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 701.456071 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 701.062771 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.215559 | 0.143299 | 186.338143 | 0.215559 | 0.048232 | 0.109879 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.203245 | 0.130985 | 140.077614 | 0.203245 | 0.11437 | 0.147113 | 0.065431 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.203607 | 0.131347 | 90.862943 | 0.203607 | 0.116207 | 0.148407 | 0.451106 | 0.62 | True |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 99.501771 | 0.213387 | 0.150269 | 0.173523 | 0.86078 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `709.339814` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.193358`, selector regret `0.121098`, runtime-adjusted gap `0.466465`.
- Family transfer `0.079247` and combined transfer `0.121288`.
- Runtime `1711.242357` ms, runtime inflation `1.412444`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `701.456071` ms, runtime inflation `-0.011114`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `701.062771` ms, runtime inflation `-0.011669`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.215559`, selector regret `0.143299`, runtime-adjusted gap `0.215559`.
- Family transfer `0.048232` and combined transfer `0.109879`.
- Runtime `186.338143` ms, runtime inflation `-0.737308`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `edge_preserving_restart:cluster_first_local_search:edge_preserving_restart:nearest_neighbor_multistart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over a frozen heuristic portfolio using interpretable structure cues (two-cluster/bottleneck, grid-likeness, clustering, corridor, and nearest-neighbor trap). Includes bounded tuning knobs for restart/candidate limits a", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "tsp_one_shot_interpretable_portfolio_epoch1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "edge_preserving_restart", "restart_offset": 1, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.203245`, selector regret `0.130985`, runtime-adjusted gap `0.203245`.
- Family transfer `0.11437` and combined transfer `0.147113`.
- Runtime `140.077614` ms, runtime inflation `-0.802524`, mean novelty `0.065431`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag4:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.007, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive scheduler over frozen TSP heuristic portfolio using structure descriptors plus online stagnation/perturbation feedback.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "det_adaptive_tsp_portfolio_epoch7", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.203607`, selector regret `0.131347`, runtime-adjusted gap `0.203607`.
- Family transfer `0.116207` and combined transfer `0.148407`.
- Runtime `90.862943` ms, runtime inflation `-0.871905`, mean novelty `0.451106`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cheapest_insertion_two_opt:edge_preserving_restart:nearest_neighbor_multistart:stag4:cand-1:restart0`.
- Controller rule summary: {"acceptance_bias": 0.01, "candidate_limit_offset": -1, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive TSP hyper-heuristic selector/scheduler over a frozen portfolio, using interpretable structure scores plus online stagnation to switch/sanitize search; tuned for stronger transfer while limiting disruptive restarts.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "interpretable_structure_adaptive_portfolio_v4", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 0, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 4, "temperature_scale": 1.15, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `99.501771` ms, runtime inflation `-0.859726`, mean novelty `0.86078`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Summary of TSP Adaptive Heuristic Portfolio Suite Evaluation

| Condition                                  | Held-out TSPLIB Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes                                                                                                                   |
|--------------------------------------------|---------------------|-----------------|---------------------|-------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic**    | 0.07226             | 0.0             | 0.07226             | 0.0               | 0.03122      | No               | Best fixed heuristic ("farthest_insertion_two_opt"), strong baseline, no runtime inflation.                              |
| **phase8_oracle_selector**                  | 0.07226             | 0.0             | 0.07226             | -0.0111           | 0.02668      | No               | Oracle selector as upper bound; matches best fixed in TSPLIB gap and runtime; not deployable in practice.               |
| **phase8_supervised_ml_selector**           | 0.07226             | 0.0             | 0.07226             | -0.0117           | 0.03122      | Yes              | Approaches oracle performance without runtime cost inflation; interpretable control; pareto efficient.                  |
| **phase8_llm_evolved_adaptive_controller** | 0.20325             | 0.1310          | 0.20325             | -0.8025           | 0.14711      | Yes              | Adaptive controller with fast runtime, negative runtime inflation (speedup), but significantly worse held-out gap.      |
| **phase8_llm_evolved_controller_diversity_failure_replay** | 0.20361             | 0.1313          | 0.20361             | -0.8719           | 0.14840      | Yes              | Similar adaptive approach, slightly less runtime, similar gap and regret, pareto efficient.                            |
| **phase8_full_solver_evolution**            | 0.21339             | 0.1411          | 0.21339             | -0.8597           | 0.17352      | Yes              | Full solver evolution with larger code novelty; worse gap; fast but less effective adaptation control.                  |
| **phase8_llm_static_selector**               | 0.21556             | 0.1433          | 0.21556             | -0.7373           | 0.10987      | No               | One-shot interpretable static selector, fastest runtime, but poorer gap and regret; not pareto efficient.               |
| **phase8_random_portfolio**                   | 0.19336             | 0.1211          | 0.46646             | 1.4124            | 0.12129      | No               | Random portfolio baseline; much worse runtime and gap; high runtime inflation and regret.                                |

---

### Conservative Interpretation

- **Primary endpoint (held-out TSPLIB gap)**:  
  The **best single fixed heuristic**, the **oracle selector**, and the **supervised ML selector** all achieve identical held-out TSPLIB gaps (~0.072). This suggests that adaptive selection methods here did not surpass or improve on the single best known heuristic in solution quality.

- **Selector regret vs. oracle**:  
  The supervised ML selector shows zero regret relative to the oracle, indicating its instance-adaptive decision closely emulates the oracle portfolio. Adaptive controllers have significant positive regret (~0.13), indicating suboptimal instance adaptation.

- **Runtime-adjusted gap and runtime inflation**:  
  Adaptive controllers and static selectors consistently improve runtime (negative runtime inflation), often achieving 2-5x speedup versus fixed heuristics. However, this speedup comes at the cost of a doubled or tripled gap. The supervised ML selector matches the fixed heuristic runtime closely, with no runtime inflation.

- **Pareto efficiency**:  
  The supervised ML selector and adaptive controllers (LLM evolved variants) are on the Pareto front, with the ML selector the only one achieving both zero regret and no runtime penalty among them.

- **Cross-family transfer**:  
  Transfer gaps correlate with TSPLIB performance; the oracle has the best transfer (lowest gap 0.0267), supervised ML selector slightly higher (0.0312). Adaptive controllers show elevated transfer gaps (~0.14-0.17), indicating less robust cross-family generalization.

- **Interpretability and instance-adaptive control**:  
  The supervised ML selector demonstrates interpretable, instance-adaptive control matching oracle performance without runtime cost, suggesting effective hyper-heuristic control over known heuristics. Adaptive controllers with evolved policies trade solution quality for runtime but might be viable when speed is critical, though their adaptation efficiency is low.

- **No new algorithm discovery**:  
  All methods control known heuristics; improvements are in hyper-heuristic adaptation rather than new heuristics.

---

### Key Takeaways

- The **supervised ML selector** best balances interpretability, adaption efficiency, and performance, effectively emulating the oracle with no runtime inflation. It represents a convincing instance-adaptive hyper-heuristic portfolio controller at this phase.

- The **best single fixed heuristic** remains a strong baseline with moderate runtime and solution quality.

- The **oracle selector** provides a valuable theoretical upper bound but is not deployable.

- Adaptive controllers provide significant runtime speedups but with substantial penalty in solution quality and selector regret, indicating room for improvement in adaptive control strategies.

- Random and static heuristic portfolio methods underperform relative to targeted ML or adaptive strategies.

---

### Recommendation

Focus further development on **interpretable supervised ML selectors** that closely track the oracle performance without runtime cost. Investigate adaptive controllers for runtime-critical scenarios but seek strategies to reduce selector regret and improve held-out gap. Avoid random portfolios and static selectors that lack Pareto efficiency or meaningful gains.
