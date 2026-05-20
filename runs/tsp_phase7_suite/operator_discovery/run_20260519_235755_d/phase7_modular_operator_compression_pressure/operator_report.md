# Operator Discovery Report: transfer_candidate_pruner_balanced_trap_grid

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Adapt local-search candidate list size using instance descriptors: slightly tighter pruning for trap/grid-like layouts, and looser pruning for clustered/low-structure cases to preserve diverse 2-opt exchanges.
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:20:3:2:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `60051f82f1240626`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.263013`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000609`, runtime delta `94.657286`, distance-eval delta `1766.714286`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1350.4012`, distance-eval delta `1005.142857`.
- `random_restart_2opt` gap delta `0.001067`, runtime delta `55.042186`, distance-eval delta `3698.571429`.
- `sparse_three_opt` gap delta `-0.000253`, runtime delta `38.082243`, distance-eval delta `3821.857143`.
- `clustered_local_search` gap delta `0.019294`, runtime delta `138.498471`, distance-eval delta `6739.0`.

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
- Runtime inflation: 0.263013.
- Distance-evaluation inflation: 0.184271.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000224`.
- `constant_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `0.0`.
