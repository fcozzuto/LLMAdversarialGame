# Operator Discovery Report: transfer_scaffold_mix_bottleneck_cluster_grid_safe

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic scaffold choice using instance descriptors: prefer nearest-neighbor 2-opt for clustered/high transfer stability; prefer cheapest-insertion 2-opt for two-cluster bottlenecks; prefer random-restart 2-opt for 
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:nearest_neighbor_2opt:random_restart_2opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `heldout_tsplib, clustered_tsp, grid_like_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `2e318d0281e149da`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.3987.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `25.028343`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.068763`, runtime delta `3994.265471`, distance-eval delta `6276598.714286`.
- `cheapest_insertion_2opt` gap delta `0.038559`, runtime delta `547.690871`, distance-eval delta `-484459.285714`.
- `random_restart_2opt` gap delta `-0.048437`, runtime delta `3806.556314`, distance-eval delta `6262764.571429`.
- `sparse_three_opt` gap delta `-0.067477`, runtime delta `3971.568986`, distance-eval delta `6273177.428571`.
- `clustered_local_search` gap delta `-0.090286`, runtime delta `3781.584557`, distance-eval delta `6261929.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.166295` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.0` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.006647` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.095808` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.3987` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.001685` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.003539.
- Runtime inflation: 25.028343.
- Distance-evaluation inflation: 638.855145.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003539`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `0.003539`.
- `shuffled_selector` mean gap `0.116775` and delta vs full operator `-0.001003`.
