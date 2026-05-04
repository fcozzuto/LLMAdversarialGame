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

## Curriculum Axes

- `Fixed predator`: evolve one focal agent against a strong frozen opponent.
- `Rotating opponents`: expose the focal agent to a cyclic pool of opponent archetypes.
- `Nemesis archive`: reintroduce previously losing opponents on a schedule.
- `Loss-triggered mutation pressure`: after losses, explicitly demand a substantially different strategy.
- `Novelty-gated selection`: keep a candidate only if it improves score or behavioral diversity within an allowed score tolerance.
- `Holdout evaluation`: evaluate the accepted focal policy against held-out opponents after training.

## Stored Signals

Per epoch, the framework should preserve:

- submitted code and executed code
- code fingerprint and strategy tags
- behavioral descriptors
- curriculum opponent label and source
- selection decisions
- archive insertions
- loss-streak and pressure state

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

## Training Vs Evaluation

Curriculum conditions are training conditions. Holdout panels are evaluation conditions. Do not treat a curriculum run as evidence of generalization unless the accepted policy also performs meaningfully on the holdout panel.

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

## Recommended Reading

- Curriculum Learning (Bengio et al., 2009)
- Open-ended Learning in Symmetric Zero-sum Games (Balduzzi et al., 2019)
- AlphaStar league training (Vinyals et al., 2019)
- Novelty Search and MAP-Elites
- Deep RL That Matters
