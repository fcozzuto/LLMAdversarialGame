# Operator Discovery Report: transfer_candidate_pruner_sticky_size

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically limit local candidate moves using a compact base list, increasing focus when instances look grid-like or clustered, and backing off when stagnation suggests traps.
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:18:-4:3:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `4ba619c8530de1f4`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.316569`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `65.175371`, distance-eval delta `2186.714286`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `252.454943`, distance-eval delta `1111.428571`.
- `random_restart_2opt` gap delta `0.001067`, runtime delta `2.242143`, distance-eval delta `1844.428571`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `53.7399`, distance-eval delta `4353.428571`.
- `clustered_local_search` gap delta `0.015514`, runtime delta `150.475243`, distance-eval delta `6061.142857`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235667` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.000224.
- Runtime inflation: 0.316569.
- Distance-evaluation inflation: 0.22697.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
