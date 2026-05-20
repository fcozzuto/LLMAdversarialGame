# Operator Discovery Report: bottleneck_focused_restart_controller_transfer

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Grows restart count deterministically under stagnation, with perturbation enabled, to escape NN/2opt plateaus especially on bottleneck-like Euclidean instances while keeping restart budget bounded.
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `f035bd3020f23df1`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `1.083761`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `20.662657`, distance-eval delta `4494.285714`.
- `cheapest_insertion_2opt` gap delta `-0.002814`, runtime delta `-549.042357`, distance-eval delta `4222.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-217.897357`, distance-eval delta `-12294.857143`.
- `sparse_three_opt` gap delta `0.035007`, runtime delta `13.474529`, distance-eval delta `-471.285714`.
- `clustered_local_search` gap delta `-0.000156`, runtime delta `-98.421843`, distance-eval delta `-6839.142857`.

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
- Runtime inflation: 1.083761.
- Distance-evaluation inflation: 0.954353.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
