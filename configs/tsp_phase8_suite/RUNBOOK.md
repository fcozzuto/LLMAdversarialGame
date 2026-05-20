# Phase 8 Runbook

Use this runbook for the adaptive heuristic portfolio phase after activating the shared environment:

```powershell
conda activate Python3_14
```

## Preparation

Refresh the TSP benchmark manifest so the phase-6 descriptors and the phase-8 validation families are available:

```powershell
python prepare_tsp_benchmarks.py
```

## Smoke

Smoke outputs stay under `DO NOT COMMIT`:

```powershell
python run_tsp_phase8_suite.py --config configs/tsp_phase8_suite/smoke_suite.json --skip-judge
python aggregate_tsp_phase8_runs.py --runs-root "DO NOT COMMIT/tsp_phase8_suite/smoke"
```

## Official Campaign

The recommended official campaign uses 20 paired offsets across all conditions.

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

python prepare_tsp_benchmarks.py
foreach ($r in $replicates) {
  python run_tsp_phase8_suite.py --config configs/tsp_phase8_suite/01_adaptive_portfolio.json --seed-offset $r.offset --replicate-label $r.label
}
python aggregate_tsp_phase8_runs.py --runs-root runs/tsp_phase8_suite/adaptive_portfolio
```

## Outputs

Each run writes:

- `suite_summary.json`
- `run_metadata.json`
- `report.md`
- `report.pdf`
- `condition_summary.json` for each condition

Adaptive-controller conditions additionally write:

- `training_gap.svg/png`
- `transfer_gap.svg/png`
- per-epoch controller artifacts under `epochs/`

The aggregate pass writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
