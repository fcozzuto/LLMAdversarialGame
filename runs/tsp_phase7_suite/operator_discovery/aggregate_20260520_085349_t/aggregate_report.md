# Phase 7 Aggregate Report

## Overview
- Run count: 20.
- Condition count: 7.
- Best transfer condition: `phase7_full_solver_evolution`.

## Condition Means
| Condition | Final Transfer Gap | Final TSPLIB Gap | Final Family Gap | Mean Novelty | Mean Complexity | Transplant Delta | Pareto Runtime Inflation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase7_baseline_heuristic_only | 0.121317 | 0.235058 | 0.054968 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase7_full_solver_evolution | 0.117916 | 0.164668 | 0.036098 | 0.832777 | 0.65 | 0.0 | 0.0 |
| phase7_modular_operator_compression_pressure | 0.118865 | 0.232947 | 0.052316 | 0.560556 | 0.44375 | 0.005698 | 0.802631 |
| phase7_modular_operator_diversity_residual_replay | 0.121843 | 0.231468 | 0.057894 | 0.711483 | 0.443 | 0.003445 | 1.684384 |
| phase7_modular_operator_evolution | 0.119602 | 0.232023 | 0.054022 | 0.804885 | 0.442875 | 0.003951 | 1.801854 |
| phase7_modular_operator_pareto_selection | 0.126012 | 0.237085 | 0.06122 | 0.591492 | 0.44475 | 0.006265 | 0.196727 |
| phase7_modular_operator_random_replay | 0.118833 | 0.230474 | 0.053709 | 0.771204 | 0.4445 | 0.003847 | 0.476892 |

## Paired Comparisons
- `modular_vs_baseline_only`: transfer delta `-0.001715` (95% CI `-0.003418` to `8.5e-05`), TSPLIB delta `-0.003035`.
- `modular_vs_full_solver`: transfer delta `0.001686` (95% CI `-0.018321` to `0.022827`), TSPLIB delta `0.067355`.
- `random_vs_modular_base`: transfer delta `-0.000768` (95% CI `-0.002519` to `0.000889`), TSPLIB delta `-0.001549`.
- `diversity_residual_vs_random`: transfer delta `0.003009` (95% CI `-0.002884` to `0.010797`), TSPLIB delta `0.000994`.
- `compression_vs_modular_base`: transfer delta `-0.000737` (95% CI `-0.004573` to `0.002479`), TSPLIB delta `0.000924`.
- `pareto_vs_modular_base`: transfer delta `0.006411` (95% CI `0.001983` to `0.012533`), TSPLIB delta `0.005061`.

## Rediscovery
- Signature count: 56.
- Most common surviving signature: `None`.

## Discovery Answers
- modular_vs_full_solver: Relative to full-solver evolution, the base modular operator condition changed transfer by 0.001686 and transplant quality by 0.003951.
- pareto_tradeoff: Pareto selection changed transfer by 0.006411 and runtime inflation by -1.605126 relative to the base modular condition.
- rediscovery: Rediscovery produced 56 distinct signatures; the most common surviving signature is `None`.
- replay_mechanism: Random replay changed modular transfer by -0.000768 versus the no-replay modular baseline, while diversity-residual replay changed transfer by 0.003009 versus random replay.
