# Phase 5 Routing Results (2026-05-14)

This note records the first completed routing-benchmark evidence pass after the phase-5 protocol expansion.

The routing phase is now evidence-complete in the narrow sense that the official replicated suites were run and aggregated for:

- symmetric TSPLIB95 Euclidean TSP
- asymmetric TSPLIB95 ATSP
- CVRPLIB capacitated vehicle routing

Each family used:

- 20 paired offsets
- 4 compared conditions
- paired bootstrap delta summaries on the main endpoints

The compared routing conditions were:

1. no replay
2. random replay
3. failure replay
4. failure replay plus compression pressure

## Main Outcome

The current evidence is mixed and family-dependent.

- TSP: `random_replay` is the clearest winner.
- ATSP: `failure_replay_compression` is weakly favorable on combined transfer, but not cleanly on the primary held-out ATSP endpoint.
- CVRP: `no_replay` is the strongest overall baseline.

This means the phase does not currently support a broad claim that true failure replay is the dominant routing recipe across benchmark families.

## Family Summaries

### TSP

Best mean condition:

- `tsplib_random_replay`

Main paired result versus `tsplib_no_replay`:

- held-out TSPLIB gap delta: `-0.0311`, 95% CI `[-0.0602, -0.0008]`
- combined transfer-gap delta: `-0.0282`, 95% CI `[-0.0520, -0.0029]`

Interpretation:

- replay can help on a real routing family
- the strongest TSP gain came from `random_replay`, not `failure_replay`
- compression pressure sharply reduced accepted novelty relative to plain failure replay, but without a clean endpoint win

### ATSP

Best mean condition:

- `atsp_failure_replay_compression`

Main paired result versus `atsp_no_replay`:

- combined transfer-gap delta: `-0.0063`, 95% CI `[-0.0133, -0.0002]`
- held-out ATSP-gap delta: `-0.0056`, 95% CI `[-0.0191, 0.0071]`

Interpretation:

- the compression-aware arm is directionally encouraging
- the primary held-out ATSP endpoint is not decisively separated
- this is a weakly favorable rather than strongly confirmatory result

### CVRP

Best mean condition:

- `cvrp_no_replay`

Narrow paired result:

- `cvrp_failure_replay` beats `cvrp_random_replay` on held-out CVRPLIB gap with delta `-0.0076`, 95% CI `[-0.0146, -0.0006]`

But:

- `cvrp_failure_replay` does not beat `cvrp_no_replay`
- `cvrp_failure_replay_compression` lowers complexity relative to `no_replay` without improving the main endpoint

Interpretation:

- replay is not the dominant recipe on this family
- CVRP currently acts more as a boundary case than as a confirmation

## Research Interpretation

The strongest defensible reading is:

- replay-aware machinery can matter on real routing benchmarks
- the effect is conditional on benchmark family
- the current routing results do not justify a general replay-dominance claim
- the current routing results also do not justify a strong "reusable heuristic compression" claim across all three families

That is still scientifically useful. It narrows the thesis claim from "replay always helps" to "replay pressure interacts with problem structure, and its benefits do not transfer uniformly across routing families."

## Primary Sources

- [TSP aggregate report](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_suite/replay_transfer/aggregate_20260513_155249_t/aggregate_report.md)
- [ATSP aggregate report](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/atsp_suite/replay_transfer/aggregate_20260513_185617_t/aggregate_report.md)
- [CVRP aggregate report](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/cvrp_suite/replay_transfer/aggregate_20260513_200113_t/aggregate_report.md)
- [TSP aggregate summary JSON](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_suite/replay_transfer/aggregate_20260513_155249_t/aggregate_summary.json)
- [ATSP aggregate summary JSON](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/atsp_suite/replay_transfer/aggregate_20260513_185617_t/aggregate_summary.json)
- [CVRP aggregate summary JSON](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/cvrp_suite/replay_transfer/aggregate_20260513_200113_t/aggregate_summary.json)
