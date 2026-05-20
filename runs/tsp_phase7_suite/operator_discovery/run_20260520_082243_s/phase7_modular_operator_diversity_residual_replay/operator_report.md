# Operator Discovery Report: transfer_pruner_adapt_to_structure_moderate_base

- Operator type: `candidate_pruner`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Candidate pruner that keeps a mid-sized neighborhood by default, then adaptively expands/contract based on structural cues (clusteredness, grid-likeness, and stagnation) to improve cross-instance transfer while limiting 
- Novelty classification: `descriptor_adaptive_pruner`.
- Rediscovery signature: `candidate_pruner:16:3:2:2`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- Start from a base candidate-list size.
- Expand or shrink the list using instance descriptors such as size, trap score, grid-likeness, clustering, and current stagnation.
- Run the downstream local search only on the resulting pruned neighborhood.

## Complexity
- Non-empty lines: 12.
- Complexity score: 0.44.
- Fingerprint: `be9aa4335e7f560a`.

## Why It Should Help
- The operator adapts neighborhood size to instance structure, which can trade off search breadth and runtime in a reusable way.

## Failure Cases
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.000813`, runtime delta `-175.102914`, distance-eval delta `22.0`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `357.399414`, distance-eval delta `212.0`.
- `random_restart_2opt` gap delta `-0.000421`, runtime delta `-47.935257`, distance-eval delta `-1567.571429`.
- `sparse_three_opt` gap delta `0.000379`, runtime delta `17.557686`, distance-eval delta `1793.857143`.
- `clustered_local_search` gap delta `0.026377`, runtime delta `-33.575114`, distance-eval delta `-931.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.235871` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.106696` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.000299.
- Runtime inflation: -0.035494.
- Distance-evaluation inflation: 0.006899.
- Same-gap-faster flag: `True`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.000299`.
- `constant_pruner` mean gap `0.125772` and delta vs full operator `0.004155`.
- `wide_pruner` mean gap `0.121542` and delta vs full operator `-7.5e-05`.
