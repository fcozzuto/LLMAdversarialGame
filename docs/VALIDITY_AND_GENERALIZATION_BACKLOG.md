# Deferred Validity And Generalization Backlog

This document tracks the research-limit reductions that are still worth doing after the project is stable and the current curriculum results are acceptable.

It is intentionally separate from [RESEARCH_CHECKLIST.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/RESEARCH_CHECKLIST.md). The checklist defines the minimum evidence bar for the active study. This document covers the harder follow-up work needed to make the claims narrower, stronger, and easier to defend under review.

## How To Use This Backlog

- Treat these items as deferred work, not blockers for the current rerun campaign.
- Keep the corresponding threats-to-validity language in the reports until the relevant checklist is completed.
- When a section is completed, update both this document and the report wording that depends on it.

## 1. Validate Behavioral Heuristics

Goal: show that the project metrics for looping, plateauing, exploration, and pressure response track meaningful behavior rather than arbitrary proxy movement.

- [ ] Create a labeling rubric for `looping`, `plateauing`, `exploration spike`, `same-opponent recovery`, `overfitting`, and `degradation`.
- [ ] Sample a stratified set of epochs across curriculum families, replicates, and outcomes.
- [ ] Produce a blinded annotation packet so human reviewers do not see the condition name or hypothesis.
- [ ] Have at least two annotators label the packet independently.
- [ ] Measure inter-annotator agreement.
- [ ] Compare automated metrics against the human labels.
- [ ] Revise or rename metrics that do not align well with the annotations.
- [ ] Add a report section summarizing metric-validation results.

Why this matters:
- Current curriculum metrics are still heuristic operationalizations.
- Reviewers will reasonably ask whether the automated signals correspond to real strategy changes.

## 2. Separate Training-Time Selection From Final Evaluation

Goal: make it clear that replay checks and holdout spot checks are selection tools, not the final evidence of robustness or generalization.

- [ ] Freeze a held-out benchmark panel before analyzing new runs.
- [ ] Expand the held-out panel so it covers multiple opponent archetypes and map regimes.
- [ ] Run final accepted learner policies against the full held-out panel, not just selection-time spot checks.
- [ ] Ensure evaluation uses fixed seeds and no online adaptation.
- [ ] Report training metrics and held-out evaluation metrics in separate sections.
- [ ] Prevent aggregate conclusions from collapsing training success and evaluation success into one sentence.
- [ ] Add explicit report wording that selection-time replay checks are inner-loop filters.

Why this matters:
- Training-time robustness probes improve selection discipline, but they do not replace a real test set.

## 3. Strengthen Replication And Statistical Discipline

Goal: reduce the chance that reported effects are artifacts of one seed, one run family, or one noisy comparison.

- [ ] Run at least three replicated live runs for every family used in claims.
- [ ] Prefer five replicates for the strongest behavioral claims if cost allows.
- [ ] Freeze the primary metrics before inspecting results.
- [ ] Report uncertainty intervals for the main learner-centric outcomes.
- [ ] Report effect sizes, not only directional differences.
- [ ] Keep learner-centric summaries separate from opponent-role summaries.
- [ ] Add a short analysis note describing which claims are primary and which are exploratory.

Why this matters:
- Long-horizon adaptive systems are variable, and reviewers will expect replication discipline similar to RL best practice.

## 4. Add Structured Qualitative Review

Goal: support quantitative claims about novelty, recovery, churn, or overfitting with concrete case evidence.

- [ ] Define a fixed process for selecting notable epochs across runs.
- [ ] Include prompts, submitted code, executed-code traces, opponent context, and path artifacts for each selected epoch.
- [ ] Identify at least one example each of:
  - [ ] escape from a losing regime
  - [ ] churn without improvement
  - [ ] replay failure or archive-induced recovery
  - [ ] holdout failure after strong training performance
- [ ] Add qualitative appendices or companion notes for those cases.
- [ ] Use those cases to check whether the automated metrics are telling the right story.

Why this matters:
- Code novelty alone is not enough to justify words like `innovation` or `new strategy class`.

## 5. Broaden Generalization Claims Carefully

Goal: move from "works on this benchmark family" toward stronger and more defensible generalization statements.

- [ ] Split held-out evaluation into `near-OOD` and `far-OOD` regimes.
- [ ] Add variation in board size, obstacle density, resource layout, and spawn rules.
- [ ] Test unseen opponent families that were never present during training.
- [ ] Report generalization separately by regime instead of averaging everything together.
- [ ] Avoid broad generalization claims unless a second environment is added.
- [ ] If feasible, add a second related environment and rerun the evaluation protocol there.

Why this matters:
- Generalization is usually task-family-specific unless the benchmark scope is widened explicitly.

## 6. Improve Quality-Diversity Interpretation

Goal: make diversity-aware selection claims more rigorous and less dependent on lexical novelty.

- [ ] Compare lexical novelty and behavioral novelty directly across accepted and rejected candidates.
- [ ] Check whether behavior-cell coverage predicts held-out robustness better than code novelty.
- [ ] Evaluate whether elite-archive coverage grows in a stable way across replicates.
- [ ] Add plots showing performance versus behavior-cell coverage over training.
- [ ] Identify whether novelty-aware selection finds genuinely different successful policies or mainly filters churn.

Why this matters:
- The current curriculum results suggest that selection is helping more by rejecting poor churn than by rewarding many successful novel solutions.

## 7. Report-Language Tightening

Goal: keep the public-facing reports conservative and researcher-appropriate until the stronger evidence exists.

- [ ] Keep terms like `heuristic`, `proxy`, `suggests`, and `preliminary` where warranted.
- [ ] Avoid using `innovation` as a headline claim without behavioral validation.
- [ ] Avoid using `generalization` without held-out evaluation evidence.
- [ ] Avoid using `cheating` when the evidence is only a rule-boundary indicator.
- [ ] Update the reports when metric validation or broader evaluation is complete.

Why this matters:
- Strong claims are much harder to defend than careful, scoped claims.

## Exit Condition

These items are reduced enough for a stronger publication push when:

- [ ] behavioral heuristics have human-validation evidence
- [ ] final evaluation is clearly separated from training-time selection
- [ ] main claims are replicated across multiple live runs
- [ ] qualitative case studies support the metric-based story
- [ ] generalization claims are scoped to the tested benchmark regimes
- [ ] report language has been updated to reflect the stronger evidence
