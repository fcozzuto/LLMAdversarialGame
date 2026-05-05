# Adversarial Curriculum Phase-2 Protocol

This document defines the phase-2 research design built on top of the original adversarial grid framework.

## Goal

The central claim under test is:

> Adversarial pressure does not automatically produce innovation in LLM agents; it often produces churn, loops, or local hill-climbing unless the environment includes memory, repair, opponent diversity, and novelty-aware selection.

## Design Principles

1. Separate training pressure from evaluation pressure.
2. Measure behavior, not only code text.
3. Use reproducible opponent schedules and archives.
4. Treat novelty, looping, and pressure response as heuristic metrics that require qualitative validation.
5. Prefer deterministic summaries over judge-model prose.
6. Replicate every curriculum family across at least three predefined seed offsets before drawing conclusions.
7. Treat the learner policy as the primary unit of analysis in curriculum runs; opponent-role metrics are contextual.

## Curriculum Axes

- `Fixed predator`: evolve one focal agent against a strong frozen opponent.
- `Rotating opponents`: expose the focal agent to a cyclic pool of opponent archetypes.
- `Nemesis archive`: reintroduce previously losing opponents on a schedule.
- `Loss-triggered mutation pressure`: after losses, explicitly demand a substantially different strategy.
- `Novelty-gated selection`: keep a candidate only if it improves score or behavioral diversity within an allowed score tolerance.
- `Holdout evaluation`: evaluate the accepted focal policy against held-out opponents after training.
- `Replay-aware selection`: before accepting a candidate, re-evaluate it against recent nemeses and optional held-out opponents.
- `Elite archive`: keep a MAP-Elites-style archive of accepted focal policies indexed by behavioral cells.

## Stored Signals

Per epoch, the framework should preserve:

- submitted code and executed code
- code fingerprint and strategy tags
- behavioral descriptors
- curriculum opponent label and source
- selection decisions
- archive insertions
- loss-streak and pressure state
- replay-check summaries
- elite-archive coverage and behavior-cell occupancy

## Looping And Plateau Heuristics

- repeated same-code transitions
- failed-fix repetition after non-improving epochs
- A/B/A oscillation between strategy fingerprints
- reversion to earlier fingerprints
- low behavioral change despite high lexical novelty
- no recent score improvement with low recent novelty

## Exploration And Pressure Heuristics

- post-loss novelty spikes
- strategy-class switches
- escape from a losing regime after repeated losses
- same-opponent recovery
- degradation after loss-triggered mutation
- regression against replay opponents
- regression against held-out opponents during acceptance-time spot checks

## Training Vs Evaluation

Curriculum conditions are training conditions. Holdout panels are evaluation conditions. Do not treat a curriculum run as evidence of generalization unless the accepted policy also performs meaningfully on the holdout panel.

Replicate every curriculum family with the fixed seed-offset schedule in [configs/curriculum_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/curriculum_suite/RUNBOOK.md) before drawing claims about stable effects.

Deferred follow-up work on metric validation, stronger held-out evaluation, and broader generalization scope is tracked in [docs/VALIDITY_AND_GENERALIZATION_BACKLOG.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/VALIDITY_AND_GENERALIZATION_BACKLOG.md).

## Reporting

Per-run reports should state:

- whether the condition was curriculum-enabled
- the curriculum mode and opponent source
- loop, oscillation, reversion, and pressure metrics
- archive usage
- holdout-panel outcomes when enabled

Aggregate reports should compare:

- novelty and reliability
- loop pressure
- strategy-switch pressure
- post-loss exploration
- same-opponent adaptation
- replay robustness
- elite-archive coverage
- holdout generalization

## Recommended Reading

- [Curriculum Learning](https://icml.cc/2009/papers/119.pdf)
- [A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning](https://papers.neurips.cc/paper_files/paper/2017/hash/3323fe11e9595c09af38fe67567a9394-Paper.pdf)
- [Open-ended Learning in Symmetric Zero-sum Games](https://proceedings.mlr.press/v97/balduzzi19a.html)
- [Grandmaster level in StarCraft II using multi-agent reinforcement learning](https://www.nature.com/articles/s41586-019-1724-z)
- [Novelty Search and the Problem with Objectives](https://doi.org/10.1007/978-1-4614-1770-5_3)
- [Illuminating search spaces by mapping elites](https://arxiv.org/abs/1504.04909)
- [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560)
