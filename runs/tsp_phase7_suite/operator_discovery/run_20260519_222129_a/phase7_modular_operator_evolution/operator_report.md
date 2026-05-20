# Operator Discovery Report: restart_escape_control_2opt_transfer

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that grows restarts under stagnation and enables a perturbation-based escape each restart to prevent 2-opt-style neighborhoods from getting stuck, with conservative growth to preserve tra
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:7:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `d9e51600741992de`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.849429`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `180.979243`, distance-eval delta `4915.428571`.
- `cheapest_insertion_2opt` gap delta `-0.002742`, runtime delta `616.1672`, distance-eval delta `4398.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-250.467443`, distance-eval delta `-12498.285714`.
- `sparse_three_opt` gap delta `0.037427`, runtime delta `11.717157`, distance-eval delta `-230.714286`.
- `clustered_local_search` gap delta `0.007401`, runtime delta `-98.717643`, distance-eval delta `-5391.714286`.

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
- Runtime inflation: 0.849429.
- Distance-evaluation inflation: 0.766132.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
