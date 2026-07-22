# Cross-Family Code-Evolution Synthesis Runbook

This runbook reproduces the cross-family synthesis over the completed official experiment families.

It does not call paid model APIs. It reads archived official run artifacts and evaluates the historical direct Codex CVRP check locally through the phase-9 sandbox and validator.

## Inputs

- Simple-game transfer artifacts: `runs/transfer_suite/rotating_plus_replay_aware_selection`
- TSP replay artifacts: `runs/tsp_suite/replay_transfer`
- Real-world CVRP phase-9 artifacts: `runs/cvrp_phase9_suite/solver_evolution`
- Phase-9 CVRP config: `configs/cvrp_phase9_suite/01_solver_evolution.json`

## Command

Run from the repository root after activating the normal project environment:

```powershell
conda activate Python3_14
python analyze_cross_family_evolution.py
```

For a deterministic archive name, pass a timestamp:

```powershell
python analyze_cross_family_evolution.py --timestamp 20260522_165500
```

## Outputs

The script writes a new directory under `runs/cross_family_synthesis/meta_patterns_<timestamp>` containing:

- `cross_family_summary.json`: normalized metrics and meta-pattern payload.
- `cross_family_report.md`: human-readable synthesis report.
- `cross_family_report.pdf`: PDF version of the synthesis report.
- `codex_direct_cvrp_solver.py`: historical direct Codex-authored deterministic CVRP solver.
- `codex_direct_cvrp_summary.json`: train/holdout validation results for the historical direct solver.

## Interpretation Rules

- Treat the cross-family synthesis as an analysis artifact over completed official campaigns, not a new replicated paid experiment.
- Treat the direct Codex CVRP solver as a historical single-shot descriptive check. It is not retained thesis evidence unless a future protocol freezes and replicates direct-Codex prompting.
- Keep train-time search dynamics separate from held-out endpoint evidence.
- Do not infer that code novelty means behavioral novelty unless the relevant family has behavioral validation or held-out transfer evidence.
