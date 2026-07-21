# Phase 12 SOTA CVRP HGS Baseline Protocol

## Purpose

This phase adds an external state-of-the-art calibration baseline for the retained phase-9
capacitated vehicle routing problem (CVRP) evidence.

The goal is not to add another learned code-evolution condition. The goal is to bound the thesis
claim against a mature specialized vehicle-routing solver. If the evolved CVRP solvers remain
behind a modern hybrid genetic search (HGS) implementation on the same held-out instances, the
thesis must describe the phase-9 result as a mechanism and feasibility result rather than as
practical solver dominance.

## Relationship To Earlier Phases

This phase is a post-defense calibration requested during thesis revision. It uses the same
benchmark slice as the phase-9 real-world CVRP solver evolution and phase-9 closeout studies:

- benchmark family: CVRPLIB Uchoa X-series CVRP instances,
- split: the existing phase-9 held-out panel,
- validator: the existing phase-9 CVRP validator,
- endpoint: held-out penalized optimality gap,
- feasibility checks: customer coverage, duplicate customers, capacity, and route validity.

The HGS-style solver is external. It is not part of the LLM-guided code-evolution loop and must
not be counted as another evolved-code arm.

## Baseline

The official baseline is PyVRP, an open-source vehicle-routing solver package that implements
hybrid genetic search ideas. The official run uses:

- PyVRP version: `0.13.4`,
- VRPLIB version: `2.2.0`,
- panel: `holdout`,
- instances: the five existing phase-9 held-out CVRPLIB X instances,
- seeds: `1, 2, 3, 4, 5`,
- runtime cap: `30` seconds per seed,
- reporting rule: best validated seed per instance.

The reduced five-instance subset is acceptable because the examiner request explicitly allowed a
reduced instance subset when compute-limited, and because the calibration is used only as a
boundary check against the same held-out slice already used by phase 9.

## Command

Install or expose the exact dependency versions before running:

```powershell
python -m pip install pyvrp==0.13.4 vrplib==2.2.0
```

Then run:

```powershell
python run_cvrp_phase12_sota_hgs_baseline.py `
  --output-dir runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5 `
  --panel holdout `
  --runtime-seconds 30 `
  --seeds 1 2 3 4 5
```

If dependencies are installed into a local target directory rather than the active environment,
pass that directory with `--pydeps`.

## Required Outputs

The official archive must contain:

- `summary.md`,
- `summary.json`,
- `pyvrp_hgs_runs.csv`,
- `pyvrp_hgs_best_by_instance.csv`,
- `best_routes.json`.

The public result note must be written to:

```text
docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_RESULTS_2026-07-21.md
```

## Validity Checks

The result is usable only if:

- all 25 expected runs are present,
- all five held-out instances have a selected best seed,
- each selected route set revalidates with the project phase-9 validator,
- the best-by-instance feasibility rate is reported,
- the mean held-out penalized gap is reported for both all runs and best seed per instance,
- the interpretation remains bounded: PyVRP calibrates solver strength, but does not invalidate
  the separate learned-mechanism comparisons.

## Branch And Tag

- Working branch: `sota-cvrp-hgs-baseline`
- Official archive tag: `phase-12-sota-cvrp-hgs-baseline`

The tag should point to the final archive/results commit, after the official run outputs and
result note are committed.
