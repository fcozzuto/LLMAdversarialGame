# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_static_selector, phase8_oracle_selector.

## Run Metadata
- run_name: run_20260520_214625_m
- started_at_local: 2026-05-20 21:46:25
- finished_at_local: 2026-05-20 22:03:18
- duration_hhmm: 00:17
- duration_seconds: 1013.242
- seed_offset: 12000
- replicate_label: m
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 719.199271 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.201486 | 0.129226 | 1712.379657 | 0.479729 | 0.126216 | 0.153947 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 691.643686 | 0.07226 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | True |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 704.474929 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.217506 | 0.145246 | 170.428671 | 0.217506 | 0.024668 | 0.095713 | 0.0 | 0.62 | True |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.086887 | 0.014627 | 1299.970086 | 0.15705 | 0.106009 | 0.098964 | 0.0 | 0.7175 | False |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.084733 | 0.012473 | 2029.476943 | 0.239104 | 0.090132 | 0.088143 | 0.647902 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.099035 | 0.026775 | 192.633443 | 0.099035 | 0.000881 | 0.037043 | 0.75 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `719.199271` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.201486`, selector regret `0.129226`, runtime-adjusted gap `0.479729`.
- Family transfer `0.126216` and combined transfer `0.153947`.
- Runtime `1712.379657` ms, runtime inflation `1.380953`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `691.643686` ms, runtime inflation `-0.038314`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `704.474929` ms, runtime inflation `-0.020473`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.217506`, selector regret `0.145246`, runtime-adjusted gap `0.217506`.
- Family transfer `0.024668` and combined transfer `0.095713`.
- Runtime `170.428671` ms, runtime inflation `-0.76303`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:farthest_insertion_two_opt:nearest_neighbor_multistart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selector over frozen TSP heuristic portfolio using structure descriptors (cluster, grid, bottleneck, corridor, NN-trap) and fixed bounded tuning/scheduling knobs.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.05, "name": "det_tsp_portfolio_oracleish_v1", "nearest_neighbor_trap_heuristic": "edge_preserving_restart", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.65, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.086887`, selector regret `0.014627`, runtime-adjusted gap `0.15705`.
- Family transfer `0.106009` and combined transfer `0.098964`.
- Runtime `1299.970086` ms, runtime inflation `0.807524`, mean novelty `0.0`, and complexity `0.7175`.
- Pareto efficient: `False`.
- Controller signature: `annealed_multi_start:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand-2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller selecting from a frozen TSP heuristic portfolio. Uses interpretable structure cues (clusteredness, grid-likeness, bottleneck/two-cluster, corridor/elongation, and nearest-neighbor trap) plus online stagnation signals ", "failed_perturbation_threshold": 2, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.09, "name": "deterministic_instance_adaptive_tsp_hh_v1", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "annealed_multi_start", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.5, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.084733`, selector regret `0.012473`, runtime-adjusted gap `0.239104`.
- Family transfer `0.090132` and combined transfer `0.088143`.
- Runtime `2029.476943` ms, runtime inflation `1.821856`, mean novelty `0.647902`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag4:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.007, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic over a frozen portfolio; structure-driven core selection with conservative stagnation switching to reduce thrashing under hard/difficult replay modes.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "interpretable_instance_adaptive_tsp_hh_v2", "nearest_neighbor_trap_heuristic": "farthest_insertion_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.3, "time_budget_trigger": 0.65, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.099035`, selector regret `0.026775`, runtime-adjusted gap `0.099035`.
- Family transfer `0.000881` and combined transfer `0.037043`.
- Runtime `192.633443` ms, runtime inflation `-0.732156`, mean novelty `0.75`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

#### 1. **Primary Endpoint: Held-Out TSPLIB Gap**
- **Best fixed heuristic ("farthest_insertion_two_opt")** achieves a TSPLIB gap of **0.07226**, serving as the baseline for practical deployment.
- **Oracle selector** matches this gap (0.07226) but is a theoretical upper bound, not deployable.
- **Supervised ML selector** also achieves this same gap (0.07226) with slightly lower runtime than oracle.
- The **adaptive controllers** improve gap moderately but at the expense of increased runtime: 
  - "phase8_llm_evolved_adaptive_controller" gap = 0.0869 (worse than fixed heuristic) with much higher runtime (~1300 ms vs ~720 ms).
  - "phase8_llm_evolved_controller_diversity_failure_replay" gap = 0.0847 but with very high runtime inflation and runtime (~2029 ms).
- The **full solver evolution** achieves a somewhat worse TSPLIB gap (0.099) but with significantly lower runtime (~193 ms), demonstrating a runtime-quality tradeoff.

#### 2. **Selector Regret vs Oracle Portfolio**
- The **best fixed heuristic** and **supervised selector** have zero regret, indicating no underperformance relative to oracle on TSPLIB instances.
- Adaptive controllers have small selection regrets (around 0.01–0.03), but these do not translate to improved TSPLIB gaps.
  - Small regret but increased runtime suggests they do not consistently improve solution quality vs cost.

#### 3. **Runtime-Adjusted Gap**
- Despite the best TSPLIB gap, adaptive controllers have **worse runtime-adjusted gaps** compared to fixed or oracle selectors.
- The **static LLM-based selector** and **full solver evolution** are Pareto efficient, balancing quality and runtime better:
  - Static selector has a higher gap (0.217) but *very low runtime* (170 ms), good for fast approximate solutions.
  - Full solver evolution has lower gap (0.099) with runtime ~193 ms.
- Oracle and fixed heuristic have moderate runtime (~700 ms) but best or near-best gaps, representing a balanced point.

#### 4. **Pareto Efficiency**
- **Pareto-efficient settings** are:
  - **Oracle selector** (best gap, moderate runtime),
  - **LLM static selector** (fast runtime but higher gap),
  - **Full solver evolution** (moderate gap and low runtime).
- Adaptive controllers are **not Pareto-efficient** due to runtime inflation without gap improvements beyond fixed baseline.

#### 5. **Cross-Family Transfer**
- Transfer gaps (performance on cross-family instances) are lowest for oracle and fixed heuristic (~0.026–0.031), showing stable transfer.
- Adaptive controllers show higher transfer gaps (~0.09–0.10), indicating potential overfitting or limited cross-family generalization.
- Static selector has intermediate transfer gap (~0.096), consistent with runtime and gap tradeoffs.

---

### Summary of Findings

- **The best fixed heuristic ("farthest_insertion_two_opt") remains a strong baseline**, achieving the lowest held-out TSPLIB gap with moderate runtime.
- The **oracle selector confirms the theoretical upper bound** and is not deployable.
- **Supervised ML selector matches the fixed heuristic performance without runtime increase**, showing promise for interpretable instance-adaptive control.
- **Adaptive controllers, while interpretable and using instance structure plus stagnation signals, do not improve TSPLIB gap relative to fixed heuristic and incur high runtime inflation and transfer gap penalties**, limiting their practical utility at this stage.
- **Pareto analysis favors either the fixed/oracle-like selectors or low-runtime static selectors**, depending on runtime vs quality tradeoff preferences.
- The **full solver evolution approach offers a competitive balance between runtime and solution quality**, suggesting value in solver-level evolution over adaptive heuristic switching alone.

---

### Recommendations

- Prioritize **deploying the fixed heuristic or supervised ML selector** for instance-adaptive hyper-heuristic control, as these approach oracle quality without runtime inflation.
- Investigate reducing runtime overhead and improving cross-family transfer in adaptive controllers before claiming benefits of interpretable instance-adaptive control.
- Avoid claims of novel algorithm discovery; current focus should remain on hyper-heuristic control over known heuristics with interpretable instance features.
- Consider further experiments with the full solver evolution approach given its Pareto efficiency and relatively low runtime.

---

This conservative interpretation respects the primary focus on held-out TSPLIB gap, runtime efficiency, selector regret, and transfer generalization without overclaiming advances beyond hyper-heuristic portfolio control.
