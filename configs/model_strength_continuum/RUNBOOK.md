# Clean Model-Strength Continuum Runbook

Use branch `clean-model-strength-continuum` in this workspace.

Activate your environment first:

```powershell
conda activate Python3_14
```

## Purpose

This phase keeps the previous negative replay result intact, but reruns the model-strength axis more cleanly:

- five pinned GPT-5 frontier-family snapshots,
- same prompting setup,
- same configured reasoning effort (`low`, with reasoning-effort fallback disabled for this clean-continuum phase),
- same validator stack,
- same candidate budgets,
- preflight check that the pinned models accept the configured reasoning efforts,
- empirical calibration before the full run,
- TSP saturation diagnostics and pooled analyses with and without TSP,
- CVRP split into feasibility escape, penalized objective, and feasible-only quality.

## No-Cost Smoke Test

This validates schema and aggregation only. It uses the builtin provider and writes to `DO NOT COMMIT`.

```powershell
$smokeStamp = Get-Date -Format "yyyyMMdd_HHmmss"
python run_model_strength_factorial.py --config configs/model_strength_continuum_smoke.yaml --timestamp $smokeStamp --task-family simple_games --model-tier builtin_smoke --technique single_shot,budget_matched_no_replay
python aggregate_model_strength_factorial.py --run-root "DO NOT COMMIT/model_strength_continuum_smoke/$smokeStamp"
```

Confirm:

```powershell
Test-Path "DO NOT COMMIT/model_strength_continuum_smoke/$smokeStamp/all_runs_long.csv"
Test-Path "DO NOT COMMIT/model_strength_continuum_smoke/$smokeStamp/cell_means.csv"
Test-Path "DO NOT COMMIT/model_strength_continuum_smoke/$smokeStamp/variance_decomposition/variance_partition_summary.csv"
Test-Path "DO NOT COMMIT/model_strength_continuum_smoke/$smokeStamp/final_report.md"
```

## Reasoning-Effort Preflight

Run this before any larger paid campaign if you are considering `low`, `medium`, or `high` reasoning. It sends one tiny Responses API request per pinned model x effort, writes the result to `DO NOT COMMIT`, and does not retry with alternate efforts.

```powershell
python probe_openai_reasoning_efforts.py --config configs/model_strength_continuum_factorial.yaml --efforts low,medium,high --max-output-tokens 16
```

Confirm that the printed `common_supported_efforts` includes the effort you plan to use. Keep `allow_reasoning_effort_fallback=false` for official runs so the campaign fails fast instead of silently switching a model to a different reasoning setting.

## Paid Calibration Suite

This is the small empirical coding-strength calibration. It uses only `single_shot` and two seeds per task family, so the planned scale is:

`5 models x 3 task families x 2 seeds = 30 API-generated candidates`.

```powershell
$calStamp = Get-Date -Format "yyyyMMdd_HHmmss"
python run_model_strength_factorial.py --config configs/model_strength_continuum_calibration.yaml --timestamp $calStamp --technique single_shot
python derive_model_strength_scores.py --calibration-run-root "runs/model_strength_continuum_calibration/$calStamp" --base-config configs/model_strength_continuum_factorial.yaml --output-config "DO NOT COMMIT/model_strength_continuum_factorial_calibrated_$calStamp.yaml"
```

Use the generated calibrated config for the full run. It replaces ordinal snapshot scores with train-validator calibration scores and keeps the calibration source path in `model_strength_table.csv`.

The uncalibrated full template intentionally fails if passed directly to `run_model_strength_factorial.py`. This prevents accidentally launching the official paid campaign with placeholder snapshot-order scores instead of the required empirical calibration scores.

## Cost Estimate

Run this before the full campaign. It uses empirical prompt/response sizes from the completed 750-row campaign, current model price assumptions in the estimator, and a default 20% balance buffer. By default it samples up to 250 old candidate artifacts per task x technique for speed; use `--max-reference-candidates-per-task-technique 0` if you want to scan every prior candidate artifact.

```powershell
python estimate_model_strength_continuum_cost.py --config "DO NOT COMMIT/model_strength_continuum_factorial_calibrated_$calStamp.yaml"
```

If you have not run calibration yet, use the uncalibrated config for a pre-calibration estimate:

```powershell
python estimate_model_strength_continuum_cost.py --config configs/model_strength_continuum_factorial.yaml
```

Estimate the paid calibration suite separately:

```powershell
python estimate_model_strength_continuum_cost.py --config configs/model_strength_continuum_calibration.yaml --technique single_shot --output-dir "DO NOT COMMIT/model_strength_continuum_calibration_cost_estimate"
```

## Full Paid Campaign

Only run this after smoke, calibration, and cost estimation are complete.

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
python run_model_strength_factorial.py --config "DO NOT COMMIT/model_strength_continuum_factorial_calibrated_$calStamp.yaml" --timestamp $stamp
python aggregate_model_strength_factorial.py --run-root "runs/clean_model_strength_factorial/$stamp"
```

If interrupted, resume with the same `$stamp`:

```powershell
python run_model_strength_factorial.py --config "DO NOT COMMIT/model_strength_continuum_factorial_calibrated_$calStamp.yaml" --timestamp $stamp --skip-existing
python aggregate_model_strength_factorial.py --run-root "runs/clean_model_strength_factorial/$stamp"
```

## Planned Full Scale

The full campaign produces 1,250 run rows:

- `simple_games`: `5 models x 5 techniques x 10 seeds = 250` rows.
- `tsp`: `5 models x 5 techniques x 20 seeds = 500` rows.
- `cvrp_phase9_real_world`: `5 models x 5 techniques x 20 seeds = 500` rows.

Candidate-generation budget is 26,650 candidates:

- `simple_games`: `5 models x 10 seeds x (1 + 4 x 100) = 20,050`.
- `tsp`: `5 models x 20 seeds x (1 + 4 x 8) = 3,300`.
- `cvrp_phase9_real_world`: `5 models x 20 seeds x (1 + 4 x 8) = 3,300`.

## Added Outputs

In addition to the prior factorial outputs, aggregation now writes:

- `cvrp_decomposition/cvrp_metric_cell_means.csv`
- `cvrp_decomposition/cvrp_vs_budget_matched_metric_effects.csv`
- `tsp_diagnostics/tsp_saturation_diagnostics.csv`
- `tsp_diagnostics/tsp_materialization_audit.csv`
- pooled variance decomposition rows with `analysis_scope=pooled_without_tsp:*`
- realized-budget accounting columns in `all_runs_long.csv` and `cell_means.csv`

## Interpretation Rules

Replay/failure/compression should only be claimed useful when they beat `budget_matched_no_replay` in paired/bootstrap comparisons.

TSP must be interpreted in two ways:

- as part of the full cross-family pool,
- and as a possible saturation case through pooled-without-TSP analyses and `tsp_saturation_diagnostics.csv`.

CVRP must be interpreted as three outcomes:

- feasibility/penalty escape,
- penalized objective quality,
- feasible-only objective quality.
