# Operator Discovery Report: transfer_restart_controller_bottleneck_escape_2opt

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth that triggers early under stagnation (tighter for trap-prone layouts) and uses perturbation on restarts; keeps restart budget moderate to preserve transfer across grid/mixed instances.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:6:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `0fbd8de1c2b96f47`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.821431`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `263.478986`, distance-eval delta `6246.857143`.
- `cheapest_insertion_2opt` gap delta `-0.002438`, runtime delta `1945.966314`, distance-eval delta `4406.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-232.458871`, distance-eval delta `-13171.428571`.
- `sparse_three_opt` gap delta `0.037684`, runtime delta `1.752043`, distance-eval delta `-243.285714`.
- `clustered_local_search` gap delta `0.016621`, runtime delta `-83.704957`, distance-eval delta `-6857.428571`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110431` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.003304.
- Runtime inflation: 0.821431.
- Distance-evaluation inflation: 0.869479.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
