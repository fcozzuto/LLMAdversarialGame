# Operator Discovery Report: candidate_pruner_transfer_grid_cluster_stagnation_adaptive

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic adaptive candidate-list pruning: keeps a moderate base list, slightly expands when stagnation is likely, and biases against trap/cluster-heavy moves while preserving diversity for grid/two-cluster bottlenec
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:22:-3:4:5`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `83e0cc78cf279346`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.344792`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `138.832271`, distance-eval delta `2264.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `292.405286`, distance-eval delta `1187.428571`.
- `random_restart_2opt` gap delta `0.001067`, runtime delta `27.342486`, distance-eval delta `3035.428571`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `53.332786`, distance-eval delta `4249.857143`.
- `clustered_local_search` gap delta `0.007254`, runtime delta `212.092043`, distance-eval delta `8807.714286`.

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
- Runtime inflation: 0.344792.
- Distance-evaluation inflation: 0.234827.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
