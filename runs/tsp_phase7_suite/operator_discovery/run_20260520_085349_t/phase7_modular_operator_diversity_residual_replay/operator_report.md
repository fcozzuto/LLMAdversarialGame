# Operator Discovery Report: scaffold_selector_transfer_default

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Select a baseline TSP scaffold based on coarse instance structure descriptors to improve held-out transfer (bottlenecks/clusters/grids/traps/elongation).
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:cheapest_insertion_2opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `heldout_tsplib, clustered_tsp, grid_like_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `b389b05ffb598dee`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `2.246598`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.024827`, runtime delta `362.854686`, distance-eval delta `255757.571429`.
- `cheapest_insertion_2opt` gap delta `0.082494`, runtime delta `-3187.541014`, distance-eval delta `-6505300.428571`.
- `random_restart_2opt` gap delta `-0.004502`, runtime delta `142.802614`, distance-eval delta `239939.428571`.
- `sparse_three_opt` gap delta `-0.023542`, runtime delta `358.383771`, distance-eval delta `252336.285714`.
- `clustered_local_search` gap delta `-0.044792`, runtime delta `148.947114`, distance-eval delta `240221.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.210231` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.038868` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.082744` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.01625.
- Runtime inflation: 2.246598.
- Distance-evaluation inflation: 26.784097.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.016073`.
- `flattened_selector` mean gap `0.153424` and delta vs full operator `0.04818`.
- `shuffled_selector` mean gap `0.095997` and delta vs full operator `-0.009247`.
