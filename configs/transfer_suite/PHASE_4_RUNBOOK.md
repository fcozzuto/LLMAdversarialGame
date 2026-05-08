# Phase 4 Causal Transfer Runbook

This runbook operationalizes the phase-4 goal: strengthen the causal interpretation of the transfer result before adding new curriculum mechanisms.

For the conceptual protocol, use [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md).

## Step 1: Choose The Paired Recipes

Required comparison:

1. `rotating_opponents_holdout_endpoint`
2. `rotating_plus_nemesis_novelty_replay`

Optional third arm:

3. `rotating_plus_replay_aware_selection`

## Step 2: Generate Phase-4-Labeled Transfer Configs

These commands keep the transfer setup the same while stamping the configs with `study_phase=phase_4` and writing to a separate phase-4 run root.

```powershell
python build_transfer_suite.py --recipe rotating_opponents_holdout_endpoint --study-phase phase_4 --output configs/transfer_suite/phase_4_rotating_opponents_holdout_endpoint.json --output-root runs/phase_4_transfer/rotating_opponents_holdout_endpoint
python build_transfer_suite.py --recipe rotating_plus_nemesis_novelty_replay --study-phase phase_4 --output configs/transfer_suite/phase_4_rotating_plus_nemesis_novelty_replay.json --output-root runs/phase_4_transfer/rotating_plus_nemesis_novelty_replay
python build_transfer_suite.py --recipe rotating_plus_replay_aware_selection --study-phase phase_4 --output configs/transfer_suite/phase_4_rotating_plus_replay_aware_selection.json --output-root runs/phase_4_transfer/rotating_plus_replay_aware_selection
```

Skip the third command if you are not running the optional replay-aware arm.

## Step 3: Run Paired Replicates

Use identical offsets for every recipe.

If you are extending the current five-offset dataset, keep:

- `a`: `0`
- `b`: `1000`
- `c`: `2000`
- `d`: `3000`
- `e`: `4000`

If you want the stronger phase-4 target, add:

- `f`: `5000`
- `g`: `6000`
- `h`: `7000`
- `i`: `8000`
- `j`: `9000`

Example commands for the required two-arm comparison:

```powershell
python run_suite.py --config configs\transfer_suite\phase_4_rotating_opponents_holdout_endpoint.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\transfer_suite\phase_4_rotating_plus_nemesis_novelty_replay.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\transfer_suite\phase_4_rotating_opponents_holdout_endpoint.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\transfer_suite\phase_4_rotating_plus_nemesis_novelty_replay.json --seed-offset 1000 --replicate-label b
```

Continue the same pattern for the remaining offsets. If you include the optional third arm, run it on the same offsets too.

## Step 4: Aggregate Each Recipe Separately

```powershell
python aggregate_runs.py --runs-root runs\phase_4_transfer\rotating_opponents_holdout_endpoint
python aggregate_runs.py --runs-root runs\phase_4_transfer\rotating_plus_nemesis_novelty_replay
python aggregate_runs.py --runs-root runs\phase_4_transfer\rotating_plus_replay_aware_selection
```

Skip the third command if you did not run the optional arm.

## Step 5: Run The Paired Causal Analysis

Required two-arm comparison:

```powershell
python analyze_causal_transfer.py --baseline-recipe rotating_opponents_holdout_endpoint --recipe-root runs\phase_4_transfer\rotating_opponents_holdout_endpoint --recipe-root runs\phase_4_transfer\rotating_plus_nemesis_novelty_replay
```

Optional three-arm comparison:

```powershell
python analyze_causal_transfer.py --baseline-recipe rotating_opponents_holdout_endpoint --recipe-root runs\phase_4_transfer\rotating_opponents_holdout_endpoint --recipe-root runs\phase_4_transfer\rotating_plus_nemesis_novelty_replay --recipe-root runs\phase_4_transfer\rotating_plus_replay_aware_selection
```

The script writes:

- `causal_transfer_summary.json`
- `causal_transfer_report.md`
- `causal_transfer_report.pdf`

## Step 6: Refresh The Novelty Review

After the new paired dataset is in place, rebuild the novelty packet on the relevant phase-4 roots:

```powershell
python review_novelty_spikes.py --runs-root runs\phase_4_transfer\rotating_plus_nemesis_novelty_replay --output-dir runs\phase_4_transfer\novelty_review_heavy
python review_novelty_spikes.py --runs-root runs\phase_4_transfer\rotating_opponents_holdout_endpoint --output-dir runs\phase_4_transfer\novelty_review_baseline
```

## Interpretation Order

1. Per-environment paired transfer result
2. Overall paired transfer average
3. Per-archetype failure modes
4. Behavioral-shift versus code-novelty interpretation
5. Qualitative novelty review

Do not invert this order. The phase-4 question is causal interpretation of the transfer result, not a search for larger novelty numbers.
