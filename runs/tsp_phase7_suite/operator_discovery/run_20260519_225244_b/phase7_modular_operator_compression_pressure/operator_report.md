# Operator Discovery Report: berlin52_transfer_restart_scope

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic bounded-worsening acceptance plus adaptive candidate pruning and restart control to improve transfer across EUC_2D clustered/two-cluster instances without rewriting the scaffold.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:3:8:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `4129068788dbf6d7`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `1.374482`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `299.895657`, distance-eval delta `10624.0`.
- `cheapest_insertion_2opt` gap delta `-0.004385`, runtime delta `715.648529`, distance-eval delta `9989.142857`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-85.544486`, distance-eval delta `-6557.714286`.
- `sparse_three_opt` gap delta `0.030566`, runtime delta `74.411314`, distance-eval delta `4746.714286`.
- `clustered_local_search` gap delta `-0.004697`, runtime delta `-34.593086`, distance-eval delta `-272.571429`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110431` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.003363.
- Runtime inflation: 1.374482.
- Distance-evaluation inflation: 1.609585.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003363`.
- `fixed_restart_budget` mean gap `0.117954` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000266`.
