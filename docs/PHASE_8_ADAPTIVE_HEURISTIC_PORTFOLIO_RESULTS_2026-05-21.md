# Phase 8 Adaptive Heuristic Portfolio Results (2026-05-21)

This note records the official 20-offset phase-8 adaptive heuristic portfolio campaign.

The official artifact archive for this phase is under `runs/tsp_phase8_suite/adaptive_portfolio/aggregate_20260521_003344_t`.

## Headline

Phase 8 produced a technically valid adaptive-controller study, but it did not deliver a strong positive portfolio-selection win on the primary held-out TSPLIB endpoint.

- The campaign is technically valid: 20 paired runs, 8 conditions, judge enabled in all 20 runs, and only 3 replay-controller generation-error epochs across the whole campaign.
- Those 3 error epochs were all rejected epochs. No accepted final controller depended on fallback behavior.
- The best held-out TSPLIB condition was `phase8_best_single_fixed_heuristic`.
- `phase8_oracle_selector` and `phase8_supervised_ml_selector` tied the best fixed heuristic on the primary held-out TSPLIB endpoint.
- `phase8_llm_evolved_adaptive_controller` beat `phase8_llm_static_selector`, so iterative adaptive-controller search did learn something beyond a one-shot LLM rule baseline.
- `phase8_llm_evolved_controller_diversity_failure_replay` did not improve over the no-replay adaptive controller.

The right interpretation is therefore:

> phase 8 shows modest, interpretable adaptive-control learning over a weak LLM rule baseline, but no win over the strongest fixed or supervised baselines because the frozen portfolio had essentially no oracle headroom on held-out TSPLIB.

## Main Findings

- Best mean held-out TSPLIB condition: `phase8_best_single_fixed_heuristic`, mean gap `0.07226`.
- `phase8_oracle_selector` versus `phase8_best_single_fixed_heuristic`: held-out TSPLIB delta `0.0`, 95% CI `[0.0, 0.0]`; transfer-gap delta `-0.004544`.
- `phase8_supervised_ml_selector` versus `phase8_best_single_fixed_heuristic`: held-out TSPLIB delta `0.0`, 95% CI `[0.0, 0.0]`; transfer-gap delta `0.0`, 95% CI `[0.0, 0.0]`.
- `phase8_random_portfolio` versus `phase8_best_single_fixed_heuristic`: held-out TSPLIB delta `+0.119683`, 95% CI `[0.108269, 0.130787]`.
- `phase8_llm_static_selector` versus `phase8_supervised_ml_selector`: held-out TSPLIB delta `+0.121255`, 95% CI `[0.099278, 0.140226]`.
- `phase8_llm_evolved_adaptive_controller` versus `phase8_llm_static_selector`: held-out TSPLIB delta `-0.038118`, 95% CI `[-0.06868, -0.00707]`; selector-regret delta `-0.038118`, 95% CI `[-0.068547, -0.006883]`.
- `phase8_llm_evolved_controller_diversity_failure_replay` versus `phase8_llm_evolved_adaptive_controller`: held-out TSPLIB delta `+0.010114`, 95% CI `[-0.020641, 0.041674]`; selector-regret delta `+0.010114`, 95% CI `[-0.02087, 0.041393]`.
- `phase8_full_solver_evolution` versus `phase8_llm_evolved_adaptive_controller`: held-out TSPLIB delta `+0.011853`, 95% CI `[-0.025032, 0.049041]`; transfer-gap delta `+0.026893`, 95% CI `[-0.004858, 0.059364]`; runtime-adjusted-gap delta `-0.106561`.

## Technical Validity

The phase-8 conclusions are not based on the aggregate report alone.

They were checked against:

- the aggregate report and `aggregate_summary.json` for means, paired deltas, and intervals
- all 20 `suite_summary.json` and `run_metadata.json` files for structural validity
- lower-level condition and epoch artifacts for the adaptive-controller arms

The main technical checks were:

- 20 paired runs were present under `runs/tsp_phase8_suite/adaptive_portfolio`
- all 8 conditions were present in every run
- judge status was `enabled` in all 20 runs
- `phase8_llm_static_selector` remained instance-conditioned only rather than using online state
- the replay-aware adaptive controller had only 3 generation-error epochs across the whole campaign, and all 3 were rejected rather than accepted

So the campaign is scientifically usable as run. There is no hidden fallback collapse analogous to the invalid early phase-7 run.

## Interpretation

Phase 8 supports a narrower, more defensible claim than a full positive algorithm-selection win.

- The LLM adaptive controller can improve over a weaker one-shot LLM static selector.
- It did not beat the best fixed heuristic on held-out TSPLIB.
- It did not beat the supervised non-LLM selector on the primary endpoint.
- Replay did not help the adaptive controller.

The most important structural result is that the oracle selector tied the best fixed heuristic on held-out TSPLIB. In algorithm-selection terms, that means the current frozen portfolio has essentially zero single-best-versus-oracle gap on the primary endpoint. If the oracle does not beat the single best method, then a learned selector cannot be expected to produce a strong positive selector-regret result there.

That suggests the phase-8 bottleneck is not only controller learning. It is also portfolio complementarity on the chosen endpoint.

There is still a small transfer signal outside the primary endpoint: the oracle was slightly better than the best fixed heuristic on the synthetic-family transfer metric. So the current portfolio is not uselessly redundant everywhere. But on the main held-out TSPLIB panel, the selector headroom is effectively absent.

## Consequence For Follow-Up Work

If a follow-up selector phase is attempted, it should first create nontrivial selector headroom.

The bounded next step would be:

- enrich the frozen portfolio with heuristics that are deliberately complementary on the held-out regime, or
- evaluate selector performance on regime splits where the oracle already beats the single best heuristic by a meaningful amount

Without that, another selector campaign is unlikely to beat the strongest fixed baseline on the primary endpoint, regardless of how sophisticated the controller is.

## Sources

- [Phase 8 aggregate report](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_phase8_suite/adaptive_portfolio/aggregate_20260521_003344_t/aggregate_report.md)
- [Phase 8 aggregate summary JSON](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_phase8_suite/adaptive_portfolio/aggregate_20260521_003344_t/aggregate_summary.json)
- [Phase 8 final run suite summary](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_phase8_suite/adaptive_portfolio/run_20260521_003344_t/suite_summary.json)
- Representative adaptive-controller artifacts under [runs/tsp_phase8_suite/adaptive_portfolio](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/tsp_phase8_suite/adaptive_portfolio)
