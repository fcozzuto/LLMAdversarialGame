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

The current operational path for this work is [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md) plus [analyze_causal_transfer.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/analyze_causal_transfer.py).

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
- [ ] Avoid broad generalization claims even after the added routing benchmark families are run with replicated official suites. The completed 20-offset TSP/ATSP/CVRP pass is mixed and family-dependent, so broader replay-aware claims still need tighter scope and better mechanism-level explanation.
- [ ] If feasible, add a second related environment and rerun the evaluation protocol there.

Why this matters:
- Generalization is usually task-family-specific unless the benchmark scope is widened explicitly.

## 6. Improve Quality-Diversity Interpretation

Goal: make diversity-aware selection claims more rigorous and less dependent on lexical novelty.

The current operational path for this work is [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md) plus [analyze_causal_transfer.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/analyze_causal_transfer.py).

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

## 8. Strengthen The Phase 6 Mechanism Claim

Goal: make the phase-6 replay explanation harder to dismiss as a post hoc story.

- [ ] Check whether archive descriptor diversity predicts transfer after controlling for archive hardness and archive size bias.
- [ ] Verify that the residual-difficulty estimator is stable across baseline portfolios, not only one fixed reference set.
- [ ] Test whether the phase-6 mechanism claim holds if the train subset or synthetic family mix changes modestly.
- [ ] Add sensitivity analyses for archive size and replay-instance count.
- [ ] Report whether the diversity signal is driven by one descriptor family or remains broad-based.

Why this matters:
- "Random replay won" is interesting, but the mechanism claim still needs to survive basic robustness checks.

## 9. Tighten Phase 7 Discovery Validation

Goal: reduce the chance that a phase-7 "discovered operator" is only a renamed standard trick or a host-scaffold artifact.

- [ ] Add a manual literature audit for any operator that survives the automated filter.
- [ ] Expand transplant validation from held-out TSPLIB to a second scaffold pool if runtime allows.
- [ ] Check whether operator signatures remain stable when validation-family seeds are changed.
- [ ] Compare rediscovery counts using both exact signatures and coarser novelty-classification families.
- [ ] Add a blinded review step for the strongest surviving operator reports before making novelty claims.

Why this matters:
- The main scientific value of phase 7 is interpretability, so false-positive "discoveries" are especially costly.

## 10. Phase 8 High-Probability Closeout Phase

Goal: land one more bounded, positive result that is easier to defend than another open-ended operator-invention campaign.

- [x] Replace open-ended operator invention with feature-based selection or configuration over a fixed library of known operators and solver scaffolds.
- [x] Freeze a library of candidate low-level operators and host scaffolds before the study begins.
- [x] Reuse the phase-6 descriptor basis and add lightweight online search-state features for selector context.
- [x] Compare against the single-best fixed scaffold, full-solver evolution, and random operator selection.
- [x] Treat a statistically reliable held-out TSPLIB gain or a clean Pareto gain over the single-best fixed baseline as the success criterion in the protocol.
- [x] Keep the operator library interpretable enough that any win can be explained as selection, scheduling, or parameter control rather than hidden solver invention.

Research basis:
- Rice-style per-instance algorithm selection, as summarized in [Algorithm selection on a meta level](https://link.springer.com/article/10.1007/s10994-022-06161-4), is a better fit when instance descriptors already exist and whole-solver discovery is unstable.
- Selection-oriented hyper-heuristics remain a standard, better-supported alternative to unconstrained heuristic generation; see [Hyper-heuristics: A survey and taxonomy](https://www.sciencedirect.com/science/article/pii/S0360835223008392).
- Automatic configuration is already recommended practice in routing because it improves solution quality and supports fairer comparisons; see [On automatic algorithm configuration of vehicle routing problem solvers](https://link.springer.com/article/10.1007/s41604-019-00010-9).
- A recent routing example using contextual low-level operator selection is [Landscape-Aware Bandit Hyper-Heuristics for Online Operator Selection in UAV Inspection Routing](https://arxiv.org/abs/2605.14620).

Why this matters:
- The current evidence suggests the system is stronger at curation, scheduling, and tuning than at inventing wholly new reusable operators.
- That makes a selector/configurator phase the most plausible way to end with a positive, interpretable claim without pretending that phase 7 already discovered a reusable primitive.

Current status:
- Phase 8 is now implemented on branch `adaptive-portfolio`.
- The official evidence campaign is now complete on branch `adaptive-portfolio`.
- The adaptive controller beat the one-shot static LLM selector, but it did not beat the best fixed heuristic or the supervised selector on held-out TSPLIB.
- The oracle selector tied the best fixed heuristic on the primary held-out TSPLIB endpoint, so the current frozen portfolio has almost no single-best-versus-oracle headroom there.
- That means any further selector-focused work should first create portfolio complementarity or shift the main endpoint toward regimes where the oracle already improves over the single best heuristic.

## Exit Condition

These items are reduced enough for a stronger publication push when:

- [ ] behavioral heuristics have human-validation evidence
- [ ] final evaluation is clearly separated from training-time selection
- [ ] main claims are replicated across multiple live runs
- [ ] qualitative case studies support the metric-based story
- [ ] generalization claims are scoped to the tested benchmark regimes
- [ ] report language has been updated to reflect the stronger evidence
