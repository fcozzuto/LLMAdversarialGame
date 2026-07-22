# Phase 6 TSP Replay Mechanism Runbook

This runbook covers the focused mechanism follow-up after the first routing archive.

The scientific target is narrower than phase 5:

- explain why `random_replay` beat `failure_replay` on symmetric TSPLIB TSP
- separate broad replay coverage from raw failure severity
- test whether residual-failure replay and compression change that conclusion

## 1. Prepare The Benchmark Pack

Activate the environment first:

```powershell
conda activate Python3_14
```

```powershell
python prepare_tsp_benchmarks.py
```

That refreshes [benchmarks/tsp/manifest.json](../../benchmarks/tsp/manifest.json) with descriptor payloads for the official TSPLIB and synthetic TSP instances.

## 2. Offline Smoke Test

```powershell
python run_tsp_suite.py --config configs/tsp_phase6_suite/smoke_suite.json --skip-judge
```

Use this first whenever you change descriptor extraction, residual-difficulty logic, replay selection, or the phase-6 aggregate code.
The smoke suite writes into `DO NOT COMMIT/tsp_phase6_suite/smoke`.

## 3. Main Phase-6 Suite

```powershell
python run_tsp_suite.py --config configs/tsp_phase6_suite/01_replay_mechanism.json
```

The nine official conditions are:

- `phase6_no_replay`
- `phase6_random_replay`
- `phase6_failure_replay`
- `phase6_random_replay_compression`
- `phase6_stratified_random_replay`
- `phase6_diversity_weighted_replay`
- `phase6_residual_failure_replay`
- `phase6_diversity_failure_replay`
- `phase6_diversity_failure_replay_compression`

Primary interpretation targets:

- final held-out TSPLIB optimality gap
- final synthetic holdout gap
- replay archive descriptor diversity
- replay archive hardness

Key secondary diagnostics:

- archive size bias
- replay failure concentration
- accepted code novelty
- heuristic complexity
- adaptation efficiency

## 4. Replication

Use paired seed offsets exactly as in earlier phases:

```powershell
python run_tsp_suite.py --config configs/tsp_phase6_suite/01_replay_mechanism.json --seed-offset 1000 --replicate-label b
```

Official target:

- 20 paired offsets using the fixed list `0, 1000, 2000, ..., 19000`

## 5. Aggregation

```powershell
python aggregate_tsp_phase6_runs.py --runs-root runs/tsp_phase6_suite/replay_mechanism
```

That writes:

- `aggregate_summary.json`
- `aggregate_report.md`
- `aggregate_report.pdf`
- `archive_diversity_vs_tsplib_gap.svg/png`
- `archive_hardness_vs_tsplib_gap.svg/png`

## 6. Interpretation Rules

- Treat this as a mechanism study, not as a new solver benchmark race.
- The main comparison is not only replay versus no replay. It is broad-coverage replay versus raw-failure replay versus residual-failure replay.
- If archive diversity predicts held-out transfer more strongly than archive hardness, say that directly and scope the claim to this TSP benchmark family.
- `random_replay_compression` matters because it tests compression on the replay arm that actually won phase 5.
- Do not call residual replay a success unless it improves held-out transfer or clearly sharpens the diversity-versus-hardness explanation.
