# Phase 5 TSP Runbook

This runbook covers the benchmark-transfer phase that moves the replay-aware curriculum study onto a real combinatorial-optimization family.

## 1. Prepare The Benchmark Pack

Activate the environment first:

```powershell
conda activate Python3_14
```

```powershell
python prepare_tsp_benchmarks.py
```

That downloads the selected TSPLIB95 EUC_2D subset, computes best-known tour costs from the official `.opt.tour` files, and writes [benchmarks/tsp/manifest.json](../../benchmarks/tsp/manifest.json).

## 2. Offline Smoke Test

```powershell
python run_tsp_suite.py --config configs/tsp_suite/smoke_suite.json --skip-judge
```

Use this first whenever you change the TSP engine, benchmark loader, or replay-selection logic.
The smoke suite writes into `DO NOT COMMIT/tsp_suite/smoke` because it is a verification artifact, not an official experiment run.

## 3. Main Phase-5 Suite

```powershell
python run_tsp_suite.py --config configs/tsp_suite/01_replay_transfer.json
```

The four default conditions are:

- `tsplib_no_replay`
- `tsplib_random_replay`
- `tsplib_failure_replay`
- `tsplib_failure_replay_compression`

Primary interpretation target:

- final held-out TSPLIB optimality gap

Secondary targets:

- final synthetic holdout gap
- combined transfer gap
- code novelty
- heuristic complexity
- adaptation efficiency

Selection-time transfer probes combine held-out TSPLIB probe instances with the adversarial geometric layout pool. The exact synthetic holdouts remain reserved for final evaluation.

## 4. Replication

Use paired seed offsets exactly as in the earlier grid phases:

```powershell
python run_tsp_suite.py --config configs/tsp_suite/01_replay_transfer.json --seed-offset 1000 --replicate-label b
```

Recommended minimum:

- 10 paired offsets for an official result

Official main-study target:

- 20 paired offsets using the fixed offset list `0, 1000, 2000, ..., 19000`
- Use the same offset list for every condition and every routing family so the paired comparisons remain valid.

## 5. Aggregation

```powershell
python aggregate_tsp_runs.py --runs-root runs/tsp_suite/replay_transfer
```

That writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
- paired bootstrap comparison tables for the replay conditions

## 6. Interpretation Rules

- Do not treat replay probes or transfer probes inside training as the final evidence; final held-out evaluation remains the endpoint.
- Do not treat code novelty as algorithmic invention without corresponding transfer improvements.
- The compression-aware replay condition matters only if it matches or improves transfer while reducing novelty or complexity growth.
