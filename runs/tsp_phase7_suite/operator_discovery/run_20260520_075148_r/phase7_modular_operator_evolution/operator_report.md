# Operator Discovery Report: det_restart_controller_stagnation_growth_transfer_robust

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart scheduling for 2-opt plateaus: when no improvement for a short stagnation window, increase restart count with mild growth and recycle a small deterministic seed pool; uses perturbation-based restart
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `f7a938a8139cd42e`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.938393`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `202.532586`, distance-eval delta `4237.142857`.
- `cheapest_insertion_2opt` gap delta `-0.002747`, runtime delta `236.1959`, distance-eval delta `4286.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-213.850871`, distance-eval delta `-12306.285714`.
- `sparse_three_opt` gap delta `0.038157`, runtime delta `7.365914`, distance-eval delta `244.714286`.
- `clustered_local_search` gap delta `0.005232`, runtime delta `-66.6011`, distance-eval delta `-5112.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235058` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.083393` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.084632` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: -0.002615.
- Runtime inflation: 0.938393.
- Distance-evaluation inflation: 0.881272.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
