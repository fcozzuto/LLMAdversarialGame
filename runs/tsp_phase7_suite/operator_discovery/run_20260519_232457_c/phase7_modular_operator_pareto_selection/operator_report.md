# Operator Discovery Report: rank_2opt_candidates_cluster_span_balanced

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic candidate ranker for 2-opt style local moves: prioritizes moves that reduce estimated crossings/long edges while rewarding productive span and mild cluster alignment; includes trap and nearest-neighbor pena
- Novelty classification: `trap_aware_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.250,cross=1.000,span=0.400,trap=0.600`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `fe95dee0aba78001`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.003328`, runtime delta `41.119457`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1476.261843`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `38.963829`, distance-eval delta `769.714286`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `2.402457`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `-0.002014`, runtime delta `31.334871`, distance-eval delta `1922.285714`.

## Instance-Family Results
- `heldout_tsplib` operator gap `0.238386` vs baseline `0.235058`.
- `clustered_tsp` operator gap `0.110853` vs baseline `0.110853`.
- `elongated_corridor_tsp` operator gap `0.003204` vs baseline `0.003204`.
- `grid_like_tsp` operator gap `0.161132` vs baseline `0.106696`.
- `nearest_neighbor_trap_tsp` operator gap `0.0` vs baseline `0.0`.
- `two_cluster_bottleneck_tsp` operator gap `0.109057` vs baseline `0.109057`.
- `uniform_euclidean` operator gap `0.0` vs baseline `0.0`.

## Pareto Results
- Gap delta: 0.006956.
- Runtime inflation: 0.095546.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006956`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.001206`.
- `shuffled_ranker` mean gap `0.128189` and delta vs full operator `-8.4e-05`.
