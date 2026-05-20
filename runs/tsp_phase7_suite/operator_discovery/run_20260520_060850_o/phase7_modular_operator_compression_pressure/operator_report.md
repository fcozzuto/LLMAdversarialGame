# Operator Discovery Report: restart_controller_two_cluster_safe

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Controls restart growth to reliably escape stagnation on two-cluster/bottleneck and mixed EUC2D cases while keeping restart count moderate for transfer.
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
- Fingerprint: `dd305abde23ea4b7`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `1.104421`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `232.567371`, distance-eval delta `6002.285714`.
- `cheapest_insertion_2opt` gap delta `-0.002839`, runtime delta `1114.224343`, distance-eval delta `4430.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-214.904129`, distance-eval delta `-11710.857143`.
- `sparse_three_opt` gap delta `0.035379`, runtime delta `1.106729`, distance-eval delta `-214.142857`.
- `clustered_local_search` gap delta `0.003264`, runtime delta `-41.680229`, distance-eval delta `-4440.857143`.

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
- Runtime inflation: 1.104421.
- Distance-evaluation inflation: 0.865064.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.003304`.
- `fixed_restart_budget` mean gap `0.118013` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.117688` and delta vs full operator `-0.000325`.
