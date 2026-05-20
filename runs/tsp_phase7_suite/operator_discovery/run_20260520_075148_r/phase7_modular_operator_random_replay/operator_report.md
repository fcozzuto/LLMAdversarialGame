# Operator Discovery Report: restart_controller_episodic_perturbation_escape

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth with periodic perturbation restarts to escape 2-opt stagnation; ramps restart count only after repeated non-improvement to improve transfer on mixed and bottleneck instances.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:9:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `79c89beb098ae6d1`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.909128`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `188.495157`, distance-eval delta `4191.428571`.
- `cheapest_insertion_2opt` gap delta `-0.002769`, runtime delta `304.158143`, distance-eval delta `4318.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-220.938857`, distance-eval delta `-13173.142857`.
- `sparse_three_opt` gap delta `0.039098`, runtime delta `9.050929`, distance-eval delta `198.428571`.
- `clustered_local_search` gap delta `0.00762`, runtime delta `-80.916357`, distance-eval delta `-6216.857143`.

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
- Runtime inflation: 0.909128.
- Distance-evaluation inflation: 0.88592.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
