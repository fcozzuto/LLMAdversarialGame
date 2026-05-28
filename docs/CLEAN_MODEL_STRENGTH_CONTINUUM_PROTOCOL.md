# Clean Model-Strength Continuum Protocol

This follow-up phase extends the archived model-strength factorial rather than replacing it. The previous result remains valid: replay, failure replay, and compression did not beat the budget-matched no-replay control in the completed 750-row run.

## Scientific Question

Does evolutionary code search provide performance gains above and beyond a clean same-family GPT-5 frontier capability continuum, once benchmark saturation and feasibility/penalty regimes are handled explicitly?

## Why This Is A New Phase

This is a new phase because it changes the model-strength axis and analysis plan:

- the model ladder moves from mixed nano/mini/full aliases to five pinned GPT-5 frontier-family snapshots,
- empirical calibration is added before the full run,
- reasoning-effort support is probed before paid campaigns,
- TSP is explicitly tested as a saturation case,
- CVRP is decomposed into feasibility escape and optimization quality,
- paired/bootstrap comparisons become the primary inferential layer.

## Model Continuum

The required snapshots are:

1. `gpt-5-2025-08-07`
2. `gpt-5.1-2025-11-13`
3. `gpt-5.2-2025-12-11`
4. `gpt-5.4-2026-03-05`
5. `gpt-5.5-2026-04-23`

The full run should use the calibrated config produced by `derive_model_strength_scores.py`, not the placeholder ordinal scores in `configs/model_strength_continuum_factorial.yaml`.

The full template sets `require_empirical_model_strength_scores=true`, so the runner fails fast if the official campaign is launched before calibration-derived scores replace the pending score sources.

All five snapshots use the same configured reasoning effort, `low`, because it is supported across the requested GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, and GPT-5.5 model pages. Reasoning-effort fallback is disabled for this phase, so the run fails fast instead of silently switching one model to a different effort regime.

`probe_openai_reasoning_efforts.py` records a low-cost empirical compatibility check for the pinned models and candidate efforts. The 2026-05-28 preflight found `low`, `medium`, and `high` accepted by all five configured snapshots. This confirms that fallback-disabled official runs can use any of those efforts without silent per-model effort drift.

## Calibration

The calibration suite uses two seeds per task family and only `single_shot` generation. Its score is derived from train-validator behavior only:

- simple games: train score margin,
- TSP: negative train optimality gap,
- CVRP: negative train penalized gap,
- plus generation validity as a small conformance component.

This avoids assuming ordinal model strength a priori and avoids tuning the score on official held-out endpoints.

## TSP Saturation Handling

TSP is handled in two ways:

- the TSP primary metric is changed from held-out TSPLIB-only gap to combined transfer gap in the clean-continuum config,
- aggregation writes pooled analyses with and without TSP.

Aggregation also writes `tsp_diagnostics/tsp_saturation_diagnostics.csv` and `tsp_diagnostics/tsp_materialization_audit.csv`, so saturation and fallback/materialization rows are explicit rather than hidden in the pooled model.

The archived mixed-ladder timeout audit is recorded in [docs/TSP_MATERIALIZATION_TIMEOUT_AUDIT_2026-05-27.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/TSP_MATERIALIZATION_TIMEOUT_AUDIT_2026-05-27.md).

## CVRP Feasibility And Optimization Split

CVRP rows retain the primary penalized endpoint, but aggregation also writes a decomposed analysis:

- `feasibility_escape_rate`: higher held-out feasibility is better,
- `penalized_objective_quality`: lower held-out penalized gap is better,
- `feasible_only_objective_quality`: lower held-out feasible-only gap is better.

The decomposed paired/bootstrap effects are written to `cvrp_decomposition/cvrp_vs_budget_matched_metric_effects.csv`.

## Realized-Budget Accounting

The runner now records:

- successful generations,
- generation errors,
- fallback generations,
- repair attempts,
- salvage attempts,
- executable candidates,
- TSP materialization fallbacks,
- TSP materialization timeouts,
- accepted fallback epochs,
- accepted executable epochs.

These fields make it possible to separate model capability from failure to produce valid executable code.

The same fields are also summarized in `cell_means.csv`, so post-run checks can quickly identify cells where poor performance reflects invalid generations, fallback use, materialization timeouts, or failure to accept executable candidates.

## Inference Policy

The primary inferential layer is paired/bootstrap comparison against:

- `single_shot`,
- `budget_matched_no_replay`.

OLS/ANOVA variance decomposition is retained as a secondary diagnostic, especially for the model-strength axis and interaction structure. Replay-specific value should not be claimed unless replay/failure/compression beats `budget_matched_no_replay`.

## Research Basis

The protocol follows standard practice for stochastic adaptive systems: fixed budgets, predeclared task splits, independent seeds, budget-matched controls, held-out evaluation, effect sizes, and uncertainty estimates. This matches the project's existing references to Henderson et al. 2018 (`Deep Reinforcement Learning That Matters`) and Agarwal et al. 2021 (`Deep RL at the Edge of the Statistical Precipice`), and it follows the algorithm-selection framing introduced by Rice 1976.

## Runbook

Use [configs/model_strength_continuum/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/model_strength_continuum/RUNBOOK.md).
