# Phase 9 Closeout: Budget-Control CVRP Study

## Purpose

This protocol defines the bounded closeout study attached to phase 9.

The goal is not to introduce a new benchmark family or reopen the broad model-strength question. The goal is to answer the narrow mechanism question left open by the bounded real-world `CVRP` study:

> when the phase-9 `CVRP` pipeline improves over weaker baselines, how much of that gain is better explained by direct synthesis, by extra candidate budget, or by replay-aware iterative solver evolution?

The closeout therefore stays on the same bounded `CVRPLIB` `X` setup, the same validator, the same train/held-out split, and the same generator and judge models already used in the retained phase-9 evidence.

## Relationship To Phase 9

This is a phase-9 closeout study, not a new broad phase in the sense of phases 7, 8, or 9.

- Phase 9 established that bounded whole-solver evolution on real-world `CVRP` is technically feasible and can beat weaker fixed baselines on held-out instances.
- Phase 9 did not show a win over the strongest fixed `Clarke--Wright` baseline on the primary endpoint.
- A historical descriptive direct Codex-authored `CVRP` check was stronger than the replicated autonomous mean. That result was not a frozen replicated condition and is not retained as thesis evidence.

The closeout study exists to convert that descriptive gap into a controlled budget-comparison result, or else to falsify the stronger interpretation cleanly.

## Naming And Archival Structure

The branch and tag naming follow the same project structure used for the earlier phases.

- Working branch: `cvrp-closeout-budget-control`
- Official archive tag on successful completion: `phase-9-closeout-budget-control`
- Smoke outputs: `DO NOT COMMIT/phase9_closeout_budget_control_smoke/`
- Official outputs: `runs/cvrp_phase9_closeout/budget_control/`
- Permanent report: `docs/PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_RESULTS_YYYY-MM-DD.md`

The official tag should be created only after:

1. the protocol is frozen,
2. the smoke campaign passes,
3. the official replicated campaign completes, and
4. the aggregate report and thesis integration are checked.

## Fixed Invariants

The following parts of the study are fixed unless this protocol is revised before any official run:

- Benchmark family: the same bounded phase-9 `CVRPLIB` `X` suite
- Train/held-out split: unchanged from phase 9
- Generator model: unchanged from phase 9
- Judge model: unchanged from phase 9
- Timeout policy: unchanged from phase 9 unless a technical-failure audit justifies a documented change
- Primary endpoint: held-out penalized gap
- Secondary endpoints: held-out feasibility, held-out runtime, accepted-candidate count where applicable, code novelty, and solver complexity
- Replication design: paired seed offsets shared across compared conditions

This preserves comparability with the retained phase-9 thesis result and avoids reopening the separate model-strength question.

## Conditions

The official closeout suite retains the three fixed phase-9 baselines for context:

- `nearest_neighbor_constructive`
- `clarke_wright_savings`
- `regret_insertion_local_search`

The closeout comparison set is:

1. `direct_generate_plus_one_repair`
2. `budget_matched_no_replay`
3. `replay_solver_evolution`

The scientific roles of the closeout arms are:

- `direct_generate_plus_one_repair`: a bounded direct-synthesis control with one scripted evaluation-driven follow-up round
- `budget_matched_no_replay`: an independent multi-candidate control with the same candidate budget as iterative search but no replay memory
- `replay_solver_evolution`: an incumbent-preserving iterative search arm that receives compact replay summaries from earlier weak candidates

## Candidate Budgets

The closeout uses the same `8`-candidate budget as the bounded phase-9 evolutionary run:

- `direct_generate_plus_one_repair`: `2` generated candidates
- `budget_matched_no_replay`: `8` independent generated candidates
- `replay_solver_evolution`: `8` iterative generated candidates

The direct arm uses a smaller budget because it asks a different question: whether minimal bounded repair already explains most of the descriptive direct-solver advantage.

## Statistical Reporting

The official report follows the same conservative reporting discipline as the retained thesis phases.

- Report per-condition held-out means on the primary endpoint.
- Report paired deltas with `95%` bootstrap confidence intervals.
- For the closeout arms, accept or retain candidates using train-panel feasibility first and train penalized gap second; report runtime, but do not use runtime as the primary acceptance criterion.
- Report technical-validity checks, including generation errors, fallback counts, feasibility failures, and accepted-candidate counts.
- If API budgeting matters, record spend separately from provider usage or billing logs; the repository's built-in closeout reports do not currently estimate dollar cost.
- Keep smoke outputs out of the thesis evidence base.
- Do not promote replay-specific claims unless `replay_solver_evolution` beats `budget_matched_no_replay`.

## Success Criterion

The strongest positive closeout result is not necessarily "beat `Clarke--Wright`." The closeout is scientifically successful if it cleanly answers the budget-versus-mechanism question under the phase-9 validator.

Valid closeout outcomes include:

- replay-aware evolution beats budget-matched no replay under paired uncertainty,
- budget-matched no replay matches replay and shows that extra search budget explains most gains,
- direct synthesis plus one repair dominates both iterative arms, which narrows the thesis conclusion toward bounded coding assistance rather than replay-aware autonomy.

Any of these outcomes is more valuable than another unconstrained late benchmark extension because each sharpens the final dissertation claim without broadening it.
