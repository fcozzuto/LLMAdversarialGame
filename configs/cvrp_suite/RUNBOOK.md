# Phase 5C CVRP Runbook

This runbook extends the replay-aware benchmark-transfer study from TSP/ATSP to real vehicle-routing benchmarks from CVRPLIB.

## 1. Prepare The Benchmark Pack

Activate the environment first:

```powershell
conda activate Python3_14
```

```powershell
python prepare_cvrp_benchmarks.py
```

That downloads the selected CVRPLIB subset, verifies official solution files against recomputed route cost, and writes [benchmarks/cvrp/manifest.json](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/benchmarks/cvrp/manifest.json).

## 2. Offline Smoke Test

```powershell
python run_cvrp_suite.py --config configs/cvrp_suite/smoke_suite.json --skip-judge
```

Use this after changes to the CVRP engine, benchmark loader, or replay-selection logic. The smoke suite writes into `DO NOT COMMIT/cvrp_suite/smoke` because it is a verification artifact, not an official experiment run.

## 3. Main CVRP Extension Suite

```powershell
python run_cvrp_suite.py --config configs/cvrp_suite/01_replay_transfer.json
```

The four default conditions are:

- `cvrp_no_replay`
- `cvrp_random_replay`
- `cvrp_failure_replay`
- `cvrp_failure_replay_compression`

Primary interpretation target:

- final held-out CVRPLIB optimality gap

Secondary targets:

- final synthetic holdout gap
- combined transfer gap
- code novelty
- heuristic complexity
- adaptation efficiency

Selection-time transfer probes combine held-out CVRPLIB probe instances with the adversarial routing layout pool. The exact synthetic holdouts remain reserved for final evaluation.

## 4. Replication

```powershell
python run_cvrp_suite.py --config configs/cvrp_suite/01_replay_transfer.json --seed-offset 1000 --replicate-label b
```

Recommended minimum:

- 10 paired offsets for an official result

Official main-study target:

- 20 paired offsets using the fixed offset list `0, 1000, 2000, ..., 19000`
- Use the same offset list for every condition and every routing family so the paired comparisons remain valid.

## 5. Aggregation

```powershell
python aggregate_cvrp_runs.py --runs-root runs/cvrp_suite/replay_transfer
```

That writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
- paired bootstrap comparison tables for the replay conditions
