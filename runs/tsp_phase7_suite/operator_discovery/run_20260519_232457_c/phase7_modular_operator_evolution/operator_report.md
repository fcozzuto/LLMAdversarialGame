# Operator Discovery Report: candidate_pruner_transfer_balanced

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically prunes local-search candidates to improve cross-instance transfer: keep a moderate candidate pool, favor candidates likely to help in clustered/trap-like instances, and slightly shrink under stagnation.
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:18:2:-1:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `7db32329cb38351d`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `91.516371`, distance-eval delta `1427.857143`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1585.135457`, distance-eval delta `913.714286`.
- `random_restart_2opt` gap delta `0.001067`, runtime delta `90.062986`, distance-eval delta `4285.571429`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `35.876814`, distance-eval delta `3481.571429`.
- `clustered_local_search` gap delta `0.023118`, runtime delta `143.509`, distance-eval delta `6533.0`.

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
- Runtime inflation: 0.172081.
- Distance-evaluation inflation: 0.149822.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
