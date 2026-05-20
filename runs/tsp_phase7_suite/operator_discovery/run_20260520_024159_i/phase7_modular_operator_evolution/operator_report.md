# Operator Discovery Report: det_double_bridge_escape_schedule

- Operator type: `perturbation`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic perturbation escalation to escape 2-opt stagnation: starts with double-bridge, then alternates segment reversal and double-bridge with increased strength while stagnation persists, using a fixed attempt bud
- Novelty classification: `stagnation_escalator`.
- Rediscovery signature: `perturbation:double_bridge:segment_reversal:2:3`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Track stagnation count during local search and restarts.
- Use `double_bridge` by default and escalate toward `segment_reversal` after the stagnation threshold.
- Increase perturbation strength deterministically when escape pressure rises.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `77ae2dcd3a93b88a`.

## Why It Should Help
- The operator targets local-minimum escape directly by controlling when and how restarts are perturbed.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `76.452657`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1424.1333`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `67.571814`, distance-eval delta `-2152.0`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `0.561757`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.014118`, runtime delta `-22.091214`, distance-eval delta `-692.0`.

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
- Runtime inflation: 0.016003.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `simplified_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
- `alternate_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
