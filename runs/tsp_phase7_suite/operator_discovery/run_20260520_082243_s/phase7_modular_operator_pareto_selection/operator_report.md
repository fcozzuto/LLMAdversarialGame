# Operator Discovery Report: det_double_bridge_then_segment_reversal_escape

- Operator type: `perturbation`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic stagnation escape: apply a strong double-bridge perturbation first, then escalate to a structured segment reversal and occasional window shuffle, tuned to help escape two-cluster bottlenecks and nearest-nei
- Novelty classification: `stagnation_escalator`.
- Rediscovery signature: `perturbation:double_bridge:segment_reversal:4:3`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Track stagnation count during local search and restarts.
- Use `double_bridge` by default and escalate toward `segment_reversal` after the stagnation threshold.
- Increase perturbation strength deterministically when escape pressure rises.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `976fef93ad14cb16`.

## Why It Should Help
- The operator targets local-minimum escape directly by controlling when and how restarts are perturbed.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `56.2351`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `365.134986`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-37.980257`, distance-eval delta `-618.857143`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `-0.182471`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.015362`, runtime delta `-22.454986`, distance-eval delta `-1715.428571`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.0.
- Runtime inflation: -0.005965.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `True`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `simplified_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
- `alternate_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
