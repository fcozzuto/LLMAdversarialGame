# Operator Discovery Report: det_restart_ctrl_twocluster_bottleneck_boost

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that triggers when bounded progress stalls; uses perturbation-backed restarts and moderate growth to better escape two-cluster bottlenecks and mixed EUC2D traps without changing the core 
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `87c9e2bca0839fee`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.707203`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `226.9978`, distance-eval delta `5783.428571`.
- `cheapest_insertion_2opt` gap delta `-0.000491`, runtime delta `863.244714`, distance-eval delta `4070.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-197.744657`, distance-eval delta `-10874.857143`.
- `sparse_three_opt` gap delta `0.039374`, runtime delta `0.972957`, distance-eval delta `-329.0`.
- `clustered_local_search` gap delta `0.01081`, runtime delta `-104.275957`, distance-eval delta `-6462.571429`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.005462.
- Runtime inflation: 0.707203.
- Distance-evaluation inflation: 0.784605.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
