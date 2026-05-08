# Cross-Environment Transfer Runbook

This runbook covers supervisor request 3: test whether the best curriculum recipe transfers beyond the original resource-collection environment.

If you already have an initial transfer signal and want the follow-on paired replication plus causal-interpretation phase, use [configs/transfer_suite/PHASE_4_RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/PHASE_4_RUNBOOK.md) instead.

## Step 1: Choose the Best Factorial Recipe

Use the factorial holdout aggregate to pick the winning recipe by the primary endpoint:

- highest held-out win rate
- then highest held-out score margin
- then cleaner reliability if the top conditions are close

## Step 2: Generate the Transfer Suite

Build the environment-transfer suite from the chosen transfer condition:

```powershell
python build_transfer_suite.py --recipe rotating_plus_nemesis_novelty_replay
```

Replace `rotating_plus_nemesis_novelty_replay` with the actual chosen condition name if you decide to carry forward a different one.

By default, the generator now writes a recipe-specific config and run root so multiple transfer candidates do not overwrite or mix together. For example:

```text
configs/transfer_suite/rotating_plus_nemesis_novelty_replay.json
runs/transfer_suite/rotating_plus_nemesis_novelty_replay
```

If you also want to compare the simpler rotating-opponent reference condition, build it separately:

```powershell
python build_transfer_suite.py --recipe rotating_opponents_holdout_endpoint
```

That creates:

```text
configs/transfer_suite/rotating_opponents_holdout_endpoint.json
runs/transfer_suite/rotating_opponents_holdout_endpoint
```

It creates three transfer conditions:

1. `transfer_resource_collection_denial`
2. `transfer_pursuit_evasion`
3. `transfer_territory_control`

## Step 3: Run Replicates

Use five replicate seed offsets:

- `a`: `0`
- `b`: `1000`
- `c`: `2000`
- `d`: `3000`
- `e`: `4000`

```powershell
python run_suite.py --config configs\transfer_suite\rotating_plus_nemesis_novelty_replay.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\transfer_suite\rotating_plus_nemesis_novelty_replay.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\transfer_suite\rotating_plus_nemesis_novelty_replay.json --seed-offset 2000 --replicate-label c
python run_suite.py --config configs\transfer_suite\rotating_plus_nemesis_novelty_replay.json --seed-offset 3000 --replicate-label d
python run_suite.py --config configs\transfer_suite\rotating_plus_nemesis_novelty_replay.json --seed-offset 4000 --replicate-label e
```

If you run the rotating-opponents reference condition as well, use its own config path in the same pattern.

## Step 4: Aggregate

```powershell
python aggregate_runs.py --runs-root runs\transfer_suite\rotating_plus_nemesis_novelty_replay
```

If you also run `rotating_opponents_holdout_endpoint`, aggregate it separately from its own run root.

## Interpretation

The main question is whether the same curriculum recipe still improves held-out win rate across multiple games, not just in the original benchmark.

Interpretation order:

1. held-out win rate within each environment
2. held-out score margin within each environment
3. whether the rank order of curriculum behaviors stays stable across environments
4. novelty-review packet for the strongest and weakest transfer cases
