# Operator Discovery Report: two_stage_restart_controller_transfer

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically increases restart budget under 2-opt stagnation, using perturbation-based restarts to escape two-cluster bottlenecks and clustered EUC2D traps while keeping restart growth controlled for dense/grid-like
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
- Fingerprint: `429c3751789f7e53`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.881022`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `217.202229`, distance-eval delta `5733.142857`.
- `cheapest_insertion_2opt` gap delta `-0.003577`, runtime delta `764.783557`, distance-eval delta `4894.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-213.993543`, distance-eval delta `-12060.571429`.
- `sparse_three_opt` gap delta `0.038958`, runtime delta `6.4536`, distance-eval delta `106.428571`.
- `clustered_local_search` gap delta `0.010671`, runtime delta `-28.081829`, distance-eval delta `-4314.571429`.

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
- Runtime inflation: 0.881022.
- Distance-evaluation inflation: 0.91212.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
