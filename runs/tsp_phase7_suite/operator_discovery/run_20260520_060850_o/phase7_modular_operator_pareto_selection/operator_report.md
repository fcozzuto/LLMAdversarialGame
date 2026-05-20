# Operator Discovery Report: pruner_cluster_bottleneck_adaptive

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Adaptive candidate-list pruner tuned to keep more 2-opt candidates on bottleneck/two-cluster instances while reducing noise on easy/unstructured ones.
- Novelty classification: `trap_expanding_pruner`.
- Rediscovery signature: `candidate_pruner:20:6:2:3`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `b8ea304ff7122a53`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.48603`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `93.5186`, distance-eval delta `3467.428571`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1846.092786`, distance-eval delta `1854.285714`.
- `random_restart_2opt` gap delta `0.000974`, runtime delta `114.519114`, distance-eval delta `7917.142857`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `77.996629`, distance-eval delta `5799.857143`.
- `clustered_local_search` gap delta `0.047699`, runtime delta `80.014186`, distance-eval delta `6013.0`.

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
- Runtime inflation: 0.48603.
- Distance-evaluation inflation: 0.357171.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
