# Operator Discovery Report: candidate_pruner_scale_by_structure_escape_bias

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic candidate-list size adaptation to improve transfer on clustered/grid/two-cluster-bottleneck cases; balances pruning aggressiveness via instance descriptors to reduce stagnation risk without exploding move e
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:20:-2:-1:3`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `1c397e651ec235b4`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.089548.
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000813`, runtime delta `69.486486`, distance-eval delta `-374.857143`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `740.939957`, distance-eval delta `62.285714`.
- `random_restart_2opt` gap delta `-0.000421`, runtime delta `-48.754557`, distance-eval delta `-493.285714`.
- `sparse_three_opt` gap delta `0.000379`, runtime delta `20.086271`, distance-eval delta `1797.857143`.
- `clustered_local_search` gap delta `0.025002`, runtime delta `-118.296786`, distance-eval delta `-3584.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235871` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.196244` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.009726.
- Runtime inflation: -0.126442.
- Distance-evaluation inflation: -0.01997.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.009726`.
- `constant_pruner` mean gap `0.121317` and delta vs full operator `-0.009726`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `-0.009501`.
