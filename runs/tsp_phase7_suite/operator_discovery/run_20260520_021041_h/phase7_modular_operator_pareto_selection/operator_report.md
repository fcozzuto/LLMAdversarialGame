# Operator Discovery Report: stagnation_aware_acceptance_balanced_restart

- Operator type: `acceptance`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically controls bounded-worse acceptance during local search and cools later, to escape 2opt plateaus without excessive deterioration; tuned for EUC_2D transfer and two-cluster bottlenecks.
- Novelty classification: `threshold_acceptance`.
- Rediscovery signature: `acceptance:threshold:thr=0.018:temp=0.005`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Use `threshold` acceptance when a restart solution is not immediately improving.
- Relax or tighten acceptance depending on stagnation and late-search cooling.
- Reject candidate restarts that exceed the configured worse-move budget.

## Complexity
- Non-empty lines: 11.
- Complexity score: 0.42.
- Fingerprint: `d8743608d5a41495`.

## Why It Should Help
- The operator only changes restart acceptance, so any gain is attributable to a narrow exploration-vs-stability decision rule.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `28.551443`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1588.360657`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-69.4037`, distance-eval delta `-2310.285714`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `-7.085743`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.008268`, runtime delta `17.945586`, distance-eval delta `2075.428571`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.0.
- Runtime inflation: -0.001558.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `True`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `improving_only_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
- `tight_threshold_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
