# Phase 4 Causal Transfer Analysis

## Scope
- Recipe roots analyzed: `runs/transfer_suite/rotating_opponents_holdout_endpoint`, `runs/transfer_suite/rotating_plus_nemesis_novelty_replay`, `runs/transfer_suite/rotating_plus_replay_aware_selection`.
- Recipes compared: Rotating opponents, Rotating + nemesis + novelty + replay, Rotating + replay-aware selection.
- Baseline recipe for delta metrics: `rotating_opponents_holdout_endpoint`.
- Condition observations: 90.
- Epoch-to-epoch transition rows: 8910.

## Reliability And Replication
- Rotating opponents overall transfer win rate: mean 0.5547 (95% CI 0.4336 to 0.6757; n=10); overall transfer margin: mean 5.9663 (95% CI 1.4844 to 10.4483; n=10).
- Rotating opponents on pursuit / evasion: win rate mean 0.4733 (95% CI 0.2604 to 0.6862; n=10); margin mean -0.4177 (95% CI -4.2727 to 3.4374; n=10).
- Rotating opponents on resource collection / denial: win rate mean 0.404 (95% CI 0.2812 to 0.5268; n=10); margin mean -0.22 (95% CI -2.2085 to 1.7685; n=10).
- Rotating opponents on territory control: win rate mean 0.7867 (95% CI 0.5771 to 0.9963; n=10); margin mean 18.5367 (95% CI 7.7923 to 29.2811; n=10).
- Rotating + nemesis + novelty + replay overall transfer win rate: mean 0.7231 (95% CI 0.7037 to 0.7425; n=10); overall transfer margin: mean 11.6271 (95% CI 9.4761 to 13.7781; n=10).
- Rotating + nemesis + novelty + replay on pursuit / evasion: win rate mean 0.72 (95% CI 0.6656 to 0.7744; n=10); margin mean 4.074 (95% CI 3.0943 to 5.0537; n=10).
- Rotating + nemesis + novelty + replay on resource collection / denial: win rate mean 0.476 (95% CI 0.4348 to 0.5172; n=10); margin mean 1.184 (95% CI 0.723 to 1.645; n=10).
- Rotating + nemesis + novelty + replay on territory control: win rate mean 0.9733 (95% CI 0.952 to 0.9947; n=10); margin mean 29.6233 (95% CI 23.6851 to 35.5615; n=10).
- Rotating + replay-aware selection overall transfer win rate: mean 0.7102 (95% CI 0.6799 to 0.7406; n=10); overall transfer margin: mean 13.0733 (95% CI 10.7589 to 15.3878; n=10).
- Rotating + replay-aware selection on pursuit / evasion: win rate mean 0.7 (95% CI 0.6347 to 0.7653; n=10); margin mean 3.702 (95% CI 2.5161 to 4.8879; n=10).
- Rotating + replay-aware selection on resource collection / denial: win rate mean 0.484 (95% CI 0.45 to 0.518; n=10); margin mean 1.348 (95% CI 0.9859 to 1.7101; n=10).
- Rotating + replay-aware selection on territory control: win rate mean 0.9467 (95% CI 0.904 to 0.9893; n=10); margin mean 34.17 (95% CI 27.5863 to 40.7537; n=10).

| Comparison | Scope | Left win | Right win | Win diff | Sign p | Left margin | Right margin | Margin diff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rotating opponents vs Rotating + nemesis + novelty + replay | pursuit / evasion | 0.4733 | 0.72 | 0.2467 | 0.4531 | -0.4177 | 4.074 | 4.4917 |
| Rotating opponents vs Rotating + nemesis + novelty + replay | resource collection / denial | 0.404 | 0.476 | 0.072 | 0.5078 | -0.22 | 1.184 | 1.404 |
| Rotating opponents vs Rotating + nemesis + novelty + replay | territory control | 0.7867 | 0.9733 | 0.1867 | 0.375 | 18.5367 | 29.6233 | 11.0867 |
| Rotating opponents vs Rotating + nemesis + novelty + replay | overall transfer average | 0.5547 | 0.7231 | 0.1684 | 0.0215 | 5.9663 | 11.6271 | 5.6608 |
| Rotating opponents vs Rotating + replay-aware selection | pursuit / evasion | 0.4733 | 0.7 | 0.2267 | 0.7266 | -0.4177 | 3.702 | 4.1197 |
| Rotating opponents vs Rotating + replay-aware selection | resource collection / denial | 0.404 | 0.484 | 0.08 | 0.7266 | -0.22 | 1.348 | 1.568 |
| Rotating opponents vs Rotating + replay-aware selection | territory control | 0.7867 | 0.9467 | 0.16 | 1.0 | 18.5367 | 34.17 | 15.6334 |
| Rotating opponents vs Rotating + replay-aware selection | overall transfer average | 0.5547 | 0.7102 | 0.1556 | 0.5078 | 5.9663 | 13.0733 | 7.107 |
| Rotating + nemesis + novelty + replay vs Rotating + replay-aware selection | pursuit / evasion | 0.72 | 0.7 | -0.02 | 1.0 | 4.074 | 3.702 | -0.372 |
| Rotating + nemesis + novelty + replay vs Rotating + replay-aware selection | resource collection / denial | 0.476 | 0.484 | 0.008 | 1.0 | 1.184 | 1.348 | 0.164 |
| Rotating + nemesis + novelty + replay vs Rotating + replay-aware selection | territory control | 0.9733 | 0.9467 | -0.0267 | 0.625 | 29.6233 | 34.17 | 4.5467 |
| Rotating + nemesis + novelty + replay vs Rotating + replay-aware selection | overall transfer average | 0.7231 | 0.7102 | -0.0129 | 0.2891 | 11.6271 | 13.0733 | 1.4462 |

## Failure Modes
- Holdout rows are reported as `mean win rate / mean score margin` across replicates.
- Persistent weak archetypes across all compared recipes: `pursuit / evasion / evasion_midline_dodge`, `resource collection / denial / corner_guard`, `resource collection / denial / diagonal_probe`, `resource collection / denial / safe_collector`.
- Largest win-rate improvements relative to the baseline appeared in `pursuit / evasion / evasion_axis_flip` for Rotating + nemesis + novelty + replay (+0.400 win rate), `pursuit / evasion / evasion_center_weave` for Rotating + nemesis + novelty + replay (+0.300 win rate), `territory control / territory_far_corner_claim` for Rotating + nemesis + novelty + replay (+0.280 win rate), `resource collection / denial / safe_collector` for Rotating + replay-aware selection (+0.180 win rate), `territory control / territory_diagonal_claim` for Rotating + nemesis + novelty + replay (+0.160 win rate).

### pursuit / evasion
| Holdout archetype | Rotating opponents win/margin | Rotating + nemesis + novelty + replay win/margin | Rotating + replay-aware selection win/margin |
| --- | --- | --- | --- |
| evasion_axis_flip | 0.6 / 1.848 | 1.0 / 9.07 | 0.98 / 8.711 |
| evasion_center_weave | 0.52 / 0.532 | 0.82 / 6.061 | 0.8 / 5.687 |
| evasion_midline_dodge | 0.3 / -3.633 | 0.34 / -2.909 | 0.32 / -3.292 |

### resource collection / denial
| Holdout archetype | Rotating opponents win/margin | Rotating + nemesis + novelty + replay win/margin | Rotating + replay-aware selection win/margin |
| --- | --- | --- | --- |
| center_rush | 0.36 / -0.54 | 0.5 / 0.86 | 0.46 / 0.98 |
| corner_guard | 0.36 / -0.9 | 0.28 / 0.16 | 0.36 / 0.38 |
| diagonal_probe | 0.36 / -1.6 | 0.4 / -0.02 | 0.38 / 0.26 |
| edge_patrol | 0.82 / 4.12 | 0.92 / 5.3 | 0.92 / 5.42 |
| safe_collector | 0.12 / -2.18 | 0.28 / -0.38 | 0.3 / -0.3 |

### territory control
| Holdout archetype | Rotating opponents win/margin | Rotating + nemesis + novelty + replay win/margin | Rotating + replay-aware selection win/margin |
| --- | --- | --- | --- |
| territory_diagonal_claim | 0.82 / 22.27 | 0.98 / 31.34 | 0.98 / 35.99 |
| territory_far_corner_claim | 0.68 / 13.41 | 0.96 / 27.92 | 0.86 / 22.8 |
| territory_quadrant_claim | 0.86 / 19.93 | 0.98 / 29.61 | 1.0 / 43.72 |

## Behavioral Interpretation
- `mean_code_novelty` is the average lexical code-change magnitude across consecutive epochs.
- `mean_descriptor_shift` is the average behavioral-descriptor distance across consecutive epochs.
- `strategy_switch_count`, `behavior_cell_count`, and `specific_adaptation_count` are the main proxies for stable adaptive motifs in this report.

- All transitions: novelty vs descriptor shift -> rho 0.2412 (n=8910).
- Accepted transitions only: novelty vs descriptor shift -> rho 0.2503 (n=4902).
- Strongest positive transfer correlates in this dataset: mean_descriptor_shift (0.7598), functional_adaptation_ratio (0.7166).
- Strongest negative transfer correlates in this dataset: superficial_novelty_rate (-0.5923), strategy_switch_rate (-0.4631).

| Feature proxy | Outcome | Spearman rho | N |
| --- | --- | --- | --- |
| mean_code_novelty | primary_win_rate | 0.5735 | 90 |
| mean_code_novelty | primary_margin | 0.6051 | 90 |
| mean_code_novelty | delta_vs_baseline_win_rate | -0.0589 | 60 |
| mean_code_novelty | delta_vs_baseline_margin | 0.1823 | 60 |
| mean_descriptor_shift | primary_win_rate | 0.7598 | 90 |
| mean_descriptor_shift | primary_margin | 0.7661 | 90 |
| mean_descriptor_shift | delta_vs_baseline_win_rate | 0.0773 | 60 |
| mean_descriptor_shift | delta_vs_baseline_margin | 0.3645 | 60 |
| functional_adaptation_ratio | primary_win_rate | 0.7166 | 90 |
| functional_adaptation_ratio | primary_margin | 0.7198 | 90 |
| functional_adaptation_ratio | delta_vs_baseline_win_rate | 0.0635 | 60 |
| functional_adaptation_ratio | delta_vs_baseline_margin | 0.3467 | 60 |
| strategy_switch_rate | primary_win_rate | -0.4631 | 90 |
| strategy_switch_rate | primary_margin | -0.4477 | 90 |
| strategy_switch_rate | delta_vs_baseline_win_rate | -0.0995 | 60 |
| strategy_switch_rate | delta_vs_baseline_margin | -0.2427 | 60 |
| behavior_cell_count | primary_win_rate | -0.255 | 90 |
| behavior_cell_count | primary_margin | -0.1692 | 90 |
| behavior_cell_count | delta_vs_baseline_win_rate | -0.0718 | 60 |
| behavior_cell_count | delta_vs_baseline_margin | -0.0543 | 60 |
| specific_adaptation_rate | primary_win_rate | 0.1086 | 90 |
| specific_adaptation_rate | primary_margin | 0.148 | 90 |
| specific_adaptation_rate | delta_vs_baseline_win_rate | 0.0121 | 60 |
| specific_adaptation_rate | delta_vs_baseline_margin | 0.0983 | 60 |
| superficial_novelty_rate | primary_win_rate | -0.5923 | 90 |
| superficial_novelty_rate | primary_margin | -0.6351 | 90 |
| superficial_novelty_rate | delta_vs_baseline_win_rate | 0.0679 | 60 |
| superficial_novelty_rate | delta_vs_baseline_margin | -0.2133 | 60 |
| post_loss_novelty_spike_rate | primary_win_rate | 0.0873 | 90 |
| post_loss_novelty_spike_rate | primary_margin | 0.0643 | 90 |
| post_loss_novelty_spike_rate | delta_vs_baseline_win_rate | 0.0972 | 60 |
| post_loss_novelty_spike_rate | delta_vs_baseline_margin | -0.0488 | 60 |

## Interpretation Guardrails
- These correlations are exploratory and should not be treated as causal proof on their own.
- The behavioral descriptors remain heuristic proxies, but they are closer to functional adaptation than lexical code novelty alone.
- Paired-seed transfer comparisons should be weighted more heavily than unpaired aggregate differences.
- Persistent weak archetypes are scientifically useful evidence of uneven robustness, not a nuisance to be hidden.
