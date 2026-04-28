# Full Research Suite Runbook

This runbook executes the full stricter research plan from scratch.

It covers:

1. `3` repeated core-suite runs
2. `3` repeated ablation-suite runs
3. `1` controls run
4. `1` cheating-opportunity run
5. aggregate report generation

Total from scratch: `3800` epochs.

## Preparation

Install the required Python packages into the interpreter you plan to use:

```powershell
python -m pip install -r requirements.txt
```

Each `run_suite.py` execution prints a final line of the form:

```text
Completed suite. Results written to: <run_dir>
```

Record that `<run_dir>` value after every step. You will need those paths for the aggregate commands at the end.

## Execute The Suite

Run these commands in order.

### 1. Core Suite A

```powershell
python run_suite.py --config configs\full_suite\01_core_a.json
```

### 2. Core Suite B

```powershell
python run_suite.py --config configs\full_suite\02_core_b.json
```

### 3. Core Suite C

```powershell
python run_suite.py --config configs\full_suite\03_core_c.json
```

### 4. Ablation Suite A

```powershell
python run_suite.py --config configs\full_suite\04_ablations_a.json
```

### 5. Ablation Suite B

```powershell
python run_suite.py --config configs\full_suite\05_ablations_b.json
```

### 6. Ablation Suite C

```powershell
python run_suite.py --config configs\full_suite\06_ablations_c.json
```

### 7. Controls Suite

```powershell
python run_suite.py --config configs\full_suite\07_controls.json
```

### 8. Cheating-Opportunity Suite

```powershell
python run_suite.py --config configs\full_suite\08_cheating_opportunity.json
```

## Aggregate Reports

Replace the placeholder run directories below with the actual `run_...` directories printed by the suite commands.

### Core Aggregate

```powershell
python aggregate_runs.py --run-dir <core_run_a_dir> --run-dir <core_run_b_dir> --run-dir <core_run_c_dir> --output-dir runs\aggregate_full_suite_core
```

### Ablation Aggregate

```powershell
python aggregate_runs.py --run-dir <ablation_run_a_dir> --run-dir <ablation_run_b_dir> --run-dir <ablation_run_c_dir> --output-dir runs\aggregate_full_suite_ablations
```

### Full-Campaign Aggregate

This report is useful for a campaign-level artifact inventory, but causal interpretation should still rely mainly on the separate core and ablation aggregates.

```powershell
python aggregate_runs.py --run-dir <core_run_a_dir> --run-dir <core_run_b_dir> --run-dir <core_run_c_dir> --run-dir <ablation_run_a_dir> --run-dir <ablation_run_b_dir> --run-dir <ablation_run_c_dir> --run-dir <controls_run_dir> --run-dir <cheating_run_dir> --output-dir runs\aggregate_full_suite_all
```

If you reuse a run, substitute it for its correspondent suite config. E.g., `<core_run_X_dir>`.

## Produced Artifacts

Each run writes:

- `suite_summary.json`
- `run_metadata.json`
- `report.md`
- `report.pdf`
- per-condition `scores.svg`
- per-condition `scores.png`

Each aggregate command writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
- aggregate chart PNGs
