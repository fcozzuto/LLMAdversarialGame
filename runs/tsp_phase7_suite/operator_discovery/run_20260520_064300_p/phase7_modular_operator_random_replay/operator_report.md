# Operator Discovery Report: descriptor_aware_scaffold_selector

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Choose the most transfer-robust baseline based on instance structure descriptors (two-cluster bottlenecks, grid-likeness, elongated spreads, and nearest-neighbor trap tendency), with a safe fallback to nearest_neighbor_2
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:clustered_local_search`.
- Surviving candidate: `False`.
- Problem class where it helps: `heldout_tsplib, two_cluster_bottleneck_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `1d19d0cb1e42320b`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.170114.
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.034212.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `1.105281`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.059449`, runtime delta `274.928857`, distance-eval delta `112789.0`.
- `cheapest_insertion_2opt` gap delta `0.047873`, runtime delta `-4660.927757`, distance-eval delta `-6648269.0`.
- `random_restart_2opt` gap delta `-0.039123`, runtime delta `143.455186`, distance-eval delta `98603.428571`.
- `sparse_three_opt` gap delta `-0.058163`, runtime delta `331.502629`, distance-eval delta `109367.714286`.
- `clustered_local_search` gap delta `-0.073402`, runtime delta `159.034029`, distance-eval delta `98934.428571`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.17836` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.113212` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.006647` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.27681` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.034212` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.001685` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.014035.
- Runtime inflation: 1.105281.
- Distance-evaluation inflation: 11.887779.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.013723`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `0.013723`.
- `shuffled_selector` mean gap `0.075559` and delta vs full operator `-0.032035`.
