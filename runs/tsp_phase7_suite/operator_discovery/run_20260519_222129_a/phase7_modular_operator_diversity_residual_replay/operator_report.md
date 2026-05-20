# Operator Discovery Report: scaffold_selector_structure_aware

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically select a best-fit baseline scaffold from instance descriptors (two-cluster bottleneck, clustered/grid/elongated, and nearest-neighbor trap), otherwise fall back to nearest_neighbor_2opt.
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:sparse_three_opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `heldout_tsplib, clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `b694c0a51632de6b`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.170114.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `1.442123`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.057811`, runtime delta `335.973914`, distance-eval delta `109924.428571`.
- `cheapest_insertion_2opt` gap delta `0.049511`, runtime delta `-3708.730271`, distance-eval delta `-6651133.571429`.
- `random_restart_2opt` gap delta `-0.037485`, runtime delta `103.263586`, distance-eval delta `94655.428571`.
- `sparse_three_opt` gap delta `-0.056525`, runtime delta `327.453757`, distance-eval delta `106503.142857`.
- `clustered_local_search` gap delta `-0.0842`, runtime delta `178.8486`, distance-eval delta `97304.142857`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.176732` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.038868` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.006647` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.27681` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.001685` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.019489.
- Runtime inflation: 1.442123.
- Distance-evaluation inflation: 11.648842.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.019114`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `0.019114`.
- `shuffled_selector` mean gap `0.073227` and delta vs full operator `-0.028976`.
