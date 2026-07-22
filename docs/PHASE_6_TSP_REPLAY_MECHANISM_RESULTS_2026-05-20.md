# Phase 6 TSP Replay Mechanism Results (2026-05-20)

This note records the official 20-offset phase-6 TSP replay-mechanism campaign.

The official artifact archive for this phase is the tagged `phase-6-replay-mechanism` state on branch `replay-mechanism`, under `runs/tsp_phase6_suite/replay_mechanism/aggregate_20260519_045055_t`.

## Headline

Phase 6 did not support the simple "broad replay coverage explains everything" story.

- `random_replay` remained slightly better than raw `failure_replay` on the paired transfer comparison, but not decisively.
- The best mean condition overall was `diversity_failure_replay`, not `random_replay`.
- Archive hardness predicted held-out TSPLIB gap more strongly than archive diversity.
- `residual_failure_replay` underperformed the naive raw-failure arm.
- Compression hurt both the random-replay arm and the best diversity-aware failure arm.

The strongest interpretation is therefore not "random replay wins because diversity alone matters most." The stronger interpretation is that naive raw-gap failure replay was too concentrated on hard cases, but replay curation still matters more than raw coverage alone.

## Main Findings

- Best mean combined transfer and held-out TSPLIB condition: `phase6_diversity_failure_replay`, with transfer gap `0.089519` and TSPLIB gap `0.132031`.
- `phase6_random_replay` versus `phase6_no_replay`: transfer delta `-0.003123`, 95% CI `[-0.027964, 0.021061]`; TSPLIB delta `-0.000293`, 95% CI `[-0.032786, 0.031526]`.
- `phase6_failure_replay` versus `phase6_random_replay`: transfer delta `0.001361`, 95% CI `[-0.022536, 0.025457]`; archive-diversity delta `-0.065566`; archive-hardness delta `0.128613`.
- `phase6_diversity_failure_replay` versus `phase6_failure_replay`: transfer delta `-0.008637`, 95% CI `[-0.035972, 0.017862]`; TSPLIB delta `-0.010644`, 95% CI `[-0.044114, 0.021829]`.
- `phase6_residual_failure_replay` versus `phase6_failure_replay`: transfer delta `0.022578`, 95% CI `[-0.005643, 0.04867]`; TSPLIB delta `0.030223`, 95% CI `[-0.004028, 0.062114]`.
- `phase6_random_replay_compression` versus `phase6_random_replay`: transfer delta `0.014874`; TSPLIB delta `0.018166`; novelty delta `-0.281412`; complexity delta `-0.03`.
- `phase6_diversity_failure_replay_compression` versus `phase6_diversity_failure_replay`: transfer delta `0.021526`; TSPLIB delta `0.029405`; novelty delta `-0.368327`; complexity delta `-0.02`.

## Diversity And Hardness Diagnostics

The archive-diversity diagnostic did not carry the mechanism explanation on its own.

- Diversity vs TSPLIB gap Pearson `r = -0.009478`
- Diversity vs TSPLIB gap Spearman `rho = -0.041013`
- Hardness vs TSPLIB gap Pearson `r = 0.39687`
- Hardness vs TSPLIB gap Spearman `rho = 0.371779`

Within this official campaign, archive hardness tracked held-out TSPLIB gap materially better than descriptor diversity did.

## Mechanism Answers

1. Why did `random_replay` beat `failure_replay`?

`random_replay` appears to have avoided the extra hardness and lower diversity induced by naive raw-gap failure replay. But the official results do not support the stronger claim that random coverage alone is the main driver. The best mean arm was `diversity_failure_replay`, which suggests that failure replay needed better curation rather than total abandonment.

2. Does replay-archive diversity explain transfer better than replay hardness?

No. In this campaign, hardness explained held-out TSPLIB gap better than diversity did.

3. Does compression help once applied to the best replay mechanism?

No. Compression reduced novelty sharply, but it worsened transfer on both `random_replay` and `diversity_failure_replay`.

4. Are the final heuristics genuinely different, or just differently tuned?

They look closer to differently tuned members of the same scaffold family than to cleanly different algorithm families. Complexity stayed tightly clustered at roughly `0.68` to `0.72`, while the larger movement was in accepted novelty and replay composition.

## Interpretation

Phase 6 is still scientifically useful. It narrows the mechanism claim:

- naive raw-failure replay is not the right default
- replay curation matters
- descriptor diversity by itself is not sufficient as the main explanation
- residual-failure replay, as implemented here, did not improve on raw failure replay

That makes phase 6 a negative-or-boundary mechanism result rather than a simple confirmation of the original coverage hypothesis.
