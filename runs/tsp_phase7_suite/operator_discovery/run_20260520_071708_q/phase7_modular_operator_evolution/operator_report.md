# Operator Discovery Report: candidate_ranker_bottleneck_aware_2opt_moves

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic local ranking for 2opt-like moves: prioritize crossing/long-edge resolutions and cluster-spanning swaps, while penalizing nearest-neighbor trap moves; helps transfer on clustered and bottleneck instances wi
- Novelty classification: `long_span_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.250,cross=1.250,span=0.600,trap=0.400`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `fb9684a7125b5c15`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.001527`, runtime delta `54.157271`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1836.116343`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `-67.111943`, distance-eval delta `-42.285714`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `4.127557`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.009035`, runtime delta `50.913214`, distance-eval delta `-88.571429`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.236585` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.161132` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.006293.
- Runtime inflation: 0.00507.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006293`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.000543`.
- `shuffled_ranker` mean gap `0.121771` and delta vs full operator `-0.005839`.
