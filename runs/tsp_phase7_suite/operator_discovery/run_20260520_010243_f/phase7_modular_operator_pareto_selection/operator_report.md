# Operator Discovery Report: rank_candidates_mix_geo_bottleneck

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic local-search candidate move ranker that biases toward 2-opt edge crossings and long-edge fixes while reducing traps; tuned to transfer across bottleneck/two-cluster and mixed EUC-2D instances.
- Novelty classification: `delta_weighted_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.250,cross=1.000,span=0.200,trap=0.600`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `44c99bc352a57fe0`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.003328`, runtime delta `65.805843`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1310.816529`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `4.460471`, distance-eval delta `-140.571429`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `2.689386`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `-0.001068`, runtime delta `85.351986`, distance-eval delta `2054.857143`.

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
- Runtime inflation: 0.014599.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006956`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.001206`.
- `shuffled_ranker` mean gap `0.128189` and delta vs full operator `-8.4e-05`.
