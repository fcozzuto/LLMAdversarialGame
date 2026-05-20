# Operator Discovery Report: perturb_escape_double_bridge_then_segment_reversal

- Operator type: `perturbation`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic stagnation escape that applies a strong, structured perturbation early (double-bridge), escalates to larger disruptive reversals on repeated stagnation, and falls back to a windowed shuffle when needed; des
- Novelty classification: `stagnation_escalator`.
- Rediscovery signature: `perturbation:double_bridge:segment_reversal:3:3`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Track stagnation count during local search and restarts.
- Use `double_bridge` by default and escalate toward `segment_reversal` after the stagnation threshold.
- Increase perturbation strength deterministically when escape pressure rises.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `c2156b9793596466`.

## Why It Should Help
- The operator targets local-minimum escape directly by controlling when and how restarts are perturbed.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `1.810343`, distance-eval delta `0.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `431.957457`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-43.607829`, distance-eval delta `-2421.714286`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `2.393043`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.015278`, runtime delta `-36.173143`, distance-eval delta `-1389.142857`.

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
- Runtime inflation: 0.007338.
- Distance-evaluation inflation: 0.0.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.0`.
- `simplified_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
- `alternate_perturbation` mean gap `0.121317` and delta vs full operator `0.0`.
