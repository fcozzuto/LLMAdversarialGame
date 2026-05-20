# Operator Discovery Report: restart_controller_adaptive_2opt_escape_v1

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart schedule for nearest-neighbor+2opt plateaus: triggers restarts on short stagnation and grows counts mildly, using the scaffold perturbation to escape 2-opt dead-ends while keeping restart pressure m
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
- Fingerprint: `d4762a5f674ce2ec`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `1.097128`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `214.0466`, distance-eval delta `4602.857143`.
- `cheapest_insertion_2opt` gap delta `-0.002584`, runtime delta `941.245357`, distance-eval delta `3870.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-225.146143`, distance-eval delta `-12109.142857`.
- `sparse_three_opt` gap delta `0.03898`, runtime delta `-56.294186`, distance-eval delta `-299.285714`.
- `clustered_local_search` gap delta `0.009794`, runtime delta `-146.916671`, distance-eval delta `-7954.0`.

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
- Runtime inflation: 1.097128.
- Distance-evaluation inflation: 0.9834.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.005462`.
- `fixed_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.115856` and delta vs full operator `0.0`.
