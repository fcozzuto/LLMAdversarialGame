# Operator Discovery Report: two_cluster_bottleneck_stagnation_perturbation_restart_controller

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic stagnation-aware restart controller with optional perturbation restarts; triggers more often on difficult bottleneck-like instances while capping total restarts for runtime stability. Parameterized to trans
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `b9fd1976b1f4df02`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.977422`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `146.953186`, distance-eval delta `4830.285714`.
- `cheapest_insertion_2opt` gap delta `-0.002702`, runtime delta `1276.115071`, distance-eval delta `3566.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-243.858143`, distance-eval delta `-13398.285714`.
- `sparse_three_opt` gap delta `0.035224`, runtime delta `8.119657`, distance-eval delta `32.142857`.
- `clustered_local_search` gap delta `0.012072`, runtime delta `-105.229857`, distance-eval delta `-5890.0`.

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
- Runtime inflation: 0.977422.
- Distance-evaluation inflation: 0.97364.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
