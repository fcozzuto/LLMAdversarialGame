# Operator Discovery Report: descriptor_scaffold_selector_v1

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Choose a simple baseline scaffold deterministically from instance descriptors, prioritizing bottleneck and trap-aware heuristics, with a robust fallback for mixed/unknown structure.
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:random_restart_2opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `b8844c7280347b68`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `heldout_tsplib` with gap delta 0.005953.
- Underperforms on `elongated_corridor_tsp` with gap delta 0.034174.
- Underperforms on `grid_like_tsp` with gap delta 0.170114.
- Underperforms on `nearest_neighbor_trap_tsp` with gap delta 0.3987.
- Underperforms on `two_cluster_bottleneck_tsp` with gap delta 0.022965.
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `sparse_three_opt`.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.
- Runtime inflation is high at `24.116978`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.005953`, runtime delta `3562.927486`, distance-eval delta `6175991.0`.
- `cheapest_insertion_2opt` gap delta `0.113275`, runtime delta `123.355086`, distance-eval delta `-585067.0`.
- `random_restart_2opt` gap delta `0.026279`, runtime delta `3334.782043`, distance-eval delta `6161039.714286`.
- `sparse_three_opt` gap delta `0.007239`, runtime delta `3542.660543`, distance-eval delta `6172569.714286`.
- `clustered_local_search` gap delta `-0.014371`, runtime delta `3448.417014`, distance-eval delta `6164819.571429`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.241011` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.0` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.037378` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.27681` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.3987` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.132022` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.057846.
- Runtime inflation: 24.116978.
- Distance-evaluation inflation: 628.593581.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.057846`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `-0.057846`.
- `shuffled_selector` mean gap `0.106492` and delta vs full operator `-0.072672`.
