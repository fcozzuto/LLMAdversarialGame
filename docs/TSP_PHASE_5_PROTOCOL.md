# Phase 5 TSP Benchmark Transfer Protocol

This document defines the first benchmark-transfer phase after the grid-game causal-transfer analysis.

The goal is to test whether the replay-aware curriculum machinery can move beyond toy strategic environments and progressively improve genuinely reusable optimization structure on a real benchmark family.

## Central Question

The phase-5 claim under test is narrower than "the model invented a new state-of-the-art solver":

> Replay-aware evolution may improve transfer to unseen TSP instance families while the magnitude of accepted code edits decreases over time.

That is the main result shape that matters here.

## Benchmark Basis

Phase 5 uses:

- official TSPLIB95 Euclidean benchmark instances and official optimal-tour files from the TSPLIB95 catalog
- exact synthetic geometric holdouts for clustered and deceptive layouts
- a constrained heuristic scaffold rather than unconstrained full-solver generation

Research basis:

- Gerhard Reinelt, [TSPLIB-A Traveling Salesman Problem Library](https://doi.org/10.1287/ijoc.3.4.376), 1991
- TSPLIB95 official TSP catalog: [tsp.html](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp.html)
- TSPLIB95 official symmetric-optima page: [STSP.html](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/STSP.html)
- S. Lin and B. W. Kernighan, [An Effective Heuristic Algorithm for the Traveling-Salesman Problem](https://doi.org/10.1287/opre.21.2.498), 1973
- Daniel J. Rosenkrantz, Richard E. Stearns, and Philip M. Lewis II, [An Analysis of Several Heuristics for the Traveling Salesman Problem](https://doi.org/10.1137/0206041), 1977
- Existing replication and generalization guidance already used in this repository:
  - [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560)
  - [A Study on Overfitting in Deep Reinforcement Learning](https://research.google/pubs/a-study-on-overfitting-in-deep-reinforcement-learning/)
  - [Measuring Sample Efficiency and Generalization in RL with Procgen](https://openreview.net/forum?id=rylKB3A9Fm)

## Why A Constrained Heuristic Scaffold

This phase does not ask the model to write arbitrary solvers from scratch.

It asks the model to modify a bounded heuristic scaffold that already contains:

- nearest-neighbor style construction
- candidate pruning
- 2-opt local improvement
- bounded 3-opt sampling
- route perturbation
- deterministic restart logic
- deterministic acceptance schedules
- simple clustering/decomposition bias

This keeps the scientific question focused on reusable heuristic structure instead of unconstrained lexical search.

## Training And Evaluation Split

### Training

Train or evolve on a subset of TSPLIB95 Euclidean instances only.

### Replay Archives

Maintain archives for:

- worst-performing training instances
- adversarial synthetic geometric layouts
- catastrophic failure cases above a fixed optimality-gap threshold

For the current phase-5 implementation, the `failure_replay` arm replays the highest raw-gap cases from the worst-case archive. The catastrophic-failure archive is still logged separately and remains available for later mechanism variants.

### Final Evaluation

Evaluate the final accepted heuristic on:

- held-out TSPLIB95 Euclidean instances
- exact synthetic clustered or deceptive holdouts

Selection-time replay probes and transfer probes are allowed as inner-loop filters, but they are not the final evidence.
For this phase, use adversarial geometric layouts in the inner-loop transfer probe and archive machinery, while keeping the exact synthetic holdouts for final evaluation.

## Required Comparisons

The default phase-5 comparison set is:

1. `tsplib_no_replay`
2. `tsplib_random_replay`
3. `tsplib_failure_replay`
4. `tsplib_failure_replay_compression`

Interpretation target:

- whether raw-gap failure replay beats both no replay and random replay
- whether replay plus compression pressure preserves or improves transfer while reducing novelty or complexity growth

## Endpoints

Primary endpoint:

- final held-out TSPLIB mean optimality gap

Secondary endpoints:

- final synthetic holdout mean optimality gap
- combined transfer gap across held-out TSPLIB and synthetic holdouts
- code novelty or edit distance across accepted epochs
- heuristic complexity
- adaptation efficiency

Exploratory metrics:

- per-family holdout gap
- replay-probe gap
- archive composition over time
- behavior-profile and behavior-cell changes

## Interpretation Rules

- Do not claim state-of-the-art TSP invention from this phase.
- Do not treat lower training gap alone as evidence of transfer.
- Do not treat replay probes as substitutes for final held-out evaluation.
- Do not treat code novelty as innovation without corresponding held-out improvements.
- The strongest result shape is:
  - lower held-out gap later in training
  - lower or stabilizing heuristic complexity
  - decreasing accepted code novelty

If that pattern appears, describe it as evidence for reusable heuristic abstraction or compression, not as proof of universal algorithm discovery.

## Replication

Recommended minimum:

- 10 paired seed offsets for an official result

Official main-study target for this repository:

- 20 paired seed offsets with the fixed offset list `0, 1000, 2000, ..., 19000`

For the final routing aggregates, use paired comparisons across those same offsets and report uncertainty on the paired deltas, not only per-condition means.

Keep the benchmark manifest, held-out set, and synthetic families fixed across compared conditions.

## Operational Entry Points

- Prepare benchmarks with [prepare_tsp_benchmarks.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/prepare_tsp_benchmarks.py)
- Run the suite with [run_tsp_suite.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/run_tsp_suite.py)
- Use [configs/tsp_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/tsp_suite/RUNBOOK.md) for concrete commands
- Aggregate replicated runs with [aggregate_tsp_runs.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/aggregate_tsp_runs.py)
- For the asymmetric and vehicle-routing follow-on phases, use [docs/ROUTING_PHASE_5B_5C_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/ROUTING_PHASE_5B_5C_PROTOCOL.md)

## Current Evidence Note

The first completed 20-offset routing pass is summarized in [docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md).

For this TSP family, the strongest result was not `failure_replay`; it was `random_replay`. That means this protocol remains useful as the benchmark recipe, but the completed evidence should be read through the results note rather than through the original expectation alone.

The two direct follow-on phases are now:

- [docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md) for the mechanism study
- [docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md) for modular operator discovery
