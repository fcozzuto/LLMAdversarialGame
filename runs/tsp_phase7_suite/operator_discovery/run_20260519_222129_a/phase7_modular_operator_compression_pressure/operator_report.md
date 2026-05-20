# Operator Discovery Report: transfer_restart_controller_bottleneck_escape_dense

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth tuned to escape 2-opt stagnation on bottleneck/two-cluster EUC instances while limiting restart explosion on already-stable runs.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `bb9aca1cafd01c7b`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.702383`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `196.2423`, distance-eval delta `4997.714286`.
- `cheapest_insertion_2opt` gap delta `-0.003807`, runtime delta `714.786714`, distance-eval delta `4934.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-222.050114`, distance-eval delta `-12180.571429`.
- `sparse_three_opt` gap delta `0.035903`, runtime delta `-4.160814`, distance-eval delta `-299.285714`.
- `clustered_local_search` gap delta `0.003769`, runtime delta `-168.006757`, distance-eval delta `-8116.285714`.

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
- Runtime inflation: 0.702383.
- Distance-evaluation inflation: 0.788207.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
