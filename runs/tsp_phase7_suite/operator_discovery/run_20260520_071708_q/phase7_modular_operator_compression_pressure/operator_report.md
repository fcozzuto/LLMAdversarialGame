# Operator Discovery Report: descriptor_driven_restart_controller_stagnation_escape

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Triggers deterministic restarts on short stagnation and grows restart budget cautiously, using perturbation at each restart to escape nearest-neighbor / 2-opt traps without excessive diversification.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:6:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `586d7fcf0845f2b3`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.911918`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `89.435386`, distance-eval delta `3270.285714`.
- `cheapest_insertion_2opt` gap delta `-0.000585`, runtime delta `1949.318443`, distance-eval delta `4254.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-235.805214`, distance-eval delta `-13437.714286`.
- `sparse_three_opt` gap delta `0.036385`, runtime delta `4.635029`, distance-eval delta `-65.0`.
- `clustered_local_search` gap delta `0.003398`, runtime delta `-29.1608`, distance-eval delta `-4644.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110431` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.003304.
- Runtime inflation: 0.911918.
- Distance-evaluation inflation: 0.929896.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
