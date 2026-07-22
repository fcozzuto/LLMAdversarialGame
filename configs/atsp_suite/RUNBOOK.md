# Phase 5B ATSP Runbook

This runbook extends the replay-aware benchmark-transfer study from symmetric TSPLIB TSP to asymmetric TSPLIB ATSP instances.

## 1. Prepare The Benchmark Pack

Activate the environment first:

```powershell
conda activate Python3_14
```

```powershell
python prepare_atsp_benchmarks.py
```

That downloads the selected TSPLIB95 ATSP subset, assigns official best-known costs, and writes [benchmarks/atsp/manifest.json](../../benchmarks/atsp/manifest.json).

## 2. Offline Smoke Test

```powershell
python run_atsp_suite.py --config configs/atsp_suite/smoke_suite.json --skip-judge
```

Use this after changes to the ATSP engine, benchmark loader, or replay-selection logic. The smoke suite writes into `DO NOT COMMIT/atsp_suite/smoke` because it is a verification artifact, not an official experiment run.

## 3. Main ATSP Extension Suite

```powershell
python run_atsp_suite.py --config configs/atsp_suite/01_replay_transfer.json
```

The four default conditions are:

- `atsp_no_replay`
- `atsp_random_replay`
- `atsp_failure_replay`
- `atsp_failure_replay_compression`

Primary interpretation target:

- final held-out TSPLIB ATSP optimality gap

Secondary targets:

- final synthetic holdout gap
- combined transfer gap
- code novelty
- heuristic complexity
- adaptation efficiency

Selection-time transfer probes combine held-out TSPLIB ATSP probe instances with the adversarial asymmetric layout pool. The exact synthetic holdouts remain reserved for final evaluation.

## 4. Replication

```powershell
python run_atsp_suite.py --config configs/atsp_suite/01_replay_transfer.json --seed-offset 1000 --replicate-label b
```

Recommended minimum:

- 10 paired offsets for an official result

Official main-study target:

- 20 paired offsets using the fixed offset list `0, 1000, 2000, ..., 19000`
- Use the same offset list for every condition and every routing family so the paired comparisons remain valid.

## 5. Aggregation

```powershell
python aggregate_atsp_runs.py --runs-root runs/atsp_suite/replay_transfer
```

That writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
- paired bootstrap comparison tables for the replay conditions
