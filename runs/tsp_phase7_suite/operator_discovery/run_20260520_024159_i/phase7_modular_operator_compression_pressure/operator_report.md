# Operator Discovery Report: select_transfer_scaffold_by_structure

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically picks a TSP baseline scaffold based on instance structure descriptors (bottleneck/cluster/grid/elongation) to improve transfer while keeping local 2-opt style behavior consistent.
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
- Fingerprint: `e04c01207bedeb3a`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.034212.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `0.981692`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.059029`, runtime delta `291.734943`, distance-eval delta `110250.142857`.
- `cheapest_insertion_2opt` gap delta `0.048293`, runtime delta `-4282.379157`, distance-eval delta `-6650807.857143`.
- `random_restart_2opt` gap delta `-0.038703`, runtime delta `40.549529`, distance-eval delta `94468.571429`.
- `sparse_three_opt` gap delta `-0.057743`, runtime delta `315.845714`, distance-eval delta `106828.857143`.
- `clustered_local_search` gap delta `-0.086334`, runtime delta `114.2281`, distance-eval delta `95342.428571`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.182167` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.113212` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.006647` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.034212` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.001685` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.02318.
- Runtime inflation: 0.981692.
- Distance-evaluation inflation: 11.735255.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.021933`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `0.021933`.
- `shuffled_selector` mean gap `0.081893` and delta vs full operator `-0.017491`.
