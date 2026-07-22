# Deferred Validity And Generalization Backlog

This document tracks the research-limit reductions that are still worth doing after the project is stable and the current curriculum results are acceptable.

This document is separate from [RESEARCH_CHECKLIST.md](../RESEARCH_CHECKLIST.md). The checklist defines the minimum evidence bar for the active study. This document covers the follow-up work needed to make the claims narrower, stronger, and easier to defend under review.

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

The current operational path for this work is [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md) plus [analyze_causal_transfer.py](../analyze_causal_transfer.py).

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
- [ ] Use those cases to check whether the automated metrics agree with the manual evidence.

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

The current operational path for this work is [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md) plus [analyze_causal_transfer.py](../analyze_causal_transfer.py).

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

Goal: make the phase-6 replay explanation harder to dismiss as a post hoc interpretation.

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
- That makes a selector/configurator phase the most plausible way to obtain a positive, interpretable claim without treating phase 7 as evidence of a reusable primitive.

Current status:
- Phase 8 is now implemented on branch `adaptive-portfolio`.
- The official evidence campaign is now complete on branch `adaptive-portfolio`.
- The adaptive controller beat the one-shot static LLM selector, but it did not beat the best fixed heuristic or the supervised selector on held-out TSPLIB.
- The oracle selector tied the best fixed heuristic on the primary held-out TSPLIB endpoint, so the current frozen portfolio has almost no single-best-versus-oracle headroom there.
- That means any further selector-focused work should first create portfolio complementarity or shift the main endpoint toward regimes where the oracle already improves over the single best heuristic.

## 11. Phase 9 Real-World Solver Evolution

Goal: test autonomous solver-code evolution on a real-world benchmark family with explicit feasibility logic, instead of another selector or operator-selection loop.

- [x] Pick one practical benchmark family with official public instances and best-known solutions.
- [x] Keep the first real-world phase on `CVRP`, not `VRPTW`, to reuse existing parsing/scoring infrastructure while still introducing real route-feasibility complexity.
- [x] Implement a strict parser, validator, and scorer for full returned solutions.
- [x] Define a bounded baseline set with 2-3 explicit solver heuristics.
- [x] Specify exactly what the LLM is allowed to evolve in code.
- [x] Match the bounded phase-9 validator to the unrestricted-route semantics used for the chosen Uchoa `X` instances, treating `k` as contextual metadata rather than a hard feasibility limit.
- [x] Curate the bounded phase-9 `X` subset so the committed train/holdout split includes both two-cluster and grid-like descriptor regimes, rather than only a single geometric mode.
- [x] Keep held-out evaluation frozen until the final solver is selected.
- [x] Run the official replicated phase-9 campaign.

Research basis:

- CVRPLIB is the standard public benchmark repository for CVRP instances and best-known solutions; see [CVRPLIB](https://galgos.inf.puc-rio.br/cvrplib/en/instances).
- The Uchoa `X` set was designed to expose a wide range of structurally diverse CVRP behaviors and remains a standard benchmark for heuristic and exact evaluation; see [Uchoa et al. 2017](https://doi.org/10.1016/j.ejor.2016.08.012).
- DIMACS explicitly treats CVRP as a benchmark family where algorithm engineering, feasibility validation, and fair scoring matter; see [DIMACS CVRP](https://dimacs.rutgers.edu/programs/challenge/vrp/cvrp/).

Why this matters:

- It is a stronger test of autonomous solver-code evolution than TSP portfolio selection.
- It keeps the claim bounded and scorable: progress toward feasible, competitive, interpretable solver logic on held-out CVRP.

Current status:
- Phase 9 is now evidence-complete on branch `real-world-vrp`.
- The official 20-offset campaign was technically valid: all runs completed, all solver-evolution final incumbents were feasible on both train and held-out panels, and the accepted path contained no fallback, generation-error, or solver-timeout contamination.
- Solver evolution beat the weaker nearest-neighbor and regret-insertion baselines on held-out CVRPLIB X instances, but it did not beat the strongest fixed Clarke-Wright baseline on the primary endpoint.
- Cross-family synthesis was completed from that evidence base, and the current narrow follow-up is a bounded phase-9 closeout study that disentangles direct synthesis, budget-matched search, and replay-aware iterative search without reopening the broader model-strength branch.

## 11A. Phase 9 Closeout: Budget-Control CVRP Study

Goal: answer the remaining mechanism question from phase 9 without changing benchmark family, validator, train/held-out split, or model tier.

- [x] Freeze a dedicated closeout protocol that keeps the bounded Uchoa `X` setup unchanged.
- [x] Add a `direct_generate_plus_one_repair` closeout arm.
- [x] Add a `budget_matched_no_replay` closeout arm with the same candidate budget as replay-aware search.
- [x] Add a `replay_solver_evolution` closeout arm that reuses the bounded phase-9 validation path.
- [x] Keep the original phase-9 fixed baselines available for contextual comparison.
- [x] Add a no-cost smoke config that exercises the full closeout condition set.
- [x] Run the official replicated closeout campaign and aggregate paired deltas against both the strongest fixed baseline and the budget-matched control.

Research basis:

- Budget matching is required before replay can be credited for anything beyond additional candidate budget; that is the same methodological point emphasized in the project's model-strength factorial protocol.
- Replicated run summaries, paired uncertainty intervals, and avoiding best-run-only interpretation follow the same empirical-discipline concerns raised in [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560) and [Deep RL at the Edge of the Statistical Precipice](https://arxiv.org/abs/2108.13264).

Current status:
- The implementation is on branch `cvrp-closeout-budget-control`.
- The protocol is [docs/PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_PROTOCOL.md](PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_PROTOCOL.md).
- The runbook is [configs/cvrp_phase9_closeout/RUNBOOK.md](../configs/cvrp_phase9_closeout/RUNBOOK.md).
- The official 20-offset campaign is now complete under `runs/cvrp_phase9_closeout/budget_control`, with aggregate results in `aggregate_20260605_050930_t`.
- `replay_solver_evolution` was the only learned arm that stayed fully feasible in all 20 official runs, and it beat both `budget_matched_no_replay` and `direct_generate_plus_one_repair` on held-out penalized gap.
- The closeout did not overturn the strongest fixed-baseline result: Clarke-Wright remained the best condition on the primary held-out endpoint.
- The permanent interpretation note is [docs/PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_RESULTS_2026-06-05.md](PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_RESULTS_2026-06-05.md).

## 12. Cross-Family Code-Evolution Synthesis

Goal: turn the completed simple-game, TSP, and real-world CVRP evidence into a unified capabilities-and-limitations framework instead of adding another open-ended benchmark phase.

- [x] Normalize endpoint performance, code novelty, reliability, update/acceptance rate, and train-time trend signals across the completed official archives.
- [x] Keep train-time dynamics separate from held-out endpoint results.
- [x] Add a historical direct Codex-authored CVRP check that is evaluated through the phase-9 validator without API calls.
- [x] State the direct Codex result as descriptive and non-retained as thesis evidence unless a future protocol freezes and replicates direct-Codex prompting.
- [x] Preserve conservative wording: the synthesis supports capability-bounded adaptation, not a broad claim that LLM evolution beats mature optimization solvers.

Research basis:

- Replicated run summaries, uncertainty-aware reporting, and avoiding best-run-only interpretation follow the reproducibility concerns raised in [Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560) and [Deep RL at the Edge of the Statistical Precipice](https://arxiv.org/abs/2108.13264).
- The selector and portfolio phases remain naturally connected to Rice-style algorithm selection; see [The Algorithm Selection Problem](https://doi.org/10.1016/S0065-2458(08)60520-3).
- The CVRP real-world endpoint remains scoped to the standard CVRPLIB Uchoa X benchmark source used in phase 9; see [CVRPLIB](https://galgos.inf.puc-rio.br/cvrplib/en/instances).

Current status:
- Cross-family synthesis is now implemented on branch `cross-family-synthesis`.
- The official synthesis artifact is under `runs/cross_family_synthesis/meta_patterns_20260522_165500`.
- The permanent report is [docs/CROSS_FAMILY_CODE_EVOLUTION_SYNTHESIS_2026-05-22.md](CROSS_FAMILY_CODE_EVOLUTION_SYNTHESIS_2026-05-22.md).
- The direct Codex CVRP solver was feasible on all phase-9 train and held-out instances and descriptively beat the fixed Clarke-Wright baseline on mean held-out penalized gap, but this remains a historical single-shot descriptive check rather than replicated stochastic evidence or retained thesis evidence.

## 13. Model Strength Versus Evolution Technique

Goal: separate base LLM coding strength from the added value of evolutionary code search, replay, and compressed failure memory.

- [x] Define a crossed design over simple games, symmetric TSP, and real-world CVRP.
- [x] Add exactly three model-strength tiers and record a transparent benchmark-strength score source.
- [x] Add the key `budget_matched_no_replay` control so replay is not credited for extra API budget alone.
- [x] Preserve fixed train/held-out splits and existing validators.
- [x] Aggregate into model x evolution matrices, within-task z-scores, variance decomposition, and effect sizes against both single-shot and budget-matched controls.
- [ ] Run the full paid campaign and interpret replay/failure/compression only when they beat `budget_matched_no_replay`.

Research basis:

- Stochastic adaptive systems need replicated seeds, uncertainty intervals, and effect sizes rather than best-run-only evidence; see Henderson et al. 2018, `Deep Reinforcement Learning That Matters`, and Agarwal et al. 2021, `Deep RL at the Edge of the Statistical Precipice`.
- Factorial designs and ANOVA-style variance decomposition are appropriate when the scientific question is whether one experimental factor, here base model strength, explains more variance than another factor, here evolution technique.
- Budget matching is required because otherwise replay and iterative evolution can be confounded with simply buying more candidate generations.

Current status:
- The implementation is on branch `model-strength-factorial`.
- The no-cost smoke artifacts are written under `DO NOT COMMIT/`.
- The official campaign should be run only after the smoke test passes and model access is confirmed.

## Exit Condition

These items are reduced enough for a stronger publication push when:

- [ ] behavioral heuristics have human-validation evidence
- [ ] final evaluation is clearly separated from training-time selection
- [ ] main claims are replicated across multiple live runs
- [ ] qualitative case studies support the metric-based interpretation
- [ ] generalization claims are scoped to the tested benchmark regimes
- [ ] report language has been updated to reflect the stronger evidence
