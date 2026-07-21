# Phase 12 SOTA CVRP HGS Baseline Results (2026-07-21)

This note records the official external HGS-style CVRP calibration on branch
`sota-cvrp-hgs-baseline`.

The official artifact archive is under
`runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5`.

## Protocol

- Solver: PyVRP `0.13.4`, using its HGS-style vehicle-routing solver.
- Dependency parser: VRPLIB `2.2.0`.
- Panel: the same five held-out CVRPLIB X instances used in phase 9 and the phase-9 closeout.
- Seeds: `1, 2, 3, 4, 5`.
- Runtime cap: `30` seconds per seed.
- Reporting rule: best validated seed per instance.
- Validation: every selected route set was revalidated with the project phase-9 CVRP validator.

## Results

| Instance | Best seed | Cost | Best known | Gap | Wall seconds |
|---|---:|---:|---:|---:|---:|
| X-n176-k26 | 5 | 48161 | 47812 | 0.007299 | 30.036 |
| X-n190-k8 | 4 | 17020 | 16980 | 0.002356 | 30.042 |
| X-n223-k34 | 4 | 40726 | 40437 | 0.007147 | 30.056 |
| X-n247-k50 | 5 | 37671 | 37274 | 0.010651 | 30.057 |
| X-n275-k28 | 3 | 21320 | 21245 | 0.003530 | 30.058 |

The mean held-out penalized gap for all 25 runs is `0.008779`. The mean held-out penalized gap
for the best validated seed per instance is `0.006197`, with feasibility rate `1.0`.

## Validation Audit

The archive was audited after the run:

- all 25 expected runs are present,
- all five held-out instances have one selected best seed,
- all selected best routes revalidate as feasible with the phase-9 validator,
- the recomputed best-seed mean held-out penalized gap is `0.006197`,
- the selected best routes match the costs and gaps stored in the CSV and JSON summaries.

## Interpretation

This calibration strengthens the thesis boundary. PyVRP's best-seed mean held-out gap of
`0.006197` is lower than the Clarke-Wright mean held-out gap of `0.073766` and far lower than the
phase-9 closeout replay-evolution mean held-out gap of `0.171114`.

The calibration does not invalidate the phase-9 mechanism result because PyVRP is an external
specialized solver, not a learned code-evolution condition. It does rule out a practical claim that
the evolved CVRP solvers are competitive with mature HGS-style vehicle-routing search on this
held-out benchmark slice.

The thesis should therefore use this phase as an external baseline calibration: current
LLM-guided code evolution can produce feasible CVRP solver logic and mechanism-level improvements
over weaker learned controls, but mature specialized VRP search remains the stronger reference
point.

## Sources

- Protocol: `docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_PROTOCOL.md`
- Runner: `run_cvrp_phase12_sota_hgs_baseline.py`
- Result summary: `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/summary.md`
- Aggregate JSON: `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/summary.json`
- Per-seed rows: `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/pyvrp_hgs_runs.csv`
- Best-by-instance rows: `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/pyvrp_hgs_best_by_instance.csv`
- Best routes: `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/best_routes.json`
