# Operator Discovery Report: det_restart_controller_stagnation_balanced_euc2d

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth tuned for EUC2D: triggers on moderate stagnation, uses a small seed pool, and applies perturbations on restart to escape local traps without excessive restart churn.
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
- Fingerprint: `8276568a7613c42c`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.669401`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `239.984957`, distance-eval delta `5316.571429`.
- `cheapest_insertion_2opt` gap delta `-0.00272`, runtime delta `963.676371`, distance-eval delta `4222.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-225.240257`, distance-eval delta `-12845.142857`.
- `sparse_three_opt` gap delta `0.037871`, runtime delta `-1.7777`, distance-eval delta `-219.285714`.
- `clustered_local_search` gap delta `0.009741`, runtime delta `-92.1954`, distance-eval delta `-5447.714286`.

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
- Runtime inflation: 0.669401.
- Distance-evaluation inflation: 0.767933.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
