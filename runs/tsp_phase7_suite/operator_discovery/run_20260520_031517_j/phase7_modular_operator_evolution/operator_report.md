# Operator Discovery Report: det_restart_controller_two_cluster_aware_fast_growth

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that triggers early on stagnation and ramps restarts moderately; enables perturbation-based restarts to escape two-cluster/bottleneck traps while capping total restart count for 2-opt sta
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:3:9:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `5f3ba17d1d262af9`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `2.139159`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `254.750957`, distance-eval delta `9233.142857`.
- `cheapest_insertion_2opt` gap delta `-0.003457`, runtime delta `1126.381271`, distance-eval delta `8004.571429`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-149.1348`, distance-eval delta `-7750.285714`.
- `sparse_three_opt` gap delta `0.033767`, runtime delta `61.559129`, distance-eval delta `4034.142857`.
- `clustered_local_search` gap delta `0.006887`, runtime delta `-37.965157`, distance-eval delta `-1834.0`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.002615.
- Runtime inflation: 2.139159.
- Distance-evaluation inflation: 1.934645.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
