# Operator Discovery Report: epoch6_restart_controller_stagnation_doubling_with_perturb

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart controller: trigger restarts after short stagnation; grow restart budget quickly but cap total restarts; when restarting, enable the scaffold’s perturbation phase to reintroduce new edge structure d
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:8:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `685eb7e124ec47dd`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.719721`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `182.772871`, distance-eval delta `5589.714286`.
- `cheapest_insertion_2opt` gap delta `-0.002519`, runtime delta `984.9885`, distance-eval delta `4046.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-201.144971`, distance-eval delta `-11662.857143`.
- `sparse_three_opt` gap delta `0.037557`, runtime delta `-0.072129`, distance-eval delta `-75.857143`.
- `clustered_local_search` gap delta `0.019276`, runtime delta `-152.8635`, distance-eval delta `-8119.142857`.

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
- Runtime inflation: 0.719721.
- Distance-evaluation inflation: 0.844848.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
