# Model Strength x Evolution Factorial Protocol

## Purpose

This phase tests whether evolutionary code search contributes performance above base LLM coding strength across the three completed project families:

- `simple_games`
- `tsp`
- `cvrp_phase9_real_world`

The primary scientific question is:

> Does evolutionary code search provide performance gains above and beyond base LLM coding strength, or is most performance variance explained by the underlying model?

## Design

The design is a crossed factorial:

- 3 model tiers: `weak_model`, `medium_model`, `strong_model`.
- 5 techniques: `single_shot`, `budget_matched_no_replay`, `random_replay`, `failure_replay`, `failure_replay_compression`.
- 3 task families: simple games, symmetric TSP, and real-world CVRP.

The key control is `budget_matched_no_replay`. It uses the same candidate-generation budget as replay conditions but does not expose replay memory, failure memory, or compressed history. Replay claims are valid only when they improve over this control.

## Budgets

- Simple games: 10 seeds per model x technique cell, 100 candidates for all non-single-shot conditions.
- TSP: 20 seeds per model x technique cell, 8 candidates for all non-single-shot conditions.
- CVRP: 20 seeds per model x technique cell, 8 candidates for all non-single-shot conditions.

Single-shot conditions receive one candidate per seed.

## Metrics

The runner writes one row per run with:

- `task_family`
- `model_tier`
- `model_name`
- `benchmark_strength_score`
- `benchmark_score_source`
- `evolution_technique`
- `seed`
- `epochs_budget`
- `candidate_budget`
- `performance_raw`
- `performance_z`
- `secondary_performance_raw`
- `feasibility_rate`
- `runtime_ms`
- `generation_success_rate`
- `accepted_epochs`
- `acceptance_rate`
- `mean_code_novelty`
- task-specific primary metrics: `primary_holdout_win_rate`, `primary_holdout_score_margin`, `final_tsplib_gap`, `final_transfer_gap`, `adaptation_efficiency`, `heldout_feasibility_rate`, `heldout_penalized_gap`, `heldout_feasible_gap`, and `heldout_runtime_ms`
- `artifact_path`

Task-specific primary performance uses the supervisor-specified signs:

- Simple games: `performance_raw = primary_holdout_win_rate`.
- TSP: `performance_raw = -final_tsplib_gap`.
- CVRP: `performance_raw = -heldout_penalized_gap`.

For CVRP rows, `heldout_feasible_gap` and `secondary_performance_raw` remain blank if no held-out solution is feasible; infeasible solvers are still ranked by the penalized primary endpoint.

For TSP rows, `adaptation_efficiency` is the training-panel gap improvement from the first candidate to the final accepted incumbent, divided by cumulative accepted code novelty after the first candidate. It is exploratory and should not override the held-out `final_tsplib_gap` endpoint.

`performance_z` is computed within each task family so pooled analyses are not dominated by metric scale.

## Analysis

The aggregator writes:

- task-specific and pooled reduced-model OLS/ANOVA decompositions,
- categorical and continuous model-strength specifications,
- semi-partial R2,
- partial eta squared,
- p-values,
- residual variance,
- bootstrap cell confidence intervals,
- effect sizes against `single_shot`,
- effect sizes against `budget_matched_no_replay`,
- model x evolution matrices and heatmaps.

Variance-decomposition formulas:

- Task continuous: `performance_z ~ benchmark_strength_score + C(evolution_technique) + benchmark_strength_score:C(evolution_technique)`.
- Task categorical: `performance_z ~ C(model_tier) * C(evolution_technique)`.
- Pooled continuous: `performance_z ~ C(task_family) * benchmark_strength_score * C(evolution_technique)`.
- Pooled categorical: `performance_z ~ C(task_family) * C(model_tier) * C(evolution_technique)`.

Effect-size comparisons are paired by seed when both conditions share the same seed. In paired comparisons, Cohen's d is standardized by the standard deviation of seed-paired deltas; otherwise, it uses the pooled standard deviation of candidate and reference values.

The main report must explicitly answer:

1. How much variance is explained by model strength?
2. How much variance is explained by evolutionary technique?
3. Is there a model strength x technique interaction?
4. Do replay/failure/compression techniques beat a budget-matched no-replay control?
5. Are evolutionary gains larger for weak models than strong models?
6. Is the strongest conclusion model strength dominance, independent evolution value, or task/model-regime-specific value?

## Research Rationale

The protocol follows standard replication and uncertainty discipline for stochastic adaptive systems: fixed budgets, independent seeds, held-out evaluation, effect sizes, and variance decomposition rather than best-run selection. This matches the cautionary evidence from reproducibility work in adaptive/learning systems, including Henderson et al. 2018 (`Deep Reinforcement Learning That Matters`) and Agarwal et al. 2021 (`Deep RL at the Edge of the Statistical Precipice`).

The model-tier factor is analyzed both categorically and continuously because the project-specific model aliases may not have comparable public coding-benchmark scores. The committed default uses transparent ordinal scores and records `benchmark_score_source=ordinal_proxy`; if comparable HumanEval, MBPP, LiveCodeBench, or SWE-bench Verified scores are confirmed for all three tiers, those can replace the ordinal proxy before the official run.

The committed model ladder is budget-feasible rather than maximal-cost: `gpt-4.1-nano` as `weak_model`, `gpt-5-nano` as `medium_model`, and `gpt-5.4-mini` as `strong_model`. The strong tier should be interpreted as the strongest affordable model in the committed three-level ladder, not necessarily the strongest model available in the account.

## Interpretation Rule

Do not overclaim algorithmic discovery. The strongest expected claim is:

> Across games, TSP, and real-world CVRP, base model strength explains the largest share of performance variance, while evolutionary technique contributes smaller, task-dependent gains. Replay and failure-based techniques add value only if they improve over the budget-matched no-replay control, not merely over single-shot generation.
