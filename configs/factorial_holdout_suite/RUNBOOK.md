# Factorial Holdout Suite Runbook

This suite implements the supervisor-requested holdout-first factorial ablation in the original resource-collection environment.

## Goal

Compare six curriculum recipes while treating held-out opponent win rate as the primary endpoint:

1. `fixed_predator_holdout_endpoint`
2. `rotating_opponents_holdout_endpoint`
3. `rotating_plus_nemesis_archive`
4. `rotating_plus_novelty_gate`
5. `rotating_plus_replay_aware_selection`
6. `rotating_plus_nemesis_novelty_replay`

Training score remains useful, but the main ranking criterion is held-out opponent win rate after training.

## Replication Target

Use five replicate seed offsets. That yields `6 conditions x 5 replicated suite runs = 30 condition-runs`, which matches the supervisor target of 20-30 seeds.

Recommended labels and offsets:

- `a`: `0`
- `b`: `1000`
- `c`: `2000`
- `d`: `3000`
- `e`: `4000`

## Commands

```powershell
python run_suite.py --config configs\factorial_holdout_suite\01_factorial_holdout.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\factorial_holdout_suite\01_factorial_holdout.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\factorial_holdout_suite\01_factorial_holdout.json --seed-offset 2000 --replicate-label c
python run_suite.py --config configs\factorial_holdout_suite\01_factorial_holdout.json --seed-offset 3000 --replicate-label d
python run_suite.py --config configs\factorial_holdout_suite\01_factorial_holdout.json --seed-offset 4000 --replicate-label e
```

Then aggregate:

```powershell
python aggregate_runs.py --runs-root runs\factorial_holdout_suite
```

## Interpretation Order

1. Rank conditions by held-out win rate first.
2. Use held-out score margin as a secondary endpoint.
3. Use training score only as supporting context.
4. Use novelty, replay robustness, and curriculum metrics to explain why a condition won or lost.
5. Do not treat code novelty alone as innovation until the novelty-review packet confirms real behavioral change.

## Follow-Up

After the aggregate is produced, run the novelty-review tooling on the top novelty spikes before making strong claims about innovation:

```powershell
python review_novelty_spikes.py --runs-root runs\factorial_holdout_suite --output-dir runs\factorial_holdout_suite\novelty_review
```
