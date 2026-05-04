# Curriculum Suite Runbook

This runbook defines the phase-2 adversarial-curriculum campaign from scratch.

## Purpose

The suite family is designed to test whether adversarial pressure alone drives innovation, or whether it mainly produces loops, local hill-climbing, and brittle counterplay unless the setup adds opponent diversity, memory, repair, and novelty-aware selection.

## Run Order

Run these from [C:\Users\kaaro\Documents\GitHub\LLMAdversarialGame](C:\Users\kaaro\Documents\GitHub\LLMAdversarialGame).

```powershell
python run_suite.py --config configs\curriculum_suite\01_fixed_predator.json
python run_suite.py --config configs\curriculum_suite\02_rotating_opponents.json
python run_suite.py --config configs\curriculum_suite\03_nemesis_archive.json
python run_suite.py --config configs\curriculum_suite\04_loss_triggered_mutation.json
python run_suite.py --config configs\curriculum_suite\05_novelty_gated_selection.json
python run_suite.py --config configs\curriculum_suite\06_holdout_evaluation.json
```

## Aggregate Commands

Aggregate each family separately after you have repeated runs, for example:

```powershell
python aggregate_runs.py --runs-root runs\curriculum_suite\fixed_predator
python aggregate_runs.py --runs-root runs\curriculum_suite\rotating_opponents
python aggregate_runs.py --runs-root runs\curriculum_suite\nemesis_archive
python aggregate_runs.py --runs-root runs\curriculum_suite\loss_triggered_mutation
python aggregate_runs.py --runs-root runs\curriculum_suite\novelty_gated_selection
python aggregate_runs.py --runs-root runs\curriculum_suite\holdout_evaluation
```

## Interpretation Order

1. Fixed predator: does the focal agent escape a single strong adversary, or loop and plateau?
2. Rotating opponents: does opponent diversity produce broader adaptation than fixed-predator training?
3. Nemesis archive: does reintroducing previously losing opponents reduce forgetting?
4. Loss-triggered mutation: does explicit mutation pressure create useful exploration or just churn?
5. Novelty-gated selection: does behavioral diversity improve without score collapse?
6. Holdout evaluation: do the accepted training policies generalize to held-out opponent archetypes?

## Reporting Rules

- Treat deterministic summaries as primary.
- Use judge-model prose as secondary commentary only.
- Use holdout results to support generalization claims, not training-time results alone.
- Use qualitative review of notable epochs before claiming genuine innovation.
