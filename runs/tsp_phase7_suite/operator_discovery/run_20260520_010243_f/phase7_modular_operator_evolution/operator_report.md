# Operator Discovery Report: restart_controller_strong_escape_kro_gridtrap

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth with earlier stagnation triggering and frequent perturbation-backed restarts; tuned for clustered/two-cluster bottleneck and trap-prone instances to escape 2opt/NN local minima reliably.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:3:9:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `af1d08118f6af3c6`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `1.835159`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `400.122114`, distance-eval delta `11516.571429`.
- `cheapest_insertion_2opt` gap delta `-0.005009`, runtime delta `1065.377543`, distance-eval delta `9796.571429`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-149.053057`, distance-eval delta `-8190.857143`.
- `sparse_three_opt` gap delta `0.035487`, runtime delta `87.609286`, distance-eval delta `5038.142857`.
- `clustered_local_search` gap delta `-0.003885`, runtime delta `104.623014`, distance-eval delta `4234.857143`.

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
- Runtime inflation: 1.835159.
- Distance-evaluation inflation: 1.785695.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
