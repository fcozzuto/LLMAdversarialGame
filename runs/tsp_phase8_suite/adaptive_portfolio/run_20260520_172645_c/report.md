# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller, phase8_llm_evolved_controller_diversity_failure_replay, phase8_supervised_ml_selector.

## Run Metadata
- run_name: run_20260520_172645_c
- started_at_local: 2026-05-20 17:26:45
- finished_at_local: 2026-05-20 17:55:40
- duration_hhmm: 00:29
- duration_seconds: 1735.193
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1491.554171 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_random_portfolio | random_portfolio | none | 0.190005 | 0.117745 | 1482.355357 | 0.190005 | 0.082535 | 0.122129 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1535.363729 | 0.074382 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1465.688143 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_llm_static_selector | static_selector | none | 0.214311 | 0.142051 | 488.999614 | 0.214311 | 0.024801 | 0.094621 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.203245 | 0.130985 | 344.320514 | 0.203245 | 0.027485 | 0.092239 | 0.044633 | 1.7025 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.204775 | 0.132515 | 267.676329 | 0.204775 | 0.059962 | 0.113314 | 0.0 | 0.62 | True |
| phase8_full_solver_evolution | full_solver | none | 0.213387 | 0.141127 | 206.0418 | 0.213387 | 0.150269 | 0.173523 | 0.814332 | 0.56 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1491.554171` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.190005`, selector regret `0.117745`, runtime-adjusted gap `0.190005`.
- Family transfer `0.082535` and combined transfer `0.122129`.
- Runtime `1482.355357` ms, runtime inflation `-0.006167`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.074382`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1535.363729` ms, runtime inflation `0.029372`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1465.688143` ms, runtime inflation `-0.017342`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.024801` and combined transfer `0.094621`.
- Runtime `488.999614` ms, runtime inflation `-0.672154`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:farthest_insertion_two_opt:farthest_insertion_two_opt:edge_preserving_restart:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 3, "clustered_heuristic": "farthest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Static instance-conditioned portfolio selector using interpretable structure cues; schedules small bounded perturbation parameters via fixed offsets and thresholds.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "farthest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "deterministic_instance_adaptive_frozen_portfolio_v1", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.203245`, selector regret `0.130985`, runtime-adjusted gap `0.203245`.
- Family transfer `0.027485` and combined transfer `0.092239`.
- Runtime `344.320514` ms, runtime inflation `-0.769153`, mean novelty `0.044633`, and complexity `1.7025`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:farthest_insertion_two_opt:annealed_multi_start:stag4:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": -1, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic controller selecting from a frozen portfolio using interpretable structural descriptors and online stagnation/counters to schedule bounded adjustments (candidate list limit, restarts, and annealing temperature/ac", "determinism": {"no_random_choice": true, "rule_evaluation_order": "first_match_wins", "seed_free": true}, "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.08, "name": "tsp_frozen_portfolio_instance_adaptive_v2", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "policy": {"fallback": {"tuning": {"candidate_limit_offset": 0, "restart_offset": 0}, "use": "default_heuristic"}, "online_stagnation_rules": [{"tuning": {"acceptance_bias": "acceptance_bias", "candidate_limit_offset": "candidate_limit_offset", "restart_offset": "restart_offset", "temperature_scale": "temperature_scale"}, "use": "stagnation_switch_heuristic", "when": "stagnation_length >= stagnation_threshold and recent_improvement_rate <= low_improvement_threshold"}, {"tuning": {"restart_offset": "restart_offset"}, "use": "random_like_heuristic", "when": "failed_perturbation_count >= failed_perturbation_threshold and time_budget_used < time_budget_trigger"}, {"tuning": {"candidate_limit_offset": "candidate_limit_offset"}, "use": "default_heuristic", "when": "stagnation_length >= stagnation_threshold and time_budget_used >= time_budget_trigger"}], "static_structure_rules": [{"use": "grid_like_heuristic", "when": "grid_likeness >= 0.45 and dimension >= 80"}, {"use": "two_cluster_bottleneck_heuristic", "when": "bottleneck_score >= 0.52 or two_cluster_bottleneck_score >= 0.52"}, {"use": "clustered_heuristic", "when": "clustering_score >= 0.46 and cluster_separation >= 0.46"}, {"use": "corridor_heuristic", "when": "corridor_score >= 0.47"}, {"use": "nearest_neighbor_trap_heuristic", "when": "nearest_neighbor_trap_score >= 0.52 and nn_distance_cv >= 0.55"}]}, "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.204775`, selector regret `0.132515`, runtime-adjusted gap `0.204775`.
- Family transfer `0.059962` and combined transfer `0.113314`.
- Runtime `267.676329` ms, runtime inflation `-0.820539`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:limited_three_opt:stag3:cand3:restart1`.
- Controller rule summary: {"acceptance_bias": 0.0, "candidate_limit_offset": 3, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "candidate_pruned_two_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive selection among a frozen TSP portfolio; bottleneck and clustered layouts trigger specialized restart or clustering; stagnation triggers a limited 3-opt escalation; budget trigger shifts toward faster candidate-pruned local searc", "failed_perturbation_threshold": 2, "grid_like_heuristic": "cheapest_insertion_two_opt", "low_improvement_threshold": 0.08, "name": "interpretable_instance_adaptive_heuristic_switchboard_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "limited_three_opt", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.65, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.213387`, selector regret `0.141127`, runtime-adjusted gap `0.213387`.
- Family transfer `0.150269` and combined transfer `0.173523`.
- Runtime `206.0418` ms, runtime inflation `-0.861861`, mean novelty `0.814332`, and complexity `0.56`.
- Pareto efficient: `True`.

## Judge Appendix
```markdown
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Results

#### Primary Endpoint: Held-out TSPLIB Gap
- The best held-out TSPLIB gaps are reached by:
  - **phase8_best_single_fixed_heuristic** and **phase8_supervised_ml_selector**, both achieving a gap of **0.07226**.
  - The **oracle selector** matches this gap (0.07226) and serves as an upper bound.
- Other adaptive controllers (phase8_llm_evolved_adaptive_controller, phase8_llm_evolved_controller_diversity_failure_replay) have higher TSPLIB gaps (~0.20), indicating less optimal held-out performance despite adaptation.
- The random portfolio and static selector perform worse (TSPLIB gaps 0.19 and 0.21 respectively).

#### Selector Regret vs Oracle Portfolio
- The oracle selector by definition has **0 regret**.
- The **best_fixed_heuristic** and **supervised_ml_selector** also report zero selector regret, implying no performance loss relative to oracle on selector choice.
- Adaptive controllers have selector regrets around 0.13, indicating moderate inefficiency relative to oracle selection, despite adaptation.
- The random portfolio and static selector show highest regret (>0.13 and 0.14 respectively).

#### Runtime-Adjusted Gap & Runtime Inflation
- Runtime-adjusted gap balances solution quality and runtime:
  - Best single fixed heuristic and supervised ML selector have ~0.072 runtime-adjusted gap with near-zero or slightly negative runtime inflation (no runtime increase).
  - Oracle selector has slightly higher runtime-adjusted gap (0.074) with 3% runtime inflation.
  - Adaptive controllers have higher runtime-adjusted gaps (~0.20) but **much lower runtime inflation** (around -0.7 to -0.8), indicating faster runtimes but at quality cost.
  - Static selector also faster (-0.67 inflation) but worse quality.
- This tradeoff suggests adaptive controllers yield faster but lower-quality solutions.

#### Pareto Efficiency
- Pareto-efficient conditions include:
  - **phase8_supervised_ml_selector** (good TSPLIB gap, low regret, no runtime inflation)
  - **phase8_llm_evolved_adaptive_controller**, **phase8_llm_evolved_controller_diversity_failure_replay**, and **phase8_full_solver_evolution**
- Despite higher gaps, adaptive controllers are Pareto efficient due to better runtime efficiency or complexity.
- Best fixed heuristic and oracle selector are *not* Pareto efficient under multi-objective consideration.

#### Cross-Family Transfer
- Transfer gaps (performance gap when tested on different or held-out instance families):
  - Best fixed heuristic & supervised ML selector: ~0.0312 (low transfer gap)
  - Oracle selector: ~0.027 (lowest)
  - Adaptive controllers: ~0.09-0.11 (higher but still moderate)
  - Random portfolio and static selector: higher (0.10-0.12+)
- Indicates moderate generalization ability of adaptive selectors but best fixed and supervised ML selectors transfer better.

#### Interpretability and Instance-Adaptive Control
- Supervised ML selector is interpretable and instance-adaptive, achieves oracle-level TSPLIB gap without runtime inflation, supporting interpretable instance-adaptive control claims.
- Adaptive controllers apply interpretable, deterministic rules with bounded adjustments; however, their TSPLIB gap and selector regret are worse, albeit with runtime benefits.
- Static selector is interpretable but suffers from higher TSPLIB gap and regret.
- No evidence of discovering new heuristics; all control hyper-heuristic over known heuristics as intended.

---

### Summary

| Condition                              | TSPLIB Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Transfer Gap | Pareto Efficient | Notes                                      |
|--------------------------------------|------------|-----------------|---------------------|-------------------|--------------|------------------|--------------------------------------------|
| phase8_best_single_fixed_heuristic   | 0.07226    | 0.0             | 0.07226             | 0.0               | 0.03122      | No               | Best held-out gap; baseline fixed heuristic|
| phase8_supervised_ml_selector         | 0.07226    | 0.0             | 0.07226             | -0.0173           | 0.03122      | Yes              | Interpretable instance-adaptive selector; near oracle quality & runtime|
| phase8_oracle_selector                | 0.07226    | 0.0             | 0.07438             | 0.029             | 0.02668      | No               | Upper bound, non-deployable oracle         |
| phase8_llm_evolved_adaptive_controller| 0.20325    | 0.131           | 0.20325             | -0.77             | 0.0922       | Yes              | Adaptive controller with runtime improvement but quality loss          |
| phase8_llm_evolved_controller_diversity_failure_replay| 0.20477| 0.133  | 0.20477             | -0.82             | 0.1133       | Yes              | Similar adaptive controller tradeoffs     |
| phase8_full_solver_evolution          | 0.21338    | 0.141           | 0.21338             | -0.86             | 0.1735       | Yes              | Highest complexity, low runtime, worst quality               |
| phase8_llm_static_selector            | 0.21431    | 0.142           | 0.21431             | -0.67             | 0.0946       | No               | Static interpretable selector but worse quality/runtime tradeoff       |
| phase8_random_portfolio               | 0.19000    | 0.1177          | 0.19000             | ~0.0              | 0.1221       | No               | Baseline random selection; worst performance|

---

### Recommendations

- The **supervised ML selector** offers the best balance of held-out TSPLIB gap, zero selector regret, moderate runtime efficiency, and interpretable instance-adaptive control. This makes it the preferable strategy for deployment.
- Adaptive controllers achieve significant runtime savings but at cost of solution quality and increased selector regret; careful tuning needed before practical use.
- Oracle selector remains a useful theoretical upper bound but not deployable.
- No new heuristic discovery claims are warranted; results focus on hyper-heuristic control improving heuristic portfolio selection.
- Further work could focus on reducing selector regret of adaptive controllers while maintaining runtime advantages, to approach oracle performance more closely.

```
