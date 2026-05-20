# Operator Discovery Report: context_scaffold_selector_bottleneck_cluster

- Operator type: `scaffold_selector`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Selects the best baseline TSP scaffold based on instance structure descriptors (two-cluster bottlenecks, clustered layouts, and nearest-neighbor trap likelihood), with a safe fallback for mixed/unrecognized cases.
- Novelty classification: `descriptor_based_scaffold_selector`.
- Rediscovery signature: `scaffold_selector:random_restart_2opt:clustered_local_search:cheapest_insertion_2opt`.
- Surviving candidate: `False`.
- Problem class where it helps: `heldout_tsplib, grid_like_tsp`.

## Pseudocode
- Read instance descriptors to classify the layout family.
- Dispatch the instance to the preferred scaffold for that structure class.
- Fall back to a safe default scaffold when the structure is ambiguous.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `0e540a9ff56601e2`.

## Why It Should Help
- The operator selects among simple solvers from instance descriptors, so any gain should come from a reusable structure-to-scaffold mapping.

## Failure Cases
- Underperforms on `uniform_euclidean` with gap delta 0.013605.
- Does not transplant cleanly into `cheapest_insertion_2opt`.
- Runtime inflation is high at `1.366747`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `-0.035015`, runtime delta `337.469929`, distance-eval delta `255705.857143`.
- `cheapest_insertion_2opt` gap delta `0.072307`, runtime delta `-3816.784171`, distance-eval delta `-6505352.142857`.
- `random_restart_2opt` gap delta `-0.014689`, runtime delta `135.615186`, distance-eval delta `241848.285714`.
- `sparse_three_opt` gap delta `-0.033729`, runtime delta `325.875286`, distance-eval delta `252284.571429`.
- `clustered_local_search` gap delta `-0.051939`, runtime delta `186.963329`, distance-eval delta `242675.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.200044` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.113212` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.082744` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.013605` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.013741.
- Runtime inflation: 1.366747.
- Distance-evaluation inflation: 26.433505.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.013741`.
- `flattened_selector` mean gap `0.121317` and delta vs full operator `0.013741`.
- `shuffled_selector` mean gap `0.098866` and delta vs full operator `-0.00871`.
