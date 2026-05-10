# Phase 4 Causal Transfer Update

This note summarizes the completed phase-4 causal-transfer replication.
It is based on:

- [baseline aggregate](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/rotating_opponents_holdout_endpoint/aggregate_20260510_072121/aggregate_report.md)
- [heavy aggregate](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/rotating_plus_nemesis_novelty_replay/aggregate_20260510_072124/aggregate_report.md)
- [replay-aware aggregate](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/rotating_plus_replay_aware_selection/aggregate_20260510_072126/aggregate_report.md)
- [paired causal-transfer report](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/causal_analysis_20260510_072803/causal_transfer_report.md)
- [manual novelty adjudication](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_4_NOVELTY_ADJUDICATION_2026-05-10.md)

The phase-4 dataset now includes ten live replicates for each transfer recipe, with the two superseded noisy reruns preserved separately under [runs/transfer_suite/_superseded](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/runs/transfer_suite/_superseded/).

## Main Quantitative Result

The strongest simple reference remained `rotating_opponents_holdout_endpoint`.
The strongest curriculum-heavy recipe remained `rotating_plus_nemesis_novelty_replay`.
`rotating_plus_replay_aware_selection` was added as the optional third arm and ended up close to the heavy recipe.

| Recipe | Overall transfer win rate | Overall transfer margin | Reading |
| --- | ---: | ---: | --- |
| `rotating_opponents_holdout_endpoint` | `0.5547` | `5.9663` | simpler reference condition |
| `rotating_plus_nemesis_novelty_replay` | `0.7231` | `11.6271` | highest overall transfer win rate |
| `rotating_plus_replay_aware_selection` | `0.7102` | `13.0733` | near the heavy recipe on win rate and slightly higher on mean margin |

The most important paired comparisons are:

| Comparison | Overall win-rate difference | Overall margin difference | Sign-test p | Reading |
| --- | ---: | ---: | ---: | --- |
| baseline vs heavy | `+0.1684` | `+5.6608` | `0.0215` | strongest replicated positive signal |
| baseline vs replay-aware | `+0.1556` | `+7.1070` | `0.5078` | positive mean gap, but less decisive paired sign pattern |
| heavy vs replay-aware | `-0.0129` | `+1.4462` to replay-aware | `0.2891` | broadly similar overall transfer performance |

The headline result therefore still holds after the larger paired-seed replication: the curriculum-heavy recipe transferred substantially better than the simpler rotating baseline.

## Failure-Mode Result

The transfer gains did not erase the failure-mode story.
Persistent weak archetypes across all three compared recipes were:

- `evasion_midline_dodge`
- `corner_guard`
- `diagonal_probe`
- `safe_collector`

This is useful, not embarrassing.
It means the result is better framed as uneven robustness with recipe-specific strengths and weaknesses, not universal competence.

## Functional Adaptation Versus Syntactic Novelty

The phase-4 report strengthens the distinction between lexical novelty and functional adaptation.

The strongest run-level correlations with primary transfer outcome were:

- `mean_descriptor_shift` vs primary win rate: `rho = 0.7598`
- `functional_adaptation_ratio` vs primary win rate: `rho = 0.7166`

The most important cautionary contrast is that raw code novelty was not a convincing explanation of baseline-relative transfer gain:

- `mean_code_novelty` vs `delta_vs_baseline_win_rate`: `rho = -0.0589`

The clearest negative proxies were:

- `superficial_novelty_rate`: `rho = -0.5923`
- `strategy_switch_rate`: `rho = -0.4631`

This is the core phase-4 conceptual result.
Transfer gain tracks behavior-centered adaptation proxies much better than raw code-change magnitude.

## Manual Novelty Review Result

The manual adjudication of the top ten novelty spikes per recipe found:

| Recipe | Functional adaptation | Mixed or local adjustment | Churn or failed adaptation |
| --- | ---: | ---: | ---: |
| baseline | `2/10` | `2/10` | `6/10` |
| heavy | `5/10` | `2/10` | `3/10` |
| replay-aware | `5/10` | `2/10` | `3/10` |

Two points matter here.

First, the heavy and replay-aware recipes do show more true functional adaptations among their strongest novelty spikes than the baseline does.

Second, even for those stronger recipes, the novelty spikes are still far from being uniformly innovative.
Many are mixed, local, or failed changes, and most of the clearest positive cases are concentrated in `territory_control`.

That means the novelty review still supports a restrained thesis.
The project now has evidence for adaptive functional change, but not evidence for broad, repeated strategic invention as the main driver of transfer.

## Safe Claims

These claims are now well supported by the phase-4 archive.

1. The transfer advantage of `rotating_plus_nemesis_novelty_replay` over the simpler rotating baseline replicated under a larger paired-seed design.
2. The transfer gains are environment- and archetype-specific rather than universal.
3. Behavior-centered proxies such as descriptor shift and functional-adaptation ratio explain transfer outcomes better than raw code novelty does.
4. The novelty review justifies careful language about functional adaptation, but not strong claims about widespread strategic innovation.

## Exploratory Claims

These are plausible but should still be presented as secondary or exploratory.

1. `rotating_plus_replay_aware_selection` may capture much of the heavy recipe's transfer benefit without matching its exact curriculum complexity.
2. A large share of the heavy recipe's advantage may be coming from better territorial adaptation plus replay-conditioned robustness rather than from novelty pressure by itself.

## Unsupported Claims

These claims should still be avoided.

1. The system became generally smarter in a domain-independent sense.
2. Large code changes by themselves caused the transfer improvements.
3. The novelty packets demonstrate broad strategic invention across environments.

## Recommended Supervisor Update

The cleanest update to send is:

The phase-4 replication is complete.
Across ten paired seeds, `rotating_plus_nemesis_novelty_replay` still transferred substantially better than the simpler `rotating_opponents_holdout_endpoint` baseline on the overall transfer endpoint, and `rotating_plus_replay_aware_selection` ended up close to the heavy recipe.
The most important conceptual result is that the transfer gain is better explained by broader functional adaptation and replay-conditioned robustness than by raw syntactic novelty.
The manual novelty review still shows that many large code changes are mixed or failed, and the remaining weaknesses against `evasion_midline_dodge`, `corner_guard`, `diagonal_probe`, and `safe_collector` show that the result is uneven robustness rather than universal competence.
