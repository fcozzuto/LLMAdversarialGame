# Operator Discovery Report: scaffold_selector_transfer_fallback

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Select a simple baseline scaffold deterministically from instance-descriptor structure to improve cross-instance transfer; uses nearest_neighbor_2opt as fallback when descriptors are uninformative.
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
- Fingerprint: `2eaf77a86c4666a9`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `heldout_tsplib` with gap delta 0.009631.
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.068425.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `sparse_three_opt`.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `0.894435`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.003494`, runtime delta `198.5123`, distance-eval delta `8994.142857`.
- `cheapest_insertion_2opt` gap delta `0.110815`, runtime delta `-4234.790657`, distance-eval delta `-6752063.857143`.
- `random_restart_2opt` gap delta `0.02382`, runtime delta `47.410457`, distance-eval delta `-6708.0`.
- `sparse_three_opt` gap delta `0.00478`, runtime delta `261.361257`, distance-eval delta `5572.857143`.
- `clustered_local_search` gap delta `-0.02085`, runtime delta `81.133671`, distance-eval delta `-4963.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.244689` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.113212` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.082744` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.068425` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.004671.
- Runtime inflation: 0.894435.
- Distance-evaluation inflation: 1.541079.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.005919`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `-0.005919`.
- `shuffled_selector` mean gap `0.098866` and delta vs full operator `-0.02837`.
