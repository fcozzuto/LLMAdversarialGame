# Operator Discovery Report: restart_controller_adaptive_2x_pool

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that grows restart count moderately under stagnation, with a small seed pool and optional perturbation restarts to help escape long 2-opt plateaus on bottleneck/two-cluster instances.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:7:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `827019f4ff1e864b`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `0.623816`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `201.539986`, distance-eval delta `5590.857143`.
- `cheapest_insertion_2opt` gap delta `-0.002995`, runtime delta `844.364843`, distance-eval delta `4462.857143`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-171.145486`, distance-eval delta `-10716.0`.
- `sparse_three_opt` gap delta `0.038805`, runtime delta `-4.093`, distance-eval delta `-367.857143`.
- `clustered_local_search` gap delta `0.002851`, runtime delta `-127.175214`, distance-eval delta `-6300.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.105127` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.005462.
- Runtime inflation: 0.623816.
- Distance-evaluation inflation: 0.763082.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
