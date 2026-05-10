# Phase 4 Novelty Adjudication

This note records the manual review requested for the top novelty spikes in the three phase-4 transfer recipes.
It cross-checks the generated packets:

- [baseline novelty packet](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/novelty_review_baseline_20260510_073503/novelty_review.md)
- [heavy novelty packet](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/novelty_review_heavy_20260510_073503/novelty_review.md)
- [replay-aware novelty packet](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/novelty_review_replay_aware_20260510_073503/novelty_review.md)

The goal is not to re-score novelty mechanically. The goal is to decide whether the strongest lexical code changes look like:

1. true functional adaptation
2. mixed or local adjustment
3. churn or failed adaptation

The decision rule used here is conservative:

- `Functional adaptation`: the code change is accompanied by a meaningful behavioral shift and a meaningful score or margin improvement.
- `Mixed or local adjustment`: the change affects behavior or local score, but the evidence for robust functional gain is incomplete or contradictory.
- `Churn or failed adaptation`: the code changes substantially, but performance is flat, negative, or behaviorally shallow.

## Summary Counts

| Recipe | Functional adaptation | Mixed or local adjustment | Churn or failed adaptation |
| --- | ---: | ---: | ---: |
| `rotating_opponents_holdout_endpoint` | `2/10` | `2/10` | `6/10` |
| `rotating_plus_nemesis_novelty_replay` | `5/10` | `2/10` | `3/10` |
| `rotating_plus_replay_aware_selection` | `5/10` | `2/10` | `3/10` |

The main pattern is that the heavier and replay-aware recipes show more genuine functional adaptations among their strongest novelty spikes than the baseline does, but the novelty packets still do not justify a claim of broad strategic invention.

## Rotating Opponents Baseline

| Case | Manual call | Reason |
| --- | --- | --- |
| `transfer_territory_control / epoch 53 / run_20260507_210350_b` | `functional adaptation` | Large positive score and margin gain inside the same territorial motif, which looks like within-family functional retuning rather than pure churn. |
| `transfer_territory_control / epoch 37 / run_20260507_201051_a` | `churn or failed adaptation` | Large code and descriptor change, but both score and margin worsened. |
| `transfer_resource_collection_denial / epoch 57 / run_20260507_220338_c` | `churn or failed adaptation` | Resource-collection behavior stayed in the same motif and performance fell slightly. |
| `transfer_resource_collection_denial / epoch 3 / run_20260507_234515_e` | `mixed or local adjustment` | Positive local score and margin gain, but descriptor shift stayed small and the behavior motif did not clearly change. |
| `transfer_resource_collection_denial / epoch 2 / run_20260507_225407_d` | `churn or failed adaptation` | Small behavioral movement with worse score and margin. |
| `transfer_territory_control / epoch 11 / run_20260509_002410_i` | `churn or failed adaptation` | Large apparent strategy move from `static_guard` to `claimer`, but the result was strongly negative. |
| `transfer_territory_control / epoch 4 / run_20260509_094819_f` | `mixed or local adjustment` | Absolute score rose sharply, but relative margin still fell, so the functional gain is not clean. |
| `transfer_territory_control / epoch 77 / run_20260508_205712_g` | `functional adaptation` | Clear profile shift from `static_guard` to `balanced` plus strong margin improvement. |
| `transfer_resource_collection_denial / epoch 12 / run_20260507_234515_e` | `churn or failed adaptation` | Same behavioral family, modest descriptor movement, and worse performance. |
| `transfer_resource_collection_denial / epoch 73 / run_20260507_225407_d` | `churn or failed adaptation` | Profile moved toward `interceptor`, but the change lost score and margin and does not show useful transfer evidence. |

## Rotating + Nemesis + Novelty + Replay

| Case | Manual call | Reason |
| --- | --- | --- |
| `transfer_territory_control / epoch 54 / run_20260509_103847_j` | `functional adaptation` | Strong profile shift and very large score and margin gain. |
| `transfer_territory_control / epoch 42 / run_20260507_145614_b` | `functional adaptation` | Clear move from `balanced` to `claimer` with a large territorial performance gain. |
| `transfer_territory_control / epoch 87 / run_20260507_145614_b` | `mixed or local adjustment` | Score rose, but margin still dipped slightly and the visible behavior family stayed the same. |
| `transfer_territory_control / epoch 82 / run_20260507_145614_b` | `functional adaptation` | Large move from `balanced` to `static_guard` with strong positive payoff. |
| `transfer_pursuit_evasion / epoch 87 / run_20260509_011052_i` | `churn or failed adaptation` | High lexical novelty with no score or margin gain. |
| `transfer_territory_control / epoch 64 / run_20260507_145614_b` | `functional adaptation` | Very large behavioral and payoff change from `static_guard` to `claimer`. |
| `transfer_resource_collection_denial / epoch 82 / run_20260509_103847_j` | `mixed or local adjustment` | Mild but positive improvement in the same resource-collection family; useful, but not strong enough to call a major functional change. |
| `transfer_territory_control / epoch 72 / run_20260507_155959_c` | `functional adaptation` | Large shift toward `claimer` with strong territorial payoff. |
| `transfer_territory_control / epoch 67 / run_20260509_011052_i` | `churn or failed adaptation` | Large code change and descriptor movement, but score and margin both fell. |
| `transfer_resource_collection_denial / epoch 21 / run_20260508_233016_h` | `churn or failed adaptation` | Mostly lexical movement with lower score and margin. |

## Rotating + Replay-Aware Selection

| Case | Manual call | Reason |
| --- | --- | --- |
| `transfer_territory_control / epoch 49 / run_20260510_005204_d` | `churn or failed adaptation` | Same territorial family with worse score and margin. |
| `transfer_pursuit_evasion / epoch 15 / run_20260510_043943_i` | `mixed or local adjustment` | Real behavioral shift toward `static_guard`, but no observable payoff change. |
| `transfer_territory_control / epoch 78 / run_20260509_231935_b` | `functional adaptation` | Large move into a stronger territorial regime with major score and margin gains. |
| `transfer_pursuit_evasion / epoch 23 / run_20260510_035354_h` | `churn or failed adaptation` | Lexical change with no score or margin improvement. |
| `transfer_territory_control / epoch 11 / run_20260510_052825_j` | `functional adaptation` | Clear move from `static_guard` to `claimer` with strong margin improvement. |
| `transfer_territory_control / epoch 62 / run_20260510_005204_d` | `functional adaptation` | Strong shift from `balanced` to `static_guard` plus strong payoff gain. |
| `transfer_territory_control / epoch 84 / run_20260509_231935_b` | `functional adaptation` | Same broad motif, but a real and useful territorial retuning with positive score and margin gain. |
| `transfer_resource_collection_denial / epoch 8 / run_20260510_052825_j` | `churn or failed adaptation` | Profile changed, but the move reduced both score and margin. |
| `transfer_pursuit_evasion / epoch 14 / run_20260510_000504_c` | `mixed or local adjustment` | There is a real pursuit/evasion style change, but no payoff difference in that epoch. |
| `transfer_pursuit_evasion / epoch 42 / run_20260510_035354_h` | `functional adaptation` | Clear move from `static_guard` to `tagger` with a strong positive margin shift. |

## Interpretation

Three conclusions matter for the phase-4 thesis framing.

First, the baseline packet is still dominated by mixed or failed novelty spikes. That means the simpler rotating-opponent recipe does not show a strong case that its biggest lexical changes were reliable functional improvements.

Second, the heavy and replay-aware recipes do show more genuine functional adaptations, but these are concentrated mostly in `territory_control` and only occasionally in the other environments. The functional gains are therefore real but uneven, not universal.

Third, even the stronger recipes still contain several large code changes that are mixed or negative. That supports a restrained claim: the extra curriculum machinery appears to help produce more useful adaptive adjustments, but the evidence still does not justify saying that the system broadly invents new high-level strategies whenever code novelty spikes.
