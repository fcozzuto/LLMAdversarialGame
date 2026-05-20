# Operator Discovery Report: scaffold_selector_transfer_focus

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Select a compact baseline scaffold per instance structure to improve held-out transfer, emphasizing robustness on bottleneck/two-cluster shapes and clustered Euclidean instances; otherwise fall back to nearest_neighbor_2
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:random_restart_2opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, grid_like_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `d2256b0bb0be1564`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `heldout_tsplib` with gap delta 0.01955.
- Underperforms on `elongated_corridor_tsp` with gap delta 0.034174.
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.3987.
- Underperforms on `two_cluster_bottleneck_tsp` with gap delta 0.022965.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `sparse_three_opt`.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `1.679113`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.02022`, runtime delta `321.779129`, distance-eval delta `11882.714286`.
- `cheapest_insertion_2opt` gap delta `0.127541`, runtime delta `-4654.465843`, distance-eval delta `-6749175.285714`.
- `random_restart_2opt` gap delta `0.040545`, runtime delta `140.9561`, distance-eval delta `-5278.285714`.
- `sparse_three_opt` gap delta `0.021505`, runtime delta `382.081543`, distance-eval delta `8461.428571`.
- `clustered_local_search` gap delta `0.00245`, runtime delta `215.5765`, distance-eval delta `-2549.0`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.254608` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.053865` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.037378` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.082744` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.3987` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.132022` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.042667.
- Runtime inflation: 1.679113.
- Distance-evaluation inflation: 2.049916.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.043048`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `-0.043048`.
- `shuffled_selector` mean gap `0.100777` and delta vs full operator `-0.063588`.
