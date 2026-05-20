# Operator Discovery Report: det_restart_controller_gradual_growth_with_perturbation_restarts

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart schedule: trigger after short 2-opt stagnation, start with a small restart budget, and grow cautiously; on each restart, allow perturbation-based diversification to avoid being trapped in the same 2
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
- Fingerprint: `a811bfca71139c20`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.825788`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `155.878686`, distance-eval delta `4894.857143`.
- `cheapest_insertion_2opt` gap delta `-0.00316`, runtime delta `2022.265414`, distance-eval delta `4390.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-214.316486`, distance-eval delta `-12105.142857`.
- `sparse_three_opt` gap delta `0.037957`, runtime delta `2.822243`, distance-eval delta `-122.714286`.
- `clustered_local_search` gap delta `0.014283`, runtime delta `-85.523829`, distance-eval delta `-6574.0`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.105127` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.005462.
- Runtime inflation: 0.825788.
- Distance-evaluation inflation: 0.892165.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
