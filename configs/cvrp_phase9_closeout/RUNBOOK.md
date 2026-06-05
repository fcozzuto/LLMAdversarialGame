# Phase 9 Closeout Runbook

This runbook covers the bounded closeout study on branch `cvrp-closeout-budget-control`.

The closeout keeps the same bounded `CVRPLIB` Uchoa `X` setup used in phase 9:

- train: `X-n101-k25`, `X-n110-k13`, `X-n125-k30`, `X-n134-k13`, `X-n157-k13`, `X-n214-k11`
- holdout: `X-n176-k26`, `X-n190-k8`, `X-n223-k34`, `X-n247-k50`, `X-n275-k28`

For this bounded `X`-instance phase, feasibility follows the unrestricted-route `CVRP` interpretation used in the DIMACS challenge. The `k` in instance names is logged as contextual metadata, but solutions are not rejected solely for using more than `k` routes.

## Setup

```powershell
git checkout cvrp-closeout-budget-control
conda activate Python3_14
python prepare_cvrp_phase9_benchmarks.py
```

## Smoke Test

```powershell
python run_cvrp_phase9_suite.py --config configs/cvrp_phase9_closeout/smoke_suite.json
python aggregate_cvrp_phase9_runs.py --runs-root "DO NOT COMMIT/phase9_closeout_budget_control_smoke"
```

Smoke artifacts stay under `DO NOT COMMIT/phase9_closeout_budget_control_smoke`.

Aggregation reads every `run_*` directory under the chosen root. If you want an isolated smoke summary instead of a cumulative one, point the smoke config at a fresh root or clear out stale smoke `run_*` directories first.

## Official Suite

The official closeout suite compares:

- nearest-neighbor constructive
- Clarke-Wright savings
- regret-insertion plus local search
- direct generate plus one repair
- budget-matched no replay
- replay solver evolution

Recommended official replication target: `20` paired offsets.

Example PowerShell loop:

```powershell
$replicates = @(
  @{ offset = 0; label = "a" },
  @{ offset = 1000; label = "b" },
  @{ offset = 2000; label = "c" },
  @{ offset = 3000; label = "d" },
  @{ offset = 4000; label = "e" },
  @{ offset = 5000; label = "f" },
  @{ offset = 6000; label = "g" },
  @{ offset = 7000; label = "h" },
  @{ offset = 8000; label = "i" },
  @{ offset = 9000; label = "j" },
  @{ offset = 10000; label = "k" },
  @{ offset = 11000; label = "l" },
  @{ offset = 12000; label = "m" },
  @{ offset = 13000; label = "n" },
  @{ offset = 14000; label = "o" },
  @{ offset = 15000; label = "p" },
  @{ offset = 16000; label = "q" },
  @{ offset = 17000; label = "r" },
  @{ offset = 18000; label = "s" },
  @{ offset = 19000; label = "t" }
)

foreach ($r in $replicates) {
  python run_cvrp_phase9_suite.py --config configs/cvrp_phase9_closeout/01_budget_control.json --seed-offset $r.offset --replicate-label $r.label
}

python aggregate_cvrp_phase9_runs.py --runs-root runs/cvrp_phase9_closeout/budget_control
```

That aggregate command is intentionally cumulative: it combines every official `run_*` directory under `runs/cvrp_phase9_closeout/budget_control`.

## Required Interpretation

Do not claim state-of-the-art performance.

The intended closeout claim shape is narrower:

- direct synthesis, independent budget-matched search, and replay-aware iterative search can now be compared under one frozen validator,
- replay-specific value exists only if the replay arm improves over the budget-matched no-replay arm,
- if direct generate plus one repair dominates, the conclusion should shift toward bounded coding assistance rather than replay-aware autonomy.

For the closeout arms, selection should be interpreted as train-panel feasibility first and train penalized gap second. Runtime remains a reported endpoint, but it is not the primary acceptance criterion for candidate updates.

If you need API spend for budgeting, record it from the provider dashboard or usage export while the official run is in progress. The repository reports technical validity and performance, but it does not convert requests into dollar estimates automatically.

If an official offset crashes or is manually interrupted after creating a partial `run_*` directory, delete that partial run directory before rerunning the same `--seed-offset` and `--replicate-label`. Do not aggregate mixed partial and complete official runs.
