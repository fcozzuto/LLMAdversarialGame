# Operator Discovery Report: det_restart_growth_compact_two_phase_perturb

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that scales restart count under stagnation and injects a structured perturbation on perturbation-enabled restarts, improving transfer on clustered and two-cluster bottleneck instances wit
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
- Fingerprint: `86607af074c2614c`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.423769`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `238.553543`, distance-eval delta `5534.857143`.
- `cheapest_insertion_2opt` gap delta `-0.002519`, runtime delta `628.8776`, distance-eval delta `4070.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-186.7227`, distance-eval delta `-11174.285714`.
- `sparse_three_opt` gap delta `0.037457`, runtime delta `-0.344457`, distance-eval delta `-235.857143`.
- `clustered_local_search` gap delta `0.00991`, runtime delta `-154.5062`, distance-eval delta `-7799.714286`.

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
- Runtime inflation: 0.423769.
- Distance-evaluation inflation: 0.795701.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
