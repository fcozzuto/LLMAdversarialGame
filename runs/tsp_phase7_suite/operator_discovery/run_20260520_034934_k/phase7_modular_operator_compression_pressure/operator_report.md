# Operator Discovery Report: scaffold_selector_transfer_focus

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Selects a baseline TSP scaffold using instance descriptors: emphasize two-cluster bottlenecks and nearest-neighbor traps, then fall back to nearest-neighbor 2-opt. Helps held-out transfer without changing local-search in
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:clustered_local_search`.
- Surviving candidate: `False`.
- Problem class where it helps: `grid_like_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `b7e4049e968c67d3`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `heldout_tsplib` with gap delta 0.019828.
- Underperforms on `elongated_corridor_tsp` with gap delta 0.034174.
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.034212.
- Underperforms on `two_cluster_bottleneck_tsp` with gap delta 0.022965.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `sparse_three_opt`.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.682188`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.017077`, runtime delta `201.277643`, distance-eval delta `10421.285714`.
- `cheapest_insertion_2opt` gap delta `0.124398`, runtime delta `-4254.496743`, distance-eval delta `-6750636.714286`.
- `random_restart_2opt` gap delta `0.037402`, runtime delta `-100.886729`, distance-eval delta `-4254.0`.
- `sparse_three_opt` gap delta `0.018362`, runtime delta `216.8182`, distance-eval delta `7000.0`.
- `clustered_local_search` gap delta `-0.007256`, runtime delta `15.7217`, distance-eval delta `-4532.714286`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.254886` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.113212` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.037378` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.082744` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.034212` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.132022` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.017888.
- Runtime inflation: 0.682188.
- Distance-evaluation inflation: 1.485397.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.0182`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `-0.0182`.
- `shuffled_selector` mean gap `0.108754` and delta vs full operator `-0.030763`.
