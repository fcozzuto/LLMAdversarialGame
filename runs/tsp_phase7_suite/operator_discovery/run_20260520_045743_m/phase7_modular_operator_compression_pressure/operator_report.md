# Operator Discovery Report: det_restart_controller_two_cluster_bottleneck

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart scheduling that triggers perturbation-based restarts under stagnation, then grows restart count conservatively to improve transfer on bottleneck/clustered EUC instances without changing the core loc
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
- Fingerprint: `211c74474fbe83b2`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `0.616565`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `139.778629`, distance-eval delta `5471.428571`.
- `cheapest_insertion_2opt` gap delta `-0.002814`, runtime delta `676.948914`, distance-eval delta `4510.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-157.765486`, distance-eval delta `-10183.428571`.
- `sparse_three_opt` gap delta `0.036996`, runtime delta `-71.189429`, distance-eval delta `-219.857143`.
- `clustered_local_search` gap delta `0.001517`, runtime delta `-19.241857`, distance-eval delta `-7277.428571`.

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
- Runtime inflation: 0.616565.
- Distance-evaluation inflation: 0.763692.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
