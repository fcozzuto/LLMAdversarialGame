# Phase 9 Real-World CVRP Solver Evolution Results (2026-05-21)

This note records the official 20-offset phase-9 bounded real-world CVRP solver-evolution campaign.

The official artifact archive for this phase is under `runs/cvrp_phase9_suite/solver_evolution/aggregate_20260521_220715_t`.

## Headline

Phase 9 produced a technically valid whole-solver evolution study on real-world `CVRPLIB` `X` instances, but it did not beat the strongest fixed baseline on the primary held-out endpoint.

- The campaign is technically valid: 20 paired runs, 4 conditions, judge enabled in all 20 runs, and no hidden fallback or timeout contamination in the accepted solvers.
- The solver-evolution arm remained feasible in every official run on both the train and held-out panels.
- Across the full official campaign, solver evolution had 39 accepted epochs out of 160 total epochs.
- There were 0 generation fallbacks, 0 generation errors, 0 accepted fallback or errored generations, and 0 solver-worker timeouts in the completed official runs.
- The best mean held-out condition was `phase9_baseline_clarke_wright_savings`.
- `phase9_solver_evolution` clearly beat the weaker nearest-neighbor and regret-insertion baselines, but it did not beat Clarke-Wright on average.

The right interpretation is therefore:

> phase 9 shows that the LLM-driven evolution loop can reliably synthesize feasible, interpretable CVRP solver code that improves over weaker bounded baselines on held-out real-world benchmarks, but in this bounded setup it did not outperform the strongest fixed baseline.

## Main Findings

- Best mean held-out condition: `phase9_baseline_clarke_wright_savings`, mean penalized gap `0.073766`.
- `phase9_solver_evolution`: mean held-out penalized gap `0.182231`, 95% bootstrap CI `[0.145116, 0.218699]`.
- `phase9_baseline_nearest_neighbor_constructive`: mean held-out penalized gap `0.273435`.
- `phase9_baseline_regret_insertion_local_search`: mean held-out penalized gap `0.466391`.
- `phase9_solver_evolution` versus `phase9_baseline_nearest_neighbor_constructive`: held-out penalized-gap delta `-0.091204`, 95% CI `[-0.128136, -0.055417]`.
- `phase9_solver_evolution` versus `phase9_baseline_clarke_wright_savings`: held-out penalized-gap delta `+0.108465`, 95% CI `[0.071184, 0.144731]`.
- `phase9_solver_evolution` versus `phase9_baseline_regret_insertion_local_search`: held-out penalized-gap delta `-0.284160`, 95% CI `[-0.321769, -0.247706]`.
- Solver evolution beat nearest-neighbor in 15 of 20 runs, matched it in 5 of 20 runs, and beat Clarke-Wright in 5 of 20 runs.
- The frozen final incumbents were not one repeated artifact: there were 16 distinct final solver fingerprints across the 20 official runs, with the repeated fingerprint corresponding to the no-acceptance runs that stayed at the same starting incumbent.

## Technical Validity

The phase-9 conclusions are not based on the aggregate report alone.

They were checked against:

- the aggregate report and `aggregate_summary.json` for means, paired deltas, and confidence intervals
- all 20 `suite_summary.json` and `run_metadata.json` files for structural validity
- lower-level `condition_summary.json` and epoch `artifact.json` files for the solver-evolution arm

The main technical checks were:

- 20 paired runs were present under `runs/cvrp_phase9_suite/solver_evolution`
- all 4 conditions were present in every run
- judge status was `enabled` in all 20 runs
- solver evolution had 39 accepted epochs across 160 total epochs
- no accepted epoch used fallback code or contained a recorded generation error
- no completed official run contained solver-worker timeout artifacts
- train and held-out feasibility were 100% in every official run

The campaign is complete enough for interpretation as run.

## Interpretation

Phase 9 supports a narrower, defensible real-world solver-evolution claim.

- The loop can generate and preserve feasible CVRP solver code on held-out official benchmarks.
- It improves substantially over weaker bounded baselines.
- It does not beat the strongest fixed baseline in this bounded setting.
- The resulting solvers are diverse enough to show real search rather than fallback collapse or one repeated incumbent artifact.

The strongest positive result is that solver evolution beat nearest-neighbor and regret-insertion plus local search while preserving full held-out feasibility. The result shows measurable solver-code adaptation on a validator-heavy real-world optimization family.

The main limitation is that Clarke-Wright remained the best fixed method on the primary held-out endpoint. So the phase-9 claim should not be framed as "LLM evolution beat the strongest practical CVRP baseline." It should be framed as:

> given only the problem specification, validator, scorer, and training instances, the LLM-driven evolution loop generated feasible held-out CVRP solvers that improved over weaker naive baselines but did not surpass the strongest fixed heuristic in the bounded benchmark regime.

The runtime picture is also mixed. Solver evolution had a heavy-tailed held-out runtime distribution: mean `821.7 ms`, median about `255.2 ms`, and one run-level maximum over `7.4 s`. So the evolved solvers are not only judged by gap; they currently trade off more variable runtime for better solution quality than the weakest baselines.

## Consequence For Cross-Family Synthesis

Phase 9 now gives the project a third benchmark family beyond the original simple adversarial games and the routing/TSP benchmark phases.

That makes the next research step a cross-family synthesis rather than another engineering phase. A conservative synthesis is:

- in the simple games, the loop adapts and changes behavior under adversarial pressure
- in benchmark routing, replay and portfolio-style control produce mixed but interpretable family-dependent outcomes
- in real-world CVRP, whole-solver evolution can reliably produce feasible solver logic and beat weaker baselines, but not the strongest fixed heuristic

This framing reports the positive solver-evolution evidence while preserving the limiting role of the strongest fixed routing baseline.

## Sources

- [Phase 9 aggregate report](../runs/cvrp_phase9_suite/solver_evolution/aggregate_20260521_220715_t/aggregate_report.md)
- [Phase 9 aggregate summary JSON](../runs/cvrp_phase9_suite/solver_evolution/aggregate_20260521_220715_t/aggregate_summary.json)
- [Phase 9 final run suite summary](../runs/cvrp_phase9_suite/solver_evolution/run_20260521_220715_t/suite_summary.json)
- Representative solver-evolution artifacts under [runs/cvrp_phase9_suite/solver_evolution](../runs/cvrp_phase9_suite/solver_evolution)
