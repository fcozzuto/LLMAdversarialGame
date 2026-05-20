# Operator Discovery Report: stagnation_reset_restart_controller_berlin_lin_mixed

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart escalation for stagnation: trigger modestly early, grow restarts gradually, and allow perturbation-based restarts to diversify when local improvement stalls.
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
- Fingerprint: `2d401ca229aa625e`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `0.928358`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `96.527171`, distance-eval delta `3571.428571`.
- `cheapest_insertion_2opt` gap delta `-0.000244`, runtime delta `1103.232614`, distance-eval delta `4430.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-223.969229`, distance-eval delta `-12326.857143`.
- `sparse_three_opt` gap delta `0.034327`, runtime delta `7.187`, distance-eval delta `112.714286`.
- `clustered_local_search` gap delta `0.002727`, runtime delta `-19.923043`, distance-eval delta `-4605.428571`.

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
- Runtime inflation: 0.928358.
- Distance-evaluation inflation: 0.911481.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
