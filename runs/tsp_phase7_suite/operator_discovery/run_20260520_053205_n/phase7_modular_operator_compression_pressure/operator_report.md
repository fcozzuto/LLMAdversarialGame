# Operator Discovery Report: restart_controller_stagnation_escape_balanced

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically trigger small, bounded-restart growth under stagnation and enable perturbation-based restarts to escape 2-opt traps without excessive randomization across instance classes.
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
- Fingerprint: `a0d77e9aa0626d3a`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Runtime inflation is high at `0.707399`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `220.714771`, distance-eval delta `5781.714286`.
- `cheapest_insertion_2opt` gap delta `-0.002859`, runtime delta `1023.507586`, distance-eval delta `4670.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-185.635371`, distance-eval delta `-11541.714286`.
- `sparse_three_opt` gap delta `0.034327`, runtime delta `24.968514`, distance-eval delta `-7.857143`.
- `clustered_local_search` gap delta `-0.003587`, runtime delta `-112.344529`, distance-eval delta `-6283.142857`.

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
- Runtime inflation: 0.707399.
- Distance-evaluation inflation: 0.770256.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
