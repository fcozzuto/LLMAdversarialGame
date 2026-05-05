# Curriculum Suite Runbook

This runbook defines the updated adversarial-curriculum campaign.

## Purpose

The curriculum suite is now organized around three research goals:

1. Improve the scientific validity of the results by using replicated runs, learner-centric reporting, stronger holdout evaluation, and qualitative follow-up hooks.
2. Improve actual policy quality by making rotating-opponent pressure, nemesis replay, and novelty-aware selection the main training line.
3. Treat loss-triggered mutation pressure as an auxiliary ablation, not as the default mechanism for improvement.

This design follows standard best practices from curriculum learning, multi-agent generalization, quality-diversity search, and reproducible reinforcement-learning evaluation:

- [Curriculum Learning](https://icml.cc/2009/papers/119.pdf)
- [A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning](https://papers.neurips.cc/paper_files/paper/2017/hash/3323fe11e9595c09af38fe67567a9394-Paper.pdf)
- [Open-ended Learning in Symmetric Zero-sum Games](https://proceedings.mlr.press/v97/balduzzi19a.html)
- [Grandmaster level in StarCraft II using multi-agent reinforcement learning](https://www.nature.com/articles/s41586-019-1724-z)
- [Novelty Search and the Problem with Objectives](https://doi.org/10.1007/978-1-4614-1770-5_3)
- [Illuminating search spaces by mapping elites](https://arxiv.org/abs/1504.04909)
- [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560)

## Replication Rule

Run every suite family three times with predefined seed offsets. This gives you three replicated runs without maintaining eighteen nearly identical config files.

- replicate `a`: `--seed-offset 0 --replicate-label a`
- replicate `b`: `--seed-offset 1000 --replicate-label b`
- replicate `c`: `--seed-offset 2000 --replicate-label c`

## Recommended Execution Order

Run these from [C:\Users\kaaro\Documents\GitHub\LLMAdversarialGame](C:\Users\kaaro\Documents\GitHub\LLMAdversarialGame).

### Fixed Predator

```powershell
python run_suite.py --config configs\curriculum_suite\01_fixed_predator.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\01_fixed_predator.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\01_fixed_predator.json --seed-offset 2000 --replicate-label c
```

### Rotating Opponents

```powershell
python run_suite.py --config configs\curriculum_suite\02_rotating_opponents.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\02_rotating_opponents.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\02_rotating_opponents.json --seed-offset 2000 --replicate-label c
```

### Loss-Triggered Mutation

```powershell
python run_suite.py --config configs\curriculum_suite\04_loss_triggered_mutation.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\04_loss_triggered_mutation.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\04_loss_triggered_mutation.json --seed-offset 2000 --replicate-label c
```

### Nemesis Archive

```powershell
python run_suite.py --config configs\curriculum_suite\03_nemesis_archive.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\03_nemesis_archive.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\03_nemesis_archive.json --seed-offset 2000 --replicate-label c
```

### Novelty-Gated Selection

```powershell
python run_suite.py --config configs\curriculum_suite\05_novelty_gated_selection.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\05_novelty_gated_selection.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\05_novelty_gated_selection.json --seed-offset 2000 --replicate-label c
```

### Holdout Evaluation

```powershell
python run_suite.py --config configs\curriculum_suite\06_holdout_evaluation.json --seed-offset 0 --replicate-label a
python run_suite.py --config configs\curriculum_suite\06_holdout_evaluation.json --seed-offset 1000 --replicate-label b
python run_suite.py --config configs\curriculum_suite\06_holdout_evaluation.json --seed-offset 2000 --replicate-label c
```

## Aggregate Commands

Aggregate each family after the three replicated runs complete.

```powershell
python aggregate_runs.py --runs-root runs\curriculum_suite\fixed_predator
python aggregate_runs.py --runs-root runs\curriculum_suite\rotating_opponents
python aggregate_runs.py --runs-root runs\curriculum_suite\loss_triggered_mutation
python aggregate_runs.py --runs-root runs\curriculum_suite\nemesis_archive
python aggregate_runs.py --runs-root runs\curriculum_suite\novelty_gated_selection
python aggregate_runs.py --runs-root runs\curriculum_suite\holdout_evaluation
```

## Interpretation Order

1. Fixed predator: does the learner escape or does it stay trapped in the same niche?
2. Rotating opponents: does opponent diversity increase behavior-cell coverage and improve score without collapsing reliability?
3. Loss-triggered mutation: does extra mutation pressure help beyond the replay-aware novelty gate, or mostly add churn?
4. Nemesis archive: does replay against recent nemeses improve robustness and reduce forgetting?
5. Novelty-gated selection: does elite-aware acceptance filter churn while keeping or improving performance?
6. Holdout evaluation: do the accepted training policies generalize to genuinely unseen archetypes?

## Reporting Rules

- Treat deterministic summaries as primary evidence.
- Treat judge-model prose as secondary commentary only.
- In curriculum families, treat the learner as the main unit of analysis. Opponent-role metrics are contextual, not headline evidence.
- Use holdout results to support generalization claims. Training-time improvement alone is not enough.
- Use the suggested qualitative follow-up epochs in the reports before calling a behavior genuinely innovative.
