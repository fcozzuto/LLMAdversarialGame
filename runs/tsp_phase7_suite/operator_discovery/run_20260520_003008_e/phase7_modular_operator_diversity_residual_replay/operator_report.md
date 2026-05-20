# Operator Discovery Report: acceptance_threshold_worse_moves_with_stagnation_bonus

- Operator type: `acceptance`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Allow a small amount of bounded worse 2-opt moves using a low threshold; add extra acceptance probability when the search is stagnating to escape NN traps without turning into a full restart strategy.
- Novelty classification: `threshold_acceptance`.
- Rediscovery signature: `acceptance:threshold:thr=0.018:temp=0.000`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Use `threshold` acceptance when a restart solution is not immediately improving.
- Relax or tighten acceptance depending on stagnation and late-search cooling.
- Reject candidate restarts that exceed the configured worse-move budget.

## Complexity
- Non-empty lines: 11.
- Complexity score: 0.42.
- Fingerprint: `8221967b485bffa9`.

## Why It Should Help
- The operator only changes restart acceptance, so any gain is attributable to a narrow exploration-vs-stability decision rule.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `-86.828329`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1034.308557`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-6.184414`, distance-eval delta `-524.0`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `-1.237557`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.007599`, runtime delta `66.128943`, distance-eval delta `1329.428571`.

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
- Runtime inflation: -0.00642.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `True`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `improving_only_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
- `tight_threshold_acceptance` mean gap `0.121317` and delta vs full operator `0.0`.
