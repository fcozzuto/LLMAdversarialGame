# Operator Discovery Report: restart_controller_deterministic_perturb_restart_pool

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Escalates deterministic restarts under stagnation using a small seed pool; enables perturbation-based restarts to escape bottlenecks/trap layouts while keeping restart growth controlled for transfer robustness.
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
- Fingerprint: `2fc32754a2e44a8c`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.892423`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `264.607157`, distance-eval delta `6411.428571`.
- `cheapest_insertion_2opt` gap delta `-0.0007`, runtime delta `1991.225586`, distance-eval delta `4158.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-223.342871`, distance-eval delta `-12690.857143`.
- `sparse_three_opt` gap delta `0.039847`, runtime delta `6.764543`, distance-eval delta `-127.285714`.
- `clustered_local_search` gap delta `0.003902`, runtime delta `-38.510629`, distance-eval delta `-5594.0`.

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
- Runtime inflation: 0.892423.
- Distance-evaluation inflation: 0.884148.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
