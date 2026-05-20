# Operator Discovery Report: restart_controller_stagnation_restart_perturb

- Operator type: `restart_controller`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic restart growth tuned for transfer: triggers restarts on short stagnation, increases restart count gradually, and always applies the configured perturbation on restart to escape nearest-neighbor traps withou
- Novelty classification: `adaptive_restart_controller`.
- Rediscovery signature: `restart_controller:2:9:1`.
- Surviving candidate: `False`.
- Problem class where it helps: `clustered_tsp, two_cluster_bottleneck_tsp`.

## Pseudocode
- Start from a conservative restart budget.
- Increase restart count only after the configured stagnation trigger.
- Keep perturbation restarts bounded by a deterministic maximum.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `6d23e789fdcd92f4`.

## Why It Should Help
- The operator changes restart pressure under stagnation, which is a compact way to regulate exploration without rewriting search internals.

## Failure Cases
- Does not transplant cleanly into `sparse_three_opt`.
- Does not transplant cleanly into `clustered_local_search`.
- Runtime inflation is high at `0.770705`.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.0`, runtime delta `219.517629`, distance-eval delta `5819.428571`.
- `cheapest_insertion_2opt` gap delta `-0.000426`, runtime delta `890.979586`, distance-eval delta `4118.285714`.
- `random_restart_2opt` gap delta `0.0`, runtime delta `-197.947543`, distance-eval delta `-11440.0`.
- `sparse_three_opt` gap delta `0.036727`, runtime delta `6.196343`, distance-eval delta `60.714286`.
- `clustered_local_search` gap delta `0.014715`, runtime delta `-69.483086`, distance-eval delta `-6635.142857`.

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
- Runtime inflation: 0.770705.
- Distance-evaluation inflation: 0.84967.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `0.002615`.
- `fixed_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
- `wider_restart_budget` mean gap `0.118702` and delta vs full operator `0.0`.
