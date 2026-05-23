# Model Strength x Evolution Factorial Runbook

This runbook implements the final crossed experiment requested by the supervisor:

`3 task families x 3 model tiers x 5 evolution techniques`, with fixed train/held-out splits and budget-matched controls.

Use the branch `model-strength-factorial`. Activate your environment first:

```powershell
conda activate Python3_14
```

## Smoke Test

The smoke test is no-cost because it uses the builtin game policy generator. It writes to `DO NOT COMMIT/`, not to official artifacts.

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
python run_model_strength_factorial.py --config configs/model_strength_factorial_smoke.yaml --timestamp $stamp --task-family simple_games --model-tier weak_model --technique single_shot,budget_matched_no_replay
python aggregate_model_strength_factorial.py --run-root "DO NOT COMMIT/model_strength_factorial_smoke/$stamp"
```

Confirm these files exist:

```powershell
Test-Path "DO NOT COMMIT/model_strength_factorial_smoke/$stamp/all_runs_long.csv"
Test-Path "DO NOT COMMIT/model_strength_factorial_smoke/$stamp/cell_means.csv"
Test-Path "DO NOT COMMIT/model_strength_factorial_smoke/$stamp/variance_decomposition/variance_partition_summary.csv"
Test-Path "DO NOT COMMIT/model_strength_factorial_smoke/$stamp/final_report.md"
```

## Full Paid Campaign

The full campaign writes official artifacts under `runs/cross_family_model_x_evolution_factorial/YYYYMMDD_HHMMSS/`.

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
python run_model_strength_factorial.py --config configs/model_strength_factorial.yaml --timestamp $stamp
python aggregate_model_strength_factorial.py --run-root "runs/cross_family_model_x_evolution_factorial/$stamp"
```

If the campaign is interrupted, rerun the same command with the same `$stamp` and `--skip-existing`:

```powershell
python run_model_strength_factorial.py --config configs/model_strength_factorial.yaml --timestamp $stamp --skip-existing
python aggregate_model_strength_factorial.py --run-root "runs/cross_family_model_x_evolution_factorial/$stamp"
```

## Planned Scale

The committed model tiers are:

- `weak_model`: `gpt-5-nano`
- `medium_model`: `gpt-5.4-nano`
- `strong_model`: `gpt-5.5`

The planned full design produces 750 run rows:

- `simple_games`: `3 models x 5 techniques x 10 seeds = 150` rows.
- `tsp`: `3 models x 5 techniques x 20 seeds = 300` rows.
- `cvrp_phase9_real_world`: `3 models x 5 techniques x 20 seeds = 300` rows.

Candidate-generation budget is 15,990 total candidates:

- `simple_games`: `3 models x 10 seeds x (1 + 4 x 100) = 12,030` candidates.
- `tsp`: `3 models x 20 seeds x (1 + 4 x 8) = 1,980` candidates.
- `cvrp_phase9_real_world`: `3 models x 20 seeds x (1 + 4 x 8) = 1,980` candidates.

This is intentionally expensive because it separates base model tier from search budget and replay technique. Do not interpret replay as useful unless it improves over `budget_matched_no_replay`, not merely over `single_shot`.

## Required Outputs

The aggregator writes:

- `all_runs_long.csv`
- `cell_means.csv`
- `model_strength_table.csv`
- `model_x_evolution_matrices/*.csv`
- `variance_decomposition/task_specific_anova.csv`
- `variance_decomposition/pooled_anova.csv`
- `variance_decomposition/variance_partition_summary.csv`
- `effect_sizes/evolution_vs_single_shot_effects.csv`
- `effect_sizes/evolution_vs_budget_matched_effects.csv`
- `figures/*.png`
- `final_report.md`
- `final_report.pdf`

The final report prints the paths to `final_report.md`, `all_runs_long.csv`, and `variance_partition_summary.csv`, plus the empirical conclusion paragraph.

## Model Score Policy

The committed model scores are ordinal proxies: weak=1, medium=2, strong=3. This is deliberate because comparable public coding-benchmark scores are not reliably available for every project-specific model alias. If you later obtain comparable HumanEval, MBPP, LiveCodeBench, or SWE-bench Verified scores for all three tiers, update `configs/model_strength_factorial.yaml` before launching the official campaign and keep `benchmark_score_source` transparent.
