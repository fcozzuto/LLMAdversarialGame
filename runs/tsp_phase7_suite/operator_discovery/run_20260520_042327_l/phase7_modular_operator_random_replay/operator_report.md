# Operator Discovery Report: bounded_worse_threshold_acceptance_stagnation_bias

- Operator type: `acceptance`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically allows a small, structure-agnostic amount of bounded-worse 2-opt/edge-relink moves to break 2-opt plateaus; acceptance tightens with late-search cooling and relaxes slightly under short stagnation burst
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
- Fingerprint: `adef96fd584bc090`.

## Why It Should Help
- The operator only changes restart acceptance, so any gain is attributable to a narrow exploration-vs-stability decision rule.

## Failure Cases
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `111.858443`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `502.796929`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `2.1704`, distance-eval delta `252.0`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `6.232029`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `-0.000666`, runtime delta `-9.484543`, distance-eval delta `1594.285714`.

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
- Runtime inflation: 0.013898.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `improving_only_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
- `tight_threshold_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
