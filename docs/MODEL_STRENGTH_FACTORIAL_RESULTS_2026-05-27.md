# Model Strength Factorial Results (2026-05-27)

This note records the official crossed model-strength x evolution-technique campaign across simple games, symmetric TSP, and real-world CVRP.

The official artifact archive is under `runs/cross_family_model_x_evolution_factorial/20260524_172130`.

## Headline

The full 750-row factorial campaign completed and is technically valid, but it does not support the originally expected conclusion that model strength dominates performance variance.

- The campaign is structurally complete: 3 task families, 3 model tiers, 5 techniques, and all 750 planned rows.
- The model ladder was the committed budget-feasible ladder: `gpt-4.1-nano`, `gpt-5-nano`, and `gpt-5.4-mini`.
- All required aggregate outputs were produced, including `all_runs_long.csv`, `cell_means.csv`, model x evolution matrices, variance decompositions, effect-size tables, figures, `final_report.md`, and `final_report.pdf`.
- No quota, billing, rate-limit, `HTTP 429`, queue-empty crash, keyboard interrupt, or timeout-expired artifacts were found in the completed official run.
- There were 10 recorded TSP materialization timeouts; after the sandbox fix, these were logged as fallback materializations rather than aborting the campaign.
- Replay, failure replay, and compressed failure replay beat the budget-matched no-replay control in 0 task/model comparisons with positive bootstrap support.

The right interpretation is therefore:

> this factorial campaign shows that gains over single-shot generation are not enough to claim replay-specific evolutionary value. Under the budget-feasible model ladder, performance was dominated by task/model interaction structure, benchmark headroom, and search-budget effects rather than a clean base-model-strength main effect or robust replay advantage.

## Main Findings

- Pooled continuous variance partition: model-strength R2 `0.0008843`, evolution-technique R2 `0.01002`, interaction R2 `0.06909`, residual variance `0.8298`.
- Pooled categorical variance partition: model-tier R2 `0.002063`, evolution-technique R2 `0.001424`, interaction R2 `0.09274`, residual variance `0.7921`.
- Task-specific continuous model-strength R2 values were small: simple games `0.007179`, TSP `0.0`, CVRP `0.002209`.
- Evolutionary techniques beat single-shot in 10 comparisons, but beat the budget-matched no-replay control in 0 comparisons.
- The strongest positive-looking raw signal was in CVRP for `strong_model + failure_replay`, but its paired comparison against `budget_matched_no_replay` did not have strictly positive bootstrap support.
- TSP had almost no meaningful endpoint variation across most cells, which limits what that task can contribute to model-strength or replay-effect claims in this final factorial.

## Technical Validity

The conclusions are not based on the final report alone.

They were checked against:

- `all_runs_long.raw.csv` and `all_runs_long.csv` for the full 750-row structure,
- `cell_means.csv` for task x model x technique means,
- `variance_partition_summary.csv` for semi-partial R2 summaries,
- `evolution_vs_single_shot_effects.csv` and `evolution_vs_budget_matched_effects.csv` for budget-control tests,
- lower-level candidate artifacts for fatal API, quota, queue-empty, and timeout-expired markers.

The main technical checks were:

- 150 simple-game rows, 300 TSP rows, and 300 CVRP rows were present.
- Each model tier had 250 rows.
- Each evolution technique had 150 rows.
- No row was missing `performance_raw` or `performance_z`.
- The official artifact set contained all required CSV, PNG, Markdown, and PDF outputs.
- No fatal API or runner crash markers were present in the completed artifact tree.

The final factorial is complete enough for interpretation as run, with the caveat that the report conclusion must be conservative.

## Interpretation

This phase separates three effects that were previously easy to conflate:

- base model tier,
- extra candidate-generation/search budget,
- replay or failure-memory mechanism.

The result is negative but informative. Replay-style mechanisms did not clear the correct budget-matched control, so they are not described as adding independent value in this final factorial. At the same time, model tier did not dominate pooled variance under the cheaper ladder, so the final interpretation does not attribute the results to base model strength alone.

The defensible final claim is:

> across the three benchmark families, LLM code evolution can generate and select executable heuristic programs, but the reliable advantage over one-shot generation mostly comes from search budget and task/model-specific interaction structure. Replay-specific mechanisms did not provide robust added value beyond budget-matched independent search in this campaign.

## Consequence For Interpretation

This result is reported as a measurement and limitation result rather than a positive algorithm-discovery result.

It supports the following reporting constraints:

- use budget-matched controls before claiming evolutionary or replay benefits,
- report failed mechanisms directly,
- separate task headroom from model strength,
- avoid interpreting novelty or extra API calls as algorithmic discovery.

The final synthesis connects this result back to the earlier cross-family interpretation: LLM-guided code evolution is best treated as a measurable adaptive search loop whose success depends on validator pressure, benchmark headroom, and baseline strength.

## Sources

- [Official factorial final report](../runs/cross_family_model_x_evolution_factorial/20260524_172130/final_report.md)
- [Official factorial final report PDF](../runs/cross_family_model_x_evolution_factorial/20260524_172130/final_report.pdf)
- [All runs long CSV](../runs/cross_family_model_x_evolution_factorial/20260524_172130/all_runs_long.csv)
- [Variance partition summary](../runs/cross_family_model_x_evolution_factorial/20260524_172130/variance_decomposition/variance_partition_summary.csv)
- [Budget-matched effect sizes](../runs/cross_family_model_x_evolution_factorial/20260524_172130/effect_sizes/evolution_vs_budget_matched_effects.csv)
