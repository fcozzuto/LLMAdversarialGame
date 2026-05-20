# Operator Discovery Report: euclid_transfer_ranker_bottleneck_balanced_2opt

- Operator type: `candidate_ranker`.
- Host scaffold: `nearest_neighbor_2opt`.
- Core idea: Deterministic 2-opt candidate ranking that prioritizes bottleneck-escaping crossings while still favoring short-span improvements for Euclidean transfer (two-cluster bottlenecks + mixed).
- Novelty classification: `trap_aware_ranker`.
- Rediscovery signature: `candidate_ranker:delta=1.000,cross=0.750,span=0.200,trap=0.600`.
- Surviving candidate: `False`.
- Problem class where it helps: `none confirmed`.

## Pseudocode
- For each candidate move, compute a composite score from immediate delta, crossing removal, span, trap awareness, and local structure.
- Sort candidate moves by ascending composite score.
- Apply the first move that yields a genuine tour improvement.

## Complexity
- Non-empty lines: 13.
- Complexity score: 0.46.
- Fingerprint: `c91b7a126144c5eb`.

## Why It Should Help
- The operator changes which local-search moves are tried first, so it can improve search efficiency without rewriting the underlying solver.

## Failure Cases
- Underperforms on `grid_like_tsp` with gap delta 0.054436.
- Does not transplant cleanly into `nearest_neighbor_2opt`.
- Does not transplant cleanly into `random_restart_2opt`.
- Does not transplant cleanly into `clustered_local_search`.
- No validation family shows a clear improvement over the host baseline.
- Disabling the operator does not hurt, so the ablation does not support a real operator effect.

## Transplant Results
- `nearest_neighbor_2opt` gap delta `0.003328`, runtime delta `74.841171`, distance-eval delta `-100.571429`.
- `cheapest_insertion_2opt` gap delta `0.0`, runtime delta `1270.565557`, distance-eval delta `0.0`.
- `random_restart_2opt` gap delta `0.006029`, runtime delta `8.929957`, distance-eval delta `881.142857`.
- `sparse_three_opt` gap delta `0.0`, runtime delta `0.499729`, distance-eval delta `0.0`.
- `clustered_local_search` gap delta `0.005731`, runtime delta `62.426043`, distance-eval delta `2764.571429`.

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
- Runtime inflation: 0.015857.
- Distance-evaluation inflation: 0.003718.
- Same-gap-faster flag: `False`.
- Better-gap-same-runtime flag: `False`.

## Ablation Results
- `disabled` mean gap `0.121317` and delta vs full operator `-0.006956`.
- `simplified_delta_ranker` mean gap `0.127067` and delta vs full operator `-0.001206`.
- `shuffled_ranker` mean gap `0.128189` and delta vs full operator `-8.4e-05`.
