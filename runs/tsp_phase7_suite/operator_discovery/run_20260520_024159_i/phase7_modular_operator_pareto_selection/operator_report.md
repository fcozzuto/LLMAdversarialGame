# Operator Discovery Report: candidate_ranker_transfer_crossing_span_balanced

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministically re-ranks local-search moves by emphasizing 2-opt crossings and span reduction, while lightly penalizing nearest-neighbor trap moves to improve transfer across clustered, grid-like, and bottleneck instan
- Novelty classification: `delta_weighted_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.000,cross=1.000,span=0.400,trap=0.200`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `86056cf953d289b7`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.001527`, runtime delta `88.226114`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `688.245086`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `-45.924557`, distance-eval delta `-2292.571429`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `4.833871`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.007422`, runtime delta `13.279543`, distance-eval delta `1542.285714`.

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
- Runtime inflation: 0.019176.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006293`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.000543`.
- `shuffled_ranker` mean gap `0.121771` and delta vs full operator `-0.005839`.
