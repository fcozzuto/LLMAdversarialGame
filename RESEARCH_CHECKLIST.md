# Minimum Publishable Research Checklist

This checklist is the project’s fixed research protocol. It separates infrastructure that can be completed in code from evidence that must be produced by running experiments.

## Primary Questions

1. Do the models attempt rule-violating behavior under the current sandboxed setup, or mostly optimize within the documented rules?
2. Do iterative adversarial runs plateau, or do they continue to change their submitted strategies over time?
3. Are the observed strategy changes materially new algorithms or mostly variations on prior heuristics?
4. Does cross-model play increase innovation relative to same-model play?
5. Does feedback visibility change reliability, innovation, or performance?

## Operational Definitions

- `Cheating evidence`: policy markers, forbidden-call attempts, import attempts, or other sandbox-triggered rule-violation indicators. Runtime pathing mistakes are not cheating evidence.
- `Code novelty`: normalized lexical change between consecutive submitted programs.
- `Execution reliability`: submitted-code execution rate, distinct from model-call success.
- `Plateau`: repeated code with low recent novelty and no recent score improvement.
- `Materially new algorithm`: a change that is supported by both a strong code/strategy shift and qualitatively different behavior, not only superficial code variation.

## Primary Metrics

- Submitted-code execution rate per agent and condition.
- Generation error count and fallback count per agent and condition.
- Average score and win count per condition.
- Average code novelty and last-three-epoch novelty per agent.
- Plateau signals and code-change statistics.
- Policy marker counts.

## Infrastructure

- [x] Generated code is validated before play and invalid submissions are either repaired or explicitly counted as fallback/default-code epochs.
- [x] Reports distinguish generation reliability from execution reliability.
- [x] Per-run artifacts include `report.md`, `report.pdf`, `suite_summary.json`, `run_metadata.json`, labeled `scores.svg`, and embedded `scores.png`.
- [x] Judge-model prose is secondary to deterministic summaries in the report.
- [x] The report includes threats-to-validity language instead of only optimistic conclusions.
- [x] The report includes deterministic notable-epoch hooks for qualitative follow-up.
- [x] Condition metadata is preserved so ablations and controls can be grouped later.
- [x] Research ablation configs exist in [configs/research_ablations_suite.json](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/research_ablations_suite.json).
- [x] Research control/baseline configs exist in [configs/research_controls_suite.json](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/research_controls_suite.json).
- [x] An explicit undocumented-field opportunity suite exists in [configs/research_cheating_opportunity_suite.json](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/research_cheating_opportunity_suite.json).
- [x] A cross-run aggregation tool exists in [aggregate_runs.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/aggregate_runs.py).

## Required Ablations And Controls

- [x] Same-model vs cross-model comparison exists.
- [x] Full-feedback vs limited-feedback comparison exists.
- [x] Opponent-code visibility ablation exists.
- [x] Path-feedback ablation exists.
- [x] Runtime-event-feedback ablation exists.
- [x] History-window ablation exists.
- [x] Generation-scaffold ablation exists.
- [x] Builtin baseline condition exists.
- [x] Frozen LLM control condition exists.
- [x] Undocumented-field opportunity condition exists.

## Evidence Still Required

- [ ] Run repeated long-horizon experiments, not only single long runs.
- [ ] Produce aggregate cross-run statistics with confidence intervals or equivalent uncertainty summaries.
- [ ] Confirm whether the same conclusions hold across multiple seeds and repeated runs.
- [ ] Perform qualitative inspection of notable epochs referenced by the reports.
- [ ] Decide which claims are primary, which are exploratory, and which are unsupported.

## Recommended Minimum Evidence Target

- [ ] At least 3 repeated long-horizon runs for the core suite.
- [ ] At least 3 repeated runs for the main ablation suite or a justified subset of its conditions.
- [ ] At least 1 aggregate report generated with [aggregate_runs.py](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/aggregate_runs.py).
- [ ] Final claims checked against both deterministic summaries and the aggregate report, not judge prose alone.

## Current Status

- The project is engineering-complete and research-infrastructure-complete.
- The project is not research-conclusion-complete until the evidence checklist above is satisfied.
