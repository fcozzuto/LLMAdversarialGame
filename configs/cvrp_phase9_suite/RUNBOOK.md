# Phase 9 Runbook

This runbook covers the bounded real-world CVRP solver-evolution phase on branch `real-world-vrp`.

The chosen benchmark family is the official `CVRPLIB` Uchoa `X` set, using a moderate-size curated subset so the study stays feasible while still testing true capacity-feasible solver synthesis. The committed subset includes both two-cluster and grid-like regimes under the project descriptor basis, rather than only one geometric mode.

For this bounded `X`-instance phase, feasibility follows the unrestricted-route CVRP interpretation used in the DIMACS CVRP challenge. The `k` in instance names is logged as contextual metadata, but solutions are not rejected solely for using more than `k` routes.

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
  @{ offset = 9000; label = "j" }
)

foreach ($r in $replicates) {
  python run_cvrp_phase9_suite.py --config configs/cvrp_phase9_suite/01_solver_evolution.json --seed-offset $r.offset --replicate-label $r.label
}

python aggregate_cvrp_phase9_runs.py --runs-root runs/cvrp_phase9_suite/solver_evolution
```

## Optional External Reference

`OR-Tools` is deliberately not required for the bounded default suite, because it is not bundled in the current environment and the main phase-9 claim does not depend on it.

If you later install `OR-Tools`, it can be added as an auxiliary external reference condition rather than a core dependency.

## Required Interpretation

Do not claim state-of-the-art performance.

The intended phase-9 claim shape is narrower:

- feasibility improves over epochs
- objective gap improves over naive baselines
- held-out robustness remains acceptable across derived instance families
- the generated solver logic is interpretable enough to inspect as constructive, repair, local-search, or restart behavior
