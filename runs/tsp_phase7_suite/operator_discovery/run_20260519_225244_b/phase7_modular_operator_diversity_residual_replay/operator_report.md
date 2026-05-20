# Operator Discovery Report: transfer_robust_restart_controller_v2

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth with structured perturbation restarts; triggers earlier on stagnation and keeps restart budget moderate to improve transfer on clustered/bottleneck layouts without turning into an unbounded s
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `d226f682dde165c5`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.677344`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `219.246886`, distance-eval delta `5708.0`.
- `cheapest_insertion_2opt` gap delta `-0.002929`, runtime delta `639.236486`, distance-eval delta `4614.857143`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-164.024529`, distance-eval delta `-11008.571429`.
- `sparse_three_opt` gap delta `0.03836`, runtime delta `0.366786`, distance-eval delta `-161.571429`.
- `clustered_local_search` gap delta `0.006421`, runtime delta `-128.842157`, distance-eval delta `-6931.142857`.

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
- Runtime inflation: 0.677344.
- Distance-evaluation inflation: 0.804735.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
