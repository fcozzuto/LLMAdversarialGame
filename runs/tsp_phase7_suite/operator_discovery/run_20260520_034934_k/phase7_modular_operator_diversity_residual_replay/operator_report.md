# Operator Discovery Report: restart_controller_two_phase_bottleneck_v1

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart-count controller with perturbation-enabled restarts; triggers more frequent restarts on stagnation (especially for two-cluster bottlenecks) while keeping growth bounded for transfer stability.
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
- Fingerprint: `1c751f172211314c`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `1.51959`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `286.928971`, distance-eval delta `10403.428571`.
- `cheapest_insertion_2opt` gap delta `-0.001632`, runtime delta `951.0058`, distance-eval delta `8589.142857`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-151.159771`, distance-eval delta `-7988.0`.
- `sparse_three_opt` gap delta `0.036775`, runtime delta `59.4863`, distance-eval delta `3681.571429`.
- `clustered_local_search` gap delta `-0.008943`, runtime delta `8.116329`, distance-eval delta `246.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.104566` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.005462.
- Runtime inflation: 1.51959.
- Distance-evaluation inflation: 1.664774.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
