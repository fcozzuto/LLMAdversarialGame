# Operator Discovery Report: restart_controller_adaptive_escape_bottleneck

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller that triggers additional restarts after short stagnation, with a larger perturbation-driven seed pool to escape two-cluster bottlenecks and grid-like traps while keeping restart growth ca
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:3:7:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `08bac8fd1984f5ef`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `2.055607`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `344.039829`, distance-eval delta `8604.0`.
- `cheapest_insertion_2opt` gap delta `-0.00408`, runtime delta `321.847243`, distance-eval delta `7860.571429`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-171.714286`, distance-eval delta `-9090.285714`.
- `sparse_three_opt` gap delta `0.031858`, runtime delta `83.963757`, distance-eval delta `4854.142857`.
- `clustered_local_search` gap delta `-0.000591`, runtime delta `-16.3867`, distance-eval delta `-412.0`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110431` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.003363.
- Runtime inflation: 2.055607.
- Distance-evaluation inflation: 1.878498.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003363`.
- `fixed_restart_budget` mean gap `0.117954` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000266`.
