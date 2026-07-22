# Phase 5B/5C Routing Benchmark Extension Protocol

This document defines the two immediate extensions after the initial symmetric-TSPLIB phase-5 benchmark transfer:

- phase 5B: asymmetric TSPLIB95 ATSP
- phase 5C: CVRPLIB capacitated vehicle routing

The scientific goal is not to chase a one-off benchmark win. It is to test whether the replay-aware curriculum machinery keeps the same signature under harder and more structurally different routing problems:

> Later-stage replay-aware heuristics should improve held-out routing optimality gap while requiring progressively smaller accepted code edits.

## Why These Two Extensions

ATSP tests whether the replay-aware signal survives the loss of symmetric geometry. The candidate solution is still a Hamiltonian tour, but many of the useful inductive biases for Euclidean TSP no longer apply directly.

CVRP tests whether the same machinery survives the move from single-tour optimization to constrained multi-route construction with capacity feasibility.

Together, these are the most direct follow-ons to the initial TSP phase without jumping prematurely into an unbounded "graph optimization" bucket.

## Benchmark Basis

Phase 5B uses:

- official TSPLIB95 ATSP instances
- official TSPLIB95 best-known ATSP objective values
- exact synthetic asymmetric holdouts built from geometric layouts with directed-cost distortions

Phase 5C uses:

- official CVRPLIB instances
- official CVRPLIB solution downloads and catalog upper bounds
- exact synthetic CVRP holdouts with small customer counts so the optimum can be recomputed exactly

Research basis:

- Gerhard Reinelt, [TSPLIB-A Traveling Salesman Problem Library](https://doi.org/10.1287/ijoc.3.4.376), 1991
- TSPLIB95 official ATSP catalog: [atsp.html](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/atsp.html)
- TSPLIB95 official ATSP best-known-values page: [ATSP.html](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/ATSP.html)
- Eduardo Uchoa et al., [New benchmark instances for the Capacitated Vehicle Routing Problem](https://doi.org/10.1016/j.ejor.2016.08.012), 2017
- CVRPLIB official catalog: [All Instances](https://galgos.inf.puc-rio.br/cvrplib/en/instances)

## Heuristic-Scaffold Constraints

Phase 5B keeps a constrained ATSP scaffold with bounded control over:

- directed nearest-neighbor variants
- candidate pruning
- directed 2-opt / bounded 3-opt
- relocation
- restart logic
- matrix-derived clustering bands
- acceptance schedules

Phase 5C keeps a constrained CVRP scaffold with bounded control over:

- seeded route construction
- candidate pruning
- intra-route 2-opt / bounded 3-opt
- intra-route relocation
- inter-route relocate/swap proposals
- route perturbation
- restart logic
- sweep or clustering bias
- acceptance schedules

This is deliberate. The question is still reusable structure under replay-aware evolution, not unconstrained code search.

## Replay And Transfer Design

Both extension phases keep the same four core condition families:

1. no replay
2. random replay
3. raw-gap failure replay
4. failure replay plus compression pressure

Both maintain replay archives for:

- worst-performing training instances
- adversarial synthetic layouts
- catastrophic failure cases above a fixed gap threshold

As in the symmetric TSP phase, the current `failure_replay` arm replays the highest raw-gap cases from the worst-case archive, while the catastrophic-failure archive is logged separately for diagnosis and later mechanism variants.

Both reserve exact synthetic holdouts for final evaluation rather than allowing them to leak into the inner loop.

## Family-Specific Notes

### ATSP

- Primary endpoint: final held-out TSPLIB ATSP mean optimality gap.
- Synthetic families are asymmetric geometric layouts, not symmetric Euclidean tours.

### CVRP

- Primary endpoint: final held-out CVRPLIB mean optimality gap.
- Feasibility is part of the task. Capacity-violating routes are not admissible.
- The preparation script cross-checks official solution files against recomputed route cost before an instance is admitted to the curated subset.
- One malformed official solution file (`B-n50-k8`) is excluded from the curated subset because its route list duplicates a customer. Excluding a bad artifact is preferable to weakening the validator or silently trusting an inconsistent file.

## Replication Requirement

Recommended minimum for each extension:

- 10 paired seed offsets for an official result

Official target for this repository:

- 20 paired seed offsets with the fixed offset list `0, 1000, 2000, ..., 19000`

Use the exact same offset list across TSP, ATSP, and CVRP so the paired replay-condition comparisons are directly aligned.
Report paired uncertainty on condition deltas, not only independent condition summaries.

The replicated aggregates are now available. The current evidence note is [docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md](PHASE_5_ROUTING_RESULTS_2026-05-14.md), and its main conclusion is mixed rather than uniformly positive.

## Operational Entry Points

- Prepare ATSP benchmarks with [prepare_atsp_benchmarks.py](../prepare_atsp_benchmarks.py)
- Run ATSP experiments with [run_atsp_suite.py](../run_atsp_suite.py)
- Aggregate ATSP runs with [aggregate_atsp_runs.py](../aggregate_atsp_runs.py)
- Use [configs/atsp_suite/RUNBOOK.md](../configs/atsp_suite/RUNBOOK.md) for ATSP commands
- Prepare CVRP benchmarks with [prepare_cvrp_benchmarks.py](../prepare_cvrp_benchmarks.py)
- Run CVRP experiments with [run_cvrp_suite.py](../run_cvrp_suite.py)
- Aggregate CVRP runs with [aggregate_cvrp_runs.py](../aggregate_cvrp_runs.py)
- Use [configs/cvrp_suite/RUNBOOK.md](../configs/cvrp_suite/RUNBOOK.md) for CVRP commands
- Use [docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md](PHASE_5_ROUTING_RESULTS_2026-05-14.md) when interpreting the completed TSP/ATSP/CVRP evidence pass.
