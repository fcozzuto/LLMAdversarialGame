# Operator Discovery Report: restart_controller_bounded_escape_escalate

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth with perturbation-based escapes under stagnation; tuned to balance transfer across clustered/grid/bottleneck structures without excessive restarts.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:7:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `b545101a609f05b0`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `0.992123`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `167.051057`, distance-eval delta `4922.857143`.
- `cheapest_insertion_2opt` gap delta `-0.000698`, runtime delta `1160.241771`, distance-eval delta `4094.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-224.611943`, distance-eval delta `-13097.142857`.
- `sparse_three_opt` gap delta `0.034939`, runtime delta `-3.321357`, distance-eval delta `-265.0`.
- `clustered_local_search` gap delta `-0.003871`, runtime delta `-165.249871`, distance-eval delta `-8255.142857`.

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
- Runtime inflation: 0.992123.
- Distance-evaluation inflation: 0.928037.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
