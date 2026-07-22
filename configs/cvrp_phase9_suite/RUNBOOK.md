# Phase 9 Runbook

This runbook covers the bounded real-world CVRP solver-evolution phase on branch `real-world-vrp`.

The chosen benchmark family is the official `CVRPLIB` Uchoa `X` set, using a moderate-size curated subset so the study stays feasible while still testing true capacity-feasible solver synthesis. The committed subset includes both two-cluster and grid-like regimes under the project descriptor basis, rather than only one geometric mode.

For this bounded `X`-instance phase, feasibility follows the unrestricted-route CVRP interpretation used in the DIMACS CVRP challenge. The `k` in instance names is logged as contextual metadata, but solutions are not rejected solely for using more than `k` routes.

The committed split is:

- train: `X-n101-k25`, `X-n110-k13`, `X-n125-k30`, `X-n134-k13`, `X-n157-k13`, `X-n214-k11`
- holdout: `X-n176-k26`, `X-n190-k8`, `X-n223-k34`, `X-n247-k50`, `X-n275-k28`

## Setup

```powershell
git checkout real-world-vrp
conda activate Python3_14
python prepare_cvrp_phase9_benchmarks.py
```

## Smoke Test

```powershell
python run_cvrp_phase9_suite.py --config configs/cvrp_phase9_suite/smoke_suite.json
python aggregate_cvrp_phase9_runs.py --runs-root "DO NOT COMMIT/cvrp_phase9_suite/smoke"
```

Smoke artifacts stay under `DO NOT COMMIT/cvrp_phase9_suite/smoke`.

## Official Suite

The bounded official suite compares:

- nearest-neighbor constructive
- Clarke-Wright savings
- regret-insertion plus local search
- full solver-code evolution

Recommended official replication target: `20` paired offsets.

If you want a quicker pilot before the full campaign, use `10` paired offsets and then extend to `20` without changing the config or benchmark pack.

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
  python run_cvrp_phase9_suite.py --config configs/cvrp_phase9_suite/01_solver_evolution.json --seed-offset $r.offset --replicate-label $r.label
}

python aggregate_cvrp_phase9_runs.py --runs-root runs/cvrp_phase9_suite/solver_evolution
```

## Optional External Reference

`OR-Tools` is not required for the bounded default suite, because it is not bundled in the current environment and the main phase-9 claim does not depend on it.

If you later install `OR-Tools`, it can be added as an auxiliary external reference condition rather than a core dependency.

## Required Interpretation

Do not claim state-of-the-art performance.

The intended phase-9 claim shape is narrower:

- feasibility improves over epochs
- objective gap improves over naive baselines
- held-out robustness remains acceptable across derived instance families
- the generated solver logic is interpretable enough to inspect as constructive, repair, local-search, or restart behavior

If an official offset crashes or is manually interrupted after creating a partial `run_*` directory, delete that partial run directory before rerunning the same `--seed-offset` and `--replicate-label`. Do not aggregate mixed partial and complete official runs.

If a generated solver times out on an instance, the runner now records that as a failed candidate evaluation with a penalized gap instead of aborting the whole suite run.

The official phase-9 config now separates:

- `generation.llm_timeout_seconds` for learner API calls
- `generation.solver_timeout_seconds` for sandboxed solver execution

The official bounded suite also uses a slightly looser code budget than the earliest draft, because real CVRP whole-solver logic needs more room than the earlier toy and TSP operator phases. The prompt remains mutation-oriented and still favors compact, local edits over unconstrained rewrites.

The current official solver-worker timeout is `60` seconds per instance. This value is above observed baseline and preflight runtimes, but lower than the earlier loose setting, so pathological candidates are penalized without stalling the full campaign for long periods.
