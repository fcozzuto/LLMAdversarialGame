# Phase 6 TSP Replay Mechanism Protocol

This document defines the conservative follow-up after the completed phase-5 routing study.

The scientific motivation is narrow and mechanistic:

> On symmetric TSPLIB95 TSP, why did `random_replay` beat `failure_replay`?

The purpose of phase 6 is not to claim a stronger result than phase 5. The purpose is to explain the surprising phase-5 result with a cleaner TSP-only experiment.

## Central Question

The main phase-6 question is:

> Is replay helping because it remembers true failures, or because it preserves broad distributional coverage?

The strongest phase-6 result shape is:

- replay conditions with higher archive descriptor diversity also show better held-out transfer
- raw failure severity alone is a weaker predictor than archive diversity
- residual-failure replay improves on naive failure replay by separating "hard for everyone" from "specifically bad for this heuristic"

## Descriptor Basis

Phase 6 adds per-instance descriptors for all train, holdout, replay, and adversarial TSP instances:

- number of cities
- coordinate spread
- nearest-neighbor distance statistics
- MST length
- convex-hull ratio
- clustering and cluster-separation scores
- grid-like versus random-like structure
- bottleneck or two-cluster structure
- nearest-neighbor trap score

Research basis:

- Reinelt, [TSPLIB-A Traveling Salesman Problem Library](https://doi.org/10.1287/ijoc.3.4.376), 1991
- Smith-Miles and Lopes, [Measuring instance difficulty for combinatorial optimization problems](https://www.cs.ubc.ca/labs/algorithms/EARG/stack/2012_ComputersAndOperationResearch_SmithMiles_MeasuringInstanceDifficulty.pdf), 2012
- Kerschke et al., [A study on the effects of normalized TSP features for automated algorithm selection](https://www.sciencedirect.com/science/article/pii/S0304397522006089), 2022
- Rice's algorithm-selection framing, as summarized in Smith-Miles and Lopes above, motivates using instance descriptors plus baseline performance to estimate expected difficulty
- Replication discipline in this repository still follows the repeated-run guidance already used in earlier phases:
  - [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560)
  - [Rliable: Better Evaluation for Reinforcement Learning](https://arxiv.org/abs/2108.13264)

## Benchmark Basis

Phase 6 stays TSP-only and keeps the same benchmark basis as phase 5 for comparability:

- the official TSPLIB95 Euclidean train subset
- held-out TSPLIB95 Euclidean instances
- adversarial synthetic geometric layouts
- exact synthetic geometric holdouts

This is deliberate. The phase-6 question is about replay mechanism, not cross-problem transfer.

## Replay Arms

The official comparison set is:

1. `no_replay`
2. `random_replay`
3. `failure_replay`
4. `random_replay_compression`
5. `stratified_random_replay`
6. `diversity_weighted_replay`
7. `residual_failure_replay`
8. `diversity_failure_replay`
9. `diversity_failure_replay_compression`

Key additions relative to phase 5:

- `random_replay_compression`, because the winning replay arm from phase 5 also needs a compression test
- `residual_failure_replay`, because raw failure gap is confounded with baseline hardness
- descriptor-aware replay variants, because archive coverage itself may be the relevant mechanism

## Residual Failure Replay

The defining phase-6 mechanism is:

`residual_failure_gap = observed_gap - expected_gap(instance_features, baseline_portfolio)`

The expected gap is estimated from:

- the instance descriptors above
- a fixed baseline heuristic portfolio
- descriptor-nearest neighbors over the benchmark and adversarial reference instances

Interpretation:

- large raw gap on a hard instance is not automatically a replay-worthy "true failure"
- large positive residual gap is stronger evidence that the current evolved heuristic has a specific weakness

## Required Logging

Log the replay archive composition over time, including:

- archive descriptor diversity
- archive hardness
- archive residual hardness
- archive size bias
- replay failure concentration
- structure histogram
- size histogram

These should be stored per epoch and summarized in both condition-level and aggregate reports.

## Endpoints

Primary endpoint:

- final held-out TSPLIB mean optimality gap

Secondary endpoints:

- final synthetic transfer gap
- combined transfer gap
- archive descriptor diversity
- archive hardness
- archive size bias
- replay failure concentration
- accepted code novelty
- heuristic complexity
- adaptation efficiency

Key diagnostic plot:

- held-out gap versus replay-archive descriptor diversity

The target interpretation is whether descriptor diversity predicts transfer better than raw archive hardness.

## Interpretation Rules

- Do not claim that residual replay is better unless it beats raw failure replay on held-out transfer, not only training.
- Do not claim that archive hardness is the right explanation if diversity tracks transfer better.
- Do not claim operator discovery or algorithm discovery from phase 6; this phase still evolves whole solver scaffolds.
- If random replay remains best, treat that as evidence about distributional coverage and anti-thrashing, not as a failure of the whole replay hypothesis.

## Replication

Official main-study target:

- 20 paired seed offsets with the fixed list `0, 1000, 2000, ..., 19000`

Use paired comparisons across those same offsets and report uncertainty on paired deltas, not only per-condition means.

## Deliverable

The required deliverable is a short mechanism report that answers:

1. Why did `random_replay` beat `failure_replay`?
2. Does replay-archive diversity explain transfer better than replay hardness?
3. Does compression help once applied to the best replay mechanism?
4. Are the final heuristics genuinely different, or just differently tuned?

## Operational Entry Points

- Prepare the benchmark manifest with [prepare_tsp_benchmarks.py](../prepare_tsp_benchmarks.py)
- Run the suite with [run_tsp_suite.py](../run_tsp_suite.py) and [configs/tsp_phase6_suite/01_replay_mechanism.json](../configs/tsp_phase6_suite/01_replay_mechanism.json)
- Use [configs/tsp_phase6_suite/RUNBOOK.md](../configs/tsp_phase6_suite/RUNBOOK.md) for concrete commands
- Aggregate repeated runs with [aggregate_tsp_phase6_runs.py](../aggregate_tsp_phase6_runs.py)
- Official results note: versioned on branch `replay-mechanism` as `docs/PHASE_6_TSP_REPLAY_MECHANISM_RESULTS_2026-05-20.md`

## Relationship To Phase 5

Phase 5 established that the first routing pass is scientifically useful but mixed. Phase 6 is the thesis-safe follow-up that tries to explain that mixed result before the project makes stronger claims about replay-aware abstraction.
