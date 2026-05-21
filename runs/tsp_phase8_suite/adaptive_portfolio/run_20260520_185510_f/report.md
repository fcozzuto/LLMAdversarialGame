# Adaptive Heuristic Portfolio TSP Report

## Overview
- Condition count: 8.
- Best held-out TSPLIB gap: `phase8_best_single_fixed_heuristic`.
- Best combined transfer gap: `phase8_oracle_selector`.
- Lowest selector regret: `phase8_best_single_fixed_heuristic`.
- Pareto-efficient conditions: phase8_best_single_fixed_heuristic, phase8_full_solver_evolution, phase8_llm_evolved_adaptive_controller.

## Run Metadata
- run_name: run_20260520_185510_f
- started_at_local: 2026-05-20 18:55:10
- finished_at_local: 2026-05-20 19:24:08
- duration_hhmm: 00:29
- duration_seconds: 1738.022
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Final TSPLIB Gap | Selector Regret | Runtime (ms) | Runtime-Adjusted Gap | Family Gap | Transfer Gap | Mean Novelty | Mean Complexity | Pareto Efficient |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| phase8_best_single_fixed_heuristic | best_fixed | none | 0.07226 | 0.0 | 1451.927243 | 0.07226 | 0.007284 | 0.031222 | 0.0 | 0.0 | True |
| phase8_random_portfolio | random_portfolio | none | 0.187933 | 0.115673 | 1486.783929 | 0.192445 | 0.04395 | 0.096996 | 0.0 | 0.0 | False |
| phase8_oracle_selector | oracle_selector | none | 0.07226 | 0.0 | 1452.1786 | 0.072273 | 8.9e-05 | 0.026678 | 0.0 | 0.0 | False |
| phase8_supervised_ml_selector | supervised_selector | none | 0.07226 | 0.0 | 1523.144029 | 0.075804 | 0.007284 | 0.031222 | 0.0 | 0.0 | False |
| phase8_llm_static_selector | static_selector | none | 0.214311 | 0.142051 | 465.010557 | 0.214311 | 0.052514 | 0.112124 | 0.0 | 0.62 | False |
| phase8_llm_evolved_adaptive_controller | adaptive_controller | none | 0.201598 | 0.129338 | 299.300657 | 0.201598 | 0.04628 | 0.103503 | 0.0 | 0.62 | True |
| phase8_llm_evolved_controller_diversity_failure_replay | adaptive_controller | diversity_failure | 0.246315 | 0.174055 | 562.769286 | 0.246315 | 0.001913 | 0.091956 | 0.12068 | 0.62 | False |
| phase8_full_solver_evolution | full_solver | none | 0.110275 | 0.038015 | 387.225186 | 0.110275 | 0.000881 | 0.041184 | 0.771891 | 0.76 | True |

## Condition Notes
### phase8_best_single_fixed_heuristic
- Execution mode `best_fixed` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.07226`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1451.927243` ms, runtime inflation `0.0`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `True`.
- Fixed heuristic choice: `farthest_insertion_two_opt`.

### phase8_random_portfolio
- Execution mode `random_portfolio` with replay `none`.
- Final held-out gap `0.187933`, selector regret `0.115673`, runtime-adjusted gap `0.192445`.
- Family transfer `0.04395` and combined transfer `0.096996`.
- Runtime `1486.783929` ms, runtime inflation `0.024007`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_oracle_selector
- Execution mode `oracle_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.072273`.
- Family transfer `8.9e-05` and combined transfer `0.026678`.
- Runtime `1452.1786` ms, runtime inflation `0.000173`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_supervised_ml_selector
- Execution mode `supervised_selector` with replay `none`.
- Final held-out gap `0.07226`, selector regret `0.0`, runtime-adjusted gap `0.075804`.
- Family transfer `0.007284` and combined transfer `0.031222`.
- Runtime `1523.144029` ms, runtime inflation `0.04905`, mean novelty `0.0`, and complexity `0.0`.
- Pareto efficient: `False`.

### phase8_llm_static_selector
- Execution mode `static_selector` with replay `none`.
- Final held-out gap `0.214311`, selector regret `0.142051`, runtime-adjusted gap `0.214311`.
- Family transfer `0.052514` and combined transfer `0.112124`.
- Runtime `465.010557` ms, runtime inflation `-0.679729`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:limited_three_opt:edge_preserving_restart:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "edge_preserving_restart", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive frozen-portfolio selector using structure descriptors; chooses an interpretable heuristic per regime and provides bounded schedule/tuning parameters for later-stage refinement.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "limited_three_opt", "low_improvement_threshold": 0.05, "name": "tsp_ihx_frozen_portfolio_epoch1_static_rules", "nearest_neighbor_trap_heuristic": "annealed_multi_start", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "edge_preserving_restart", "stagnation_threshold": 3, "temperature_scale": 1.05, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "limited_three_opt"}

### phase8_llm_evolved_adaptive_controller
- Execution mode `adaptive_controller` with replay `none`.
- Final held-out gap `0.201598`, selector regret `0.129338`, runtime-adjusted gap `0.201598`.
- Family transfer `0.04628` and combined transfer `0.103503`.
- Runtime `299.300657` ms, runtime inflation `-0.79386`, mean novelty `0.0`, and complexity `0.62`.
- Pareto efficient: `True`.
- Controller signature: `nearest_neighbor_multistart:cluster_first_local_search:edge_preserving_restart:annealed_multi_start:stag3:cand2:restart1`.
- Controller rule summary: {"acceptance_bias": 0.006, "candidate_limit_offset": 2, "clustered_heuristic": "cluster_first_local_search", "corridor_heuristic": "annealed_multi_start", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive controller selecting from a frozen heuristic portfolio with bounded online schedule tuning based on stagnation, improvement rate, and perturbation failures.", "failed_perturbation_threshold": 2, "grid_like_heuristic": "cheapest_insertion_two_opt", "low_improvement_threshold": 0.06, "name": "det_tsp_hh_oracle_style_portfolio_adaptive_v1", "nearest_neighbor_trap_heuristic": "candidate_pruned_two_opt", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 1, "stagnation_switch_heuristic": "annealed_multi_start", "stagnation_threshold": 3, "temperature_scale": 1.15, "time_budget_trigger": 0.7, "two_cluster_bottleneck_heuristic": "edge_preserving_restart"}

### phase8_llm_evolved_controller_diversity_failure_replay
- Execution mode `adaptive_controller` with replay `diversity_failure`.
- Final held-out gap `0.246315`, selector regret `0.174055`, runtime-adjusted gap `0.246315`.
- Family transfer `0.001913` and combined transfer `0.091956`.
- Runtime `562.769286` ms, runtime inflation `-0.612398`, mean novelty `0.12068`, and complexity `0.62`.
- Pareto efficient: `False`.
- Controller signature: `nearest_neighbor_multistart:cheapest_insertion_two_opt:farthest_insertion_two_opt:nearest_neighbor_multistart:stag4:cand-1:restart2`.
- Controller rule summary: {"acceptance_bias": 0.008, "candidate_limit_offset": -1, "clustered_heuristic": "cheapest_insertion_two_opt", "corridor_heuristic": "limited_three_opt", "default_heuristic": "farthest_insertion_two_opt", "description": "Deterministic instance-adaptive hyper-heuristic controller selecting one frozen TSP heuristic and tuning bounded schedule knobs from online stability signals.", "failed_perturbation_threshold": 3, "grid_like_heuristic": "candidate_pruned_two_opt", "low_improvement_threshold": 0.12, "name": "interpretable_adaptive_tsp_hh_controller_v2", "nearest_neighbor_trap_heuristic": "cluster_first_local_search", "random_like_heuristic": "nearest_neighbor_multistart", "restart_offset": 2, "stagnation_switch_heuristic": "nearest_neighbor_multistart", "stagnation_threshold": 4, "temperature_scale": 1.25, "time_budget_trigger": 0.55, "two_cluster_bottleneck_heuristic": "farthest_insertion_two_opt"}

### phase8_full_solver_evolution
- Execution mode `full_solver` with replay `none`.
- Final held-out gap `0.110275`, selector regret `0.038015`, runtime-adjusted gap `0.110275`.
- Family transfer `0.000881` and combined transfer `0.041184`.
- Runtime `387.225186` ms, runtime inflation `-0.733303`, mean novelty `0.771891`, and complexity `0.76`.
- Pareto efficient: `True`.

## Judge Appendix
### Conservative Interpretation of TSP Adaptive Heuristic Portfolio Suite Results

#### Prioritized Metrics Summary  
| Condition                          | Held-out TSPLIB Gap | Selector Regret | Runtime-Adjusted Gap | TSPLIB Runtime (ms) | Runtime Inflation | Transfer Gap | Pareto Efficient | Comments |
|-----------------------------------|---------------------|-----------------|---------------------|---------------------|-------------------|--------------|------------------|----------|
| **phase8_best_single_fixed_heuristic** (Best TSPLIB) | **0.07226**         | 0.0             | 0.07226             | 1452                | 0.0               | 0.0312       | Yes              | Best fixed heuristic, no runtime inflation, solid baseline |
| phase8_oracle_selector (Best Transfer)                | 0.07226             | 0.0             | 0.07227             | 1452                | ~0                | **0.0267**   | No               | Oracle upper bound, not deployable, validates best fixed result |
| phase8_llm_evolved_adaptive_controller (Pareto)      | 0.2016              | 0.1293          | 0.2016              | 299                 | -0.79             | 0.1035       | Yes              | Adaptive, much faster runtime, significant regret, runtime gain |
| phase8_full_solver_evolution (Pareto)                 | 0.1103              | 0.0380          | 0.1103              | 387                 | -0.73             | 0.0412       | Yes              | Evolved full solver, moderate gap and regret, strong runtime gain |
| phase8_llm_static_selector                              | 0.2143              | 0.1421          | 0.2143              | 465                 | -0.68             | 0.1121       | No               | Static selector, worse gap and regret despite runtime reduction |
| phase8_llm_evolved_controller_diversity_failure_replay| 0.2463              | 0.1740          | 0.2463              | 563                 | -0.61             | 0.0920       | No               | Adaptive with replay, highest gap and regret, moderate runtime gain |
| phase8_random_portfolio                                 | 0.1879              | 0.1157          | 0.1924              | 1487                | 0.02              | 0.0970       | No               | Random baseline, poor gap and regret, no runtime improvement |

---

### Key Insights

1. **Held-out TSPLIB Gap (Primary Endpoint)**  
   - The **best single fixed heuristic (farthest_insertion_two_opt)** achieves the lowest held-out TSPLIB gap (0.07226), tied with the oracle selector (upper bound).  
   - Adaptive selectors and evolved controllers have significantly higher gaps (0.1103 to 0.2463), indicating no definitive improvement in solution quality yet.

2. **Selector Regret vs Oracle Portfolio**  
   - Oracle selector regret is zero by definition (upper bound).  
   - The best adaptive controller (phase8_full_solver_evolution) shows moderate regret (0.038), while other adaptive methods regret is larger (0.13-0.17), indicating imperfect instance adaptation.  
   - The fixed heuristic selector has zero regret but no adaptability.

3. **Runtime-Adjusted Gap & Runtime Inflation**  
   - The best fixed heuristic has zero runtime inflation but longer runtime (~1452 ms).  
   - Adaptive controllers and evolved solvers offer large negative runtime inflation (-0.73 to -0.79), i.e., *significant runtime speedups*.  
   - However, these runtime reductions come with increased performance gap, reflecting a tradeoff between speed and quality.  
   - The static selector also reduces runtime but at cost of poorer gaps and higher regret.

4. **Pareto Efficiency**  
   - Three conditions are Pareto-efficient: the fixed best heuristic, the evolved full solver, and the evolved adaptive controller.  
   - These represent meaningful tradeoffs along the quality-runtime spectrum.  
   - Adaptive controllers provide faster runtime with moderate quality loss; best fixed heuristic optimal for highest solution quality without runtime gain.

5. **Cross-family Transfer**  
   - Transfer gaps are smaller for the best fixed heuristic (0.0312) and evolved full solver (0.0412) than adaptive controllers (0.091-0.103).  
   - Oracle selector lowest transfer gap (0.027), as expected.  
   - This suggests adaptive controllers may have less robust transfer/generalization and adaptation efficiency can be improved.

6. **Instance-Adaptive Control Interpretability**  
   - Adaptive controllers use interpretable frozen heuristic portfolios with rules tuned on stagnation and improvement signals.  
   - However, these do not yet approach the oracle in gap or regret, limiting claims of near-oracle interpretability without runtime inflation.  
   - Static selector simpler but has poorer tradeoffs and should not be preferred for deployment.

---

### Summary Statement

The best single fixed heuristic ("farthest_insertion_two_opt") remains the strongest baseline with the lowest held-out TSPLIB gap and zero selector regret, serving as a solid upper baseline for practical deployment without runtime cost. The oracle selector corroborates this performance as an unattainable upper bound.

Adaptive hyper-heuristic controllers and evolved solvers provide significant runtime reductions (up to ~79% faster) and represent meaningful Pareto tradeoffs, though with increased solution quality gaps and selector regret. Among these, the evolved full solver displays moderate regret with fair, lower gap and runtime gains, highlighting the potential for interpretable instance-adaptive control within a bounded schedule tuning framework. Cross-family transfer remains a challenge, with adaptive selectors showing higher transfer gaps than fixed heuristics.

Given the current results, conservative claims focus on effective *interpretable instance-adaptive portfolio control* enabling runtime-quality tradeoffs, rather than discovery of better heuristics or near-oracle adaptive performance. Further improvements should target reducing selector regret and closing the quality gap while preserving runtime benefits.
