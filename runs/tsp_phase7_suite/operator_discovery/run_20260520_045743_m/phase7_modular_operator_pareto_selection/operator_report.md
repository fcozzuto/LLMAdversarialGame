# Operator Discovery Report: candidate_pruner_transfer_adaptive_local_trap_guard

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically adapts local-search candidate-list size using instance descriptors, pruning more aggressively on easy/clustered cases while keeping more candidates for bottleneck/two-cluster and grid-like structures to
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:18:3:2:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `e37efb0280351232`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `117.623186`, distance-eval delta `1477.857143`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `861.577257`, distance-eval delta `857.714286`.
- `random_restart_2opt` gap delta `0.001067`, runtime delta `98.731229`, distance-eval delta `3803.285714`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `43.968814`, distance-eval delta `3452.428571`.
- `clustered_local_search` gap delta `0.015041`, runtime delta `271.542843`, distance-eval delta `6963.142857`.

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
- Runtime inflation: 0.197399.
- Distance-evaluation inflation: 0.154905.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
