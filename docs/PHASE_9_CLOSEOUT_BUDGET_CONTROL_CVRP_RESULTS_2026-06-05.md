# Phase 9 Closeout Budget-Control CVRP Results (2026-06-05)

This note records the official 20-offset phase-9 closeout campaign on branch `cvrp-closeout-budget-control`.

The official artifact archive for this study is under `runs/cvrp_phase9_closeout/budget_control/aggregate_20260605_050930_t`.

## Headline

The closeout successfully answered the remaining phase-9 mechanism question.

- The campaign is technically valid: 20 paired runs, 6 conditions, judge enabled in all 20 runs, and no recorded generation fallbacks or generation errors in any official closeout arm.
- `phase9_closeout_replay_solver_evolution` was the only learned arm that remained fully feasible in all 20 official runs on both the train and held-out panels.
- `phase9_closeout_replay_solver_evolution` clearly beat both `phase9_closeout_budget_matched_no_replay` and `phase9_closeout_direct_generate_plus_one_repair` on the primary held-out endpoint.
- `phase9_closeout_replay_solver_evolution` did not beat the strongest fixed `phase9_closeout_baseline_clarke_wright_savings` baseline on mean held-out penalized gap.
- The direct and budget-matched controls often produced syntactically valid but semantically broken solver code, so the closeout separates raw coding attempts from a stable replay-aware incumbent-preserving search loop.

The right interpretation is therefore:

> in the bounded phase-9 CVRP setup, replay-aware iterative search adds real value beyond extra candidate budget and beyond a one-repair direct synthesis control, but the strongest classical Clarke-Wright baseline still wins on the main held-out endpoint.

## Main Findings

- Best mean held-out condition: `phase9_closeout_baseline_clarke_wright_savings`, mean penalized gap `0.073766`.
- `phase9_closeout_replay_solver_evolution`: mean held-out penalized gap `0.171114`, 95% bootstrap CI `[0.129598, 0.212339]`.
- `phase9_closeout_budget_matched_no_replay`: mean held-out penalized gap `2.932746`, 95% bootstrap CI `[2.414166, 3.530529]`.
- `phase9_closeout_direct_generate_plus_one_repair`: mean held-out penalized gap `5.286402`, 95% bootstrap CI `[3.127768, 7.591162]`.
- `phase9_closeout_replay_solver_evolution` versus `phase9_closeout_budget_matched_no_replay`: held-out penalized-gap delta `-2.761632`, 95% CI `[-3.369777, -2.201586]`.
- `phase9_closeout_replay_solver_evolution` versus `phase9_closeout_direct_generate_plus_one_repair`: held-out penalized-gap delta `-5.115288`, 95% CI `[-7.451608, -2.946446]`.
- `phase9_closeout_replay_solver_evolution` versus `phase9_closeout_baseline_clarke_wright_savings`: held-out penalized-gap delta `+0.097348`, 95% CI `[0.055994, 0.138558]`.
- Replay beat the budget-matched no-replay control in 18 of 20 runs and beat the direct-plus-repair control in 17 of 20 runs.
- Replay beat Clarke-Wright in 10 of 20 runs, but lost often enough that Clarke-Wright remained the best condition on mean held-out gap.
- Replay beat nearest-neighbor in 10 of 20 runs and matched it in the other 10 runs.

## Technical Validity

The closeout conclusion is based on both the aggregate summary and lower-level audit checks.

The main technical checks were:

- 20 paired runs were present under `runs/cvrp_phase9_closeout/budget_control`.
- All 6 conditions were present in every run.
- Judge status was `enabled` in all 20 runs.
- `phase9_closeout_replay_solver_evolution` had 20 accepted epochs across 160 total epochs.
- `phase9_closeout_budget_matched_no_replay` had 30 accepted epochs across 160 total epochs.
- `phase9_closeout_direct_generate_plus_one_repair` had 27 accepted epochs across 40 total epochs.
- All official closeout arms had 0 recorded generation fallbacks and 0 recorded generation errors.
- Full held-out feasibility was 20 of 20 runs for replay, 5 of 20 runs for direct, and 3 of 20 runs for budget-matched no replay.
- Replay ended with 20 distinct final fingerprints across the 20 official runs, so the result is not one repeated artifact.

This means the closeout is scientifically usable as run. The weak direct and no-replay outcomes are not explained by hidden fallback contamination.

## Interpretation

The closeout narrows the dissertation claim in a useful way.

- Extra candidate budget alone is not enough. The memoryless `budget_matched_no_replay` control collapsed badly on feasibility and held-out penalized gap.
- One-step direct synthesis plus repair is also not enough in this bounded setup. It occasionally found strong feasible runs, but it was unstable and often semantically broken.
- Replay-aware iterative search is the only learned arm that preserved full train and held-out feasibility across the official campaign.
- Replay therefore contributes more than simply buying additional candidates: it stabilizes the search around an incumbent and avoids the worst failure patterns well enough to dominate the other learned controls.
- Even so, the strongest fixed Clarke-Wright baseline still wins on the main held-out endpoint.

So the closeout strengthens the thesis in a precise way:

> the bounded CVRP evidence does not support a claim that current LLM-guided autonomous code search beats the strongest practical classical baseline, but it does support a stronger claim that replay-aware incumbent-preserving search is materially better than both memoryless budget-matched search and a bounded direct-generation control.

## Consequence For The Thesis

This closeout should be used to sharpen, not broaden, the final thesis conclusion.

- It supports the capability-boundary framing already used in the dissertation.
- It rules out the weaker explanation that replay looked helpful only because it consumed more search budget.
- It also rules out the idea that a simple direct-generation-plus-repair control already explains the phase-9 result.
- The remaining limitation is unchanged: the strongest fixed classical baseline still wins on the primary held-out endpoint.

That gives the dissertation a cleaner final message than the original phase-9 result alone.

## Sources

- [Closeout aggregate report](../runs/cvrp_phase9_closeout/budget_control/aggregate_20260605_050930_t/aggregate_report.md)
- [Closeout aggregate summary JSON](../runs/cvrp_phase9_closeout/budget_control/aggregate_20260605_050930_t/aggregate_summary.json)
- [Closeout final run suite summary](../runs/cvrp_phase9_closeout/budget_control/run_20260605_050930_t/suite_summary.json)
- Representative closeout artifacts under [runs/cvrp_phase9_closeout/budget_control](../runs/cvrp_phase9_closeout/budget_control)
