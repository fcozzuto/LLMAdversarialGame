# Phase 7 TSP Operator Discovery Results (2026-05-20)

This note records the official 20-offset phase-7 modular operator-discovery campaign.

The official artifact archive for this phase is under `runs/tsp_phase7_suite/operator_discovery/aggregate_20260520_085349_t`.

## Headline

Phase 7 produced real operator diversity and nontrivial rediscovery structure, but no operator survived the full validation pipeline.

- The campaign is technically valid: 20 paired runs, 800 modular epochs, zero modular generation fallbacks, zero materialization fallbacks, and zero `missing_build_operator` errors.
- `full_solver_evolution` was the best overall transfer condition.
- No modular condition beat `full_solver_evolution` on held-out TSPLIB gap.
- No discovered operator survived transplant, ablation, family-holdout, and Pareto validation simultaneously.

The correct interpretation is therefore that phase 7 acted as a strong falsification filter, not a positive operator-discovery result.

## Main Findings

- Best mean overall condition: `phase7_full_solver_evolution`, with transfer gap `0.117916` and TSPLIB gap `0.164668`.
- Best mean modular transfer condition: `phase7_modular_operator_random_replay`, with transfer gap `0.118833`.
- Best mean modular TSPLIB condition: `phase7_modular_operator_random_replay`, with TSPLIB gap `0.230474`.
- `phase7_modular_operator_evolution` versus `phase7_baseline_heuristic_only`: transfer delta `-0.001715`, 95% CI `[-0.003418, 0.000085]`; TSPLIB delta `-0.003035`, 95% CI `[-0.010147, 0.000716]`.
- `phase7_modular_operator_evolution` versus `phase7_full_solver_evolution`: transfer delta `0.001686`, 95% CI `[-0.018321, 0.022827]`; TSPLIB delta `0.067355`, 95% CI `[0.040498, 0.094769]`.
- `phase7_modular_operator_random_replay` versus `phase7_modular_operator_evolution`: transfer delta `-0.000768`, 95% CI `[-0.002519, 0.000889]`.
- `phase7_modular_operator_diversity_residual_replay` versus `phase7_modular_operator_random_replay`: transfer delta `0.003009`, 95% CI `[-0.002884, 0.010797]`.
- `phase7_modular_operator_compression_pressure` versus `phase7_modular_operator_evolution`: transfer delta `-0.000737`, 95% CI `[-0.004573, 0.002479]`; novelty delta `-0.244329`.
- `phase7_modular_operator_pareto_selection` versus `phase7_modular_operator_evolution`: transfer delta `0.006411`, 95% CI `[0.001983, 0.012533]`; runtime-inflation delta `-1.605126`.

## Validation Outcome

No candidate satisfied the conservative `surviving_candidate` rule.

That means no operator simultaneously showed:

- positive transplant evidence across the scaffold set
- a clear family-level gain
- acceptable runtime/Pareto behavior
- ablation evidence that the operator itself mattered

The modular track therefore did not produce a reusable operator claim.

## Rediscovery Outcome

Rediscovery was real, but it did not turn into validated discovery.

- Distinct rediscovery signatures: `56`
- Most common signature: `perturbation:double_bridge:segment_reversal:3:3`
- Most common surviving signature: `None`

Repeated families included perturbation operators, restart controllers, candidate pruners, scaffold selectors, and some candidate-ranker variants. That suggests algorithmic attractors in the search space, but not validated reusable operators.

## Interpretation

Phase 7 produced a negative or boundary result that is still scientifically useful.

- The modular operator pipeline is functioning as intended after the operator-specific generation-path fix.
- The pipeline is capable of generating diverse operator proposals and recurring operator families.
- Under the current scaffold set and validation rules, none of those operators justified a discovery claim.

This means phase 7 currently supports a stronger methodological claim than a positive discovery claim:

> the validation pipeline is strict enough to reject brittle or purely host-scaffold-specific operator artifacts.

That is a meaningful outcome for the research program, even though the ambitious discovery win condition was not met in this campaign.
