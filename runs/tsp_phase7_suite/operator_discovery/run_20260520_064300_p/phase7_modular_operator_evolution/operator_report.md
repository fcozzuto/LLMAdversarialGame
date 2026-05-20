# Operator Discovery Report: epoch6_transfer_restart_controller_two_stage_escape

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Drive deterministic restarts with controlled growth; trigger earlier on stagnation to escape structured traps while limiting restart budget for transfer robustness.
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
- Fingerprint: `75fcca947c517db2`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.790432`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `226.009229`, distance-eval delta `6248.0`.
- `cheapest_insertion_2opt` gap delta `-0.000491`, runtime delta `1598.829157`, distance-eval delta `4062.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-196.445143`, distance-eval delta `-10960.0`.
- `sparse_three_opt` gap delta `0.038483`, runtime delta `3.011371`, distance-eval delta `-19.285714`.
- `clustered_local_search` gap delta `0.009278`, runtime delta `-49.4235`, distance-eval delta `-4746.0`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.002615.
- Runtime inflation: 0.790432.
- Distance-evaluation inflation: 0.856118.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
