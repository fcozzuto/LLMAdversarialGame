# Operator Discovery Report: instance_adaptive_restart_controller_two_cluster_escape

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Trigger restarts more readily on high-bottleneck / trap instances with controlled growth; optionally re-inject perturbations to escape 2-opt plateaus while avoiding excessive restart churn on easy cases.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:7:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `0a286da66549a30d`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.718077`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `211.268471`, distance-eval delta `6102.285714`.
- `cheapest_insertion_2opt` gap delta `-0.002794`, runtime delta `1194.841371`, distance-eval delta `4542.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-178.813443`, distance-eval delta `-11293.142857`.
- `sparse_three_opt` gap delta `0.035379`, runtime delta `3.520157`, distance-eval delta `-214.142857`.
- `clustered_local_search` gap delta `0.003068`, runtime delta `-119.177214`, distance-eval delta `-5093.428571`.

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
- Runtime inflation: 0.718077.
- Distance-evaluation inflation: 0.866865.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
