# Operator Discovery Report: candidate_ranker_bottleneck_grid_aware_reorder

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic local candidate re-ranking emphasizing cross-edge fixes and trap avoidance, with mild penalties for NN-like misleading moves and slight boosts for longer edges to escape grid/two-cluster bottlenecks.
- Novelty classification: `trap_aware_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.250,cross=1.250,span=0.400,trap=1.000`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `34a0dc53b8ab7294`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.001527`, runtime delta `42.846286`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1241.663014`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `7.105243`, distance-eval delta `313.142857`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `4.491214`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.004435`, runtime delta `-23.690486`, distance-eval delta `433.714286`.

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
- Runtime inflation: 0.006216.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006293`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.000543`.
- `shuffled_ranker` mean gap `0.12759` and delta vs full operator `-2e-05`.
