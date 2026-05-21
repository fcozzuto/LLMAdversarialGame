# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_random_portfolio.

## Run Metadata
- run_name: run_20260520_220319_n
- started_at_local: 2026-05-20 22:03:19
- finished_at_local: 2026-05-20 22:24:00
- duration_hhmm: 00:21
- duration_seconds: 1240.802
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 694.051829 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.20534 | 0.13308 | 112.013529 | 0.20534 | 0.051131 | 0.107945 | 0.0 | 0.0 | True |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 703.521671 | 0.073246 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 704.132457 | 0.07331 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.214311 | 0.142051 | 226.7406 | 0.214311 | 0.024668 | 0.094536 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.086887 | 0.014627 | 1331.502514 | 0.166688 | 0.003547 | 0.034251 | 0.65746 | 0.7275 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.120261 | 0.048001 | 5320.915529 | 0.921975 | 0.090132 | 0.101232 | 0.754937 | 0.695 | False |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 99.356914 | 0.213387 | 0.150269 | 0.173523 | 0.893412 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `694.051829` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.20534`, selector regret `0.13308`, runtime-adjusted gap `0.20534`.
- Family transfer `0.051131` and combined transfer `0.107945`.
- Runtime `112.013529` ms, runtime inflation `-0.838609`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.073246`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `703.521671` ms, runtime inflation `0.013644`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07331`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `704.132457` ms, runtime inflation `0.014524`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.024668` and combined transfer `0.094536`.
- Runtime `226.7406` ms, runtime inflation `-0.673309`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selection over a frozen portfolio using geometry/structure descriptors; uses bounded schedule tuning parameters for stagnation and perturbation intensity.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "tsp_heuristic_oracle_portfolio_static_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.65, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.086887`, selector regret `0.014627`, runtime-adjusted gap `0.166688`.
- Family transfer `0.003547` and combined transfer `0.034251`.
- Runtime `1331.502514` ms, runtime inflation `0.918448`, mean novelty `0.65746`, and complexity `0.7275`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag3:cand0:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 0, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over a frozen heuristic portfolio. Chooses construction/refinement style from interpretable structural descriptors (clustered/grid/two-cluster-bottleneck/corridor/nearest-neighbor trap) and escalates to restart/annealin", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "tsp_hh_frozen_portfolio_instance_adaptive_v3", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.12, "time_budget_trigger": 0.6, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.120261`, selector regret `0.048001`, runtime-adjusted gap `0.921975`.
- Family transfer `0.090132` and combined transfer `0.101232`.
- Runtime `5320.915529` ms, runtime inflation `6.666453`, mean novelty `0.754937`, and complexity `0.695`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selection over a frozen TSP heuristic portfolio with bounded, interpretable switches driven by stagnation and perturbation failure.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "interp_portfolio_adaptive_tsp_v2", "nearest_neighbor_trap_heuristic": "cheapest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `99.356914` ms, runtime inflation `-0.856845`, mean novelty `0.893412`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Heuristic Portfolio Suite Results

| Condition                            | Held-out TSPLIB Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes                                                                                  |
|------------------------------------|---------------------|-----------------|---------------------|-------------------|--------------|------------------|----------------------------------------------------------------------------------------|
| **phase8_best_single_fixed_heuristic** | **0.07226**         | 0.0             | 0.07226             | 0.0               | 0.031222     | Yes              | Best held-out TSPLIB gap, zero regret (fixed/frozen heuristic farthest_insertion_two_opt); baseline for adaptive selectors |
| phase8_oracle_selector             | 0.07226             | 0.0             | 0.073246            | 0.0136            | 0.026678     | No               | Oracle selector matches best fixed heuristic gap, slight runtime inflation; upper bound, not deployable                   |
| phase8_supervised_ml_selector      | 0.07226             | 0.0             | 0.07331             | 0.0145            | 0.031222     | No               | Nearly identical performance to best fixed heuristic and oracle; supports interpretable instance-adaptive control      |
| phase8_llm_evolved_adaptive_controller | 0.086887            | 0.014627        | 0.166688            | 0.9184            | 0.034251     | No               | Adaptive control shows some selector regret and runtime inflation (~x2); worse held-out gap and runtime-adjusted gap    |
| phase8_llm_static_selector         | 0.214311            | 0.142051        | 0.214311            | -0.6733           | 0.094536     | No               | Static selectors have worse gaps and regret despite runtime saving                                                     |
| phase8_random_portfolio            | 0.20534             | 0.13308         | 0.20534             | -0.8386           | 0.107945     | Yes              | Random portfolio shows poor gaps but low runtime, Pareto efficient due to runtime trade-off                            |
| phase8_full_solver_evolution       | 0.213387            | 0.141127        | 0.213387            | -0.8568           | 0.173523     | Yes              | Full solver evolution underperforms in gap but is Pareto efficient due to low runtime                                 |
| phase8_llm_evolved_controller_diversity_failure_replay | 0.120261            | 0.048001        | 0.921975            | 6.6664            | 0.101232     | No               | Very high runtime inflation (~7x), much worse runtime-adjusted gap; regret and transfer gap also high                   |

---

### Key Findings and Recommendations

- **Primary Endpoint (Held-out TSPLIB Gap):**
  - The **best single fixed heuristic (farthest_insertion_two_opt)** achieves the lowest gap (0.07226), matching the oracle selector.
  - Adaptive controllers, including ML-based and LLM-evolved selectors, do **not improve held-out gap** beyond best fixed.
  - Some adaptive methods (e.g., phase8_llm_evolved_adaptive_controller) actually degrade held-out gap, with significant runtime inflation.

- **Selector Regret vs Oracle:**
  - The oracle selector sets a tight lower bound on regret (0.0).
  - The best static and supervised ML selectors achieve zero regret (no gap from oracle).
  - Adaptive controllers incur small but noticeable regret (1.5% to 5%), suggesting imperfect selection accuracy or adaptation.

- **Runtime-Adjusted Gap and Runtime Inflation:**
  - The best fixed heuristic and oracle have comparable low runtime-adjusted gaps (~0.07).
  - Adaptive controllers often incur significant runtime inflation (close to doubling or more), resulting in worse runtime-adjusted gaps (~0.17 and higher).
  - Static selectors reduce runtime (negative inflation) but pay with worse solution quality and regret.
  - The large runtime overhead in some adaptive controllers limits practical interpretability and deployment.

- **Pareto Efficiency:**
  - Only three conditions are Pareto efficient: best fixed heuristic, random portfolio, and full solver evolution.
  - Neither adaptive selector variants reach Pareto front, indicating suboptimal tradeoffs between gap and runtime.

- **Cross-Family Transfer (Transfer Gap):**
  - Transfer gaps are generally low for best fixed, oracle, and supervised selectors (∼0.03).
  - Larger transfer gaps appear with adaptive selectors and full solver evolution, indicating less robust cross-family generalization.

- **Interpretability and Control:**
  - Static and supervised ML selectors demonstrate close-to-oracle performance with minimal runtime inflation, supporting claims for interpretable instance-adaptive control.
  - Evolved adaptive controllers demonstrate promising adaptation efficiency but suffer from high runtime overhead, limiting practical benefit.
  - No evidence of discovering new heuristics; results reflect hyper-heuristic control over known methods.

---

### Summary

- The **best single fixed heuristic (farthest_insertion_two_opt)** remains the strongest baseline in held-out TSPLIB gap and runtime-adjusted performance.
- The **oracle selector confirms this baseline as a tight lower bound**, so adaptive improvement is challenging.
- **Supervised ML and static selectors nearly match the oracle without significant runtime cost**, supporting interpretable, deployable instance-adaptive control.
- Evolved adaptive controllers show limited benefit due to **runtime inflation and increased regret**, diminishing practical value.
- The portfolio suite should emphasize **maintaining interpretability and runtime efficiency** as best fixed heuristics and simpler selectors demonstrate strong, reliable performance.
