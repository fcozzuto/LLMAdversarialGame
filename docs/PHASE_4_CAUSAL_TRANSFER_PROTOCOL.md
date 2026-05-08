# Phase 4 Causal Transfer Protocol

This document defines the next study phase after the initial transfer result.

The goal is not to add another curriculum mechanism yet. The goal is to strengthen the causal interpretation of the transfer result already on the table.

## Central Hypothesis

The current transfer signal supports a narrower and more defensible hypothesis than "the learner became generally smarter":

> Transfer improvements may come more from broader adaptive coverage and replay-conditioned robustness than from explicit strategic innovation.

That hypothesis should now be tested directly.

## Research Basis

This phase follows standard best practice from reproducible reinforcement learning, transfer evaluation, novelty search, and open-ended learning:

- [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560): use replication, paired comparisons, and uncertainty instead of single-seed narratives.
- [A Study on Overfitting in Deep Reinforcement Learning](https://research.google/pubs/a-study-on-overfitting-in-deep-reinforcement-learning/): keep training success separate from held-out evaluation and do not infer robustness from in-training performance alone.
- [Measuring Sample Efficiency and Generalization in RL with Procgen](https://openreview.net/forum?id=rylKB3A9Fm): report transfer per environment and avoid collapsing distinct generalization regimes into one score too early.
- [Open-ended Learning in Symmetric Zero-sum Games](https://proceedings.mlr.press/v97/balduzzi19a.html): opponent diversity and memory can improve adaptation without implying universal competence.
- [Novelty Search and the Problem with Objectives](https://doi.org/10.1007/978-1-4614-1770-5_3): novelty can be useful, but it should not be confused with objective progress or true innovation.
- [Illuminating Search Spaces by Mapping Elites](https://arxiv.org/abs/1504.04909): behavior-space coverage is a meaningful analysis axis when studying diverse adaptive repertoires.

## Phase 4 Questions

1. Does the curriculum-heavy recipe still beat the rotating-opponent baseline under larger paired-seed transfer replication?
2. Which holdout opponent archetypes transfer well, and which remain persistent weaknesses?
3. Do behavioral shifts predict transfer better than raw lexical code-change magnitude?
4. Is the transfer story better described as stable functional adaptation plus reduced churn than as high novelty alone?

## Required Comparisons

The default paired comparison is:

1. `rotating_opponents_holdout_endpoint`
2. `rotating_plus_nemesis_novelty_replay`

Optional third comparison:

3. `rotating_plus_replay_aware_selection`

Use identical seed offsets, identical transfer environments, and identical holdout panels for every compared recipe.
When generating baseline-relative causal reports, make the baseline recipe explicit in the analysis command rather than relying on argument order.

## Endpoints

Primary endpoint:

- held-out win rate within each transfer environment

Secondary endpoint:

- held-out score margin within each transfer environment

Exploratory interpretation metrics:

- per-archetype holdout win rate and score margin
- mean behavioral-descriptor shift across epochs
- functional-adaptation ratio: behavioral shift per unit of code novelty
- strategy-switch rate
- superficial-novelty rate
- novelty-review packet for the strongest spikes and the most relevant failure cases

## Design

### 1. Reliability And Replication

- Use paired seed offsets across recipes.
- Treat the paired recipe difference as the main statistical unit, not the raw pooled mean alone.
- Keep the transfer environments separate in the report:
  - resource collection / denial
  - pursuit / evasion
  - territory control
- Aggregate an overall transfer average only after the per-environment results are shown.

Recommended replication target:

- minimum: 5 paired offsets if you are extending the already completed dataset
- preferred: 10 paired offsets total for the main baseline-versus-heavy comparison if budget allows

### 2. Failure-Mode Analysis

The main paper angle is likely uneven robustness, not universal skill.

For each environment, report every holdout opponent separately and name the persistent weak cases directly.

Current scientifically useful examples include:

- `evasion_midline_dodge`
- `safe_collector`
- `center_rush`
- `corner_guard`

These weaknesses should stay visible in the reporting even when the aggregate transfer result is positive.

### 3. Behavioral Interpretation Beyond Code Novelty

This phase should explicitly separate:

- syntactic novelty
- functional adaptation

Use the following interpretation ladder:

1. Correlate code novelty with behavioral-descriptor shift.
2. Correlate behavioral-descriptor shift with transfer performance.
3. Compare raw code novelty against behavior-centered proxies:
   - mean behavioral shift
   - functional-adaptation ratio
   - strategy-switch rate
   - superficial-novelty rate

Operational rule:

- If lexical novelty rises but behavioral shift does not, treat the change as likely churn.
- If behavioral shift rises and transfer improves while churn indicators fall, treat that as stronger evidence for functional adaptation.

## Required Artifacts

- per-recipe aggregate report from [aggregate_runs.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/aggregate_runs.py)
- paired causal-transfer report from [analyze_causal_transfer.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/analyze_causal_transfer.py)
- novelty-review packet from [review_novelty_spikes.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/review_novelty_spikes.py)
- short qualitative appendix with:
  - one strong transfer gain
  - one improved but still weak archetype
  - one persistent failure case

## Interpretation Rules

- Do not add new curriculum mechanisms until the paired transfer replication is stable enough to interpret.
- Do not claim general intelligence, broad strategic invention, or universal robustness from these results.
- Do not treat lexical code novelty as innovation without behavioral and qualitative support.
- If the heavy recipe wins mainly by reducing failures against some archetypes while remaining weak on others, describe the result as targeted robustness or broader adaptive coverage.
- If behavior-centered proxies track transfer better than raw code novelty, make that distinction central in the thesis framing.

## Operational Entry Point

Use [configs/transfer_suite/PHASE_4_RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/PHASE_4_RUNBOOK.md) for the concrete commands.
