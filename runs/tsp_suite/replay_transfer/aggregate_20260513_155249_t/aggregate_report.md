# Replay-Aware TSP Aggregate Report

## Overview
- Run count: 20.
- Condition count: 4.
- Best mean transfer gap: `tsplib_random_replay`.

## Condition Comparison
| Condition | Mean Transfer Gap | Mean TSPLIB Gap | Mean Synthetic Gap | Mean Accepted Novelty | Mean Complexity | Mean Adaptation Efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tsplib_failure_replay | 0.130918 | 0.18132 | 0.042713 | 0.806087 | 0.631 | -8.5e-05 |
| tsplib_failure_replay_compression | 0.124895 | 0.177578 | 0.032698 | 0.286629 | 0.67 | 0.015348 |
| tsplib_no_replay | 0.132474 | 0.183325 | 0.043485 | 0.742512 | 0.63 | -0.01061 |
| tsplib_random_replay | 0.104243 | 0.152211 | 0.0203 | 0.736465 | 0.7 | 0.025089 |

## Bootstrap Confidence Intervals
### tsplib_failure_replay
- Transfer gap 95% CI: `0.111752` to `0.148278`.
- TSPLIB gap 95% CI: `0.158054` to `0.201666`.
- Synthetic gap 95% CI: `0.029212` to `0.055179`.
- Mean accepted novelty 95% CI: `0.708909` to `0.868262`.
### tsplib_failure_replay_compression
- Transfer gap 95% CI: `0.106918` to `0.141737`.
- TSPLIB gap 95% CI: `0.155253` to `0.19875`.
- Synthetic gap 95% CI: `0.019743` to `0.045373`.
- Mean accepted novelty 95% CI: `0.13723` to `0.445475`.
### tsplib_no_replay
- Transfer gap 95% CI: `0.113762` to `0.14929`.
- TSPLIB gap 95% CI: `0.160588` to `0.203404`.
- Synthetic gap 95% CI: `0.030349` to `0.055951`.
- Mean accepted novelty 95% CI: `0.617775` to `0.839715`.
### tsplib_random_replay
- Transfer gap 95% CI: `0.08686` to `0.122292`.
- TSPLIB gap 95% CI: `0.130868` to `0.173495`.
- Synthetic gap 95% CI: `0.007626` to `0.033284`.
- Mean accepted novelty 95% CI: `0.643003` to `0.797918`.

## Paired Comparisons
Negative delta favors the candidate for transfer gap, benchmark gap, synthetic gap, novelty, and complexity. Positive delta favors the candidate for adaptation efficiency.

| Comparison | Paired Runs | Transfer Delta | Transfer 95% CI | TSPLIB Delta | TSPLIB 95% CI | Novelty Delta | Complexity Delta | Adaptation Delta |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: |
| tsplib_random_replay vs tsplib_no_replay | 20 | -0.028231 | `-0.052034` to `-0.002934` | -0.031114 | `-0.060232` to `-0.000821` | -0.006048 | 0.07 | 0.035699 |
| tsplib_failure_replay vs tsplib_no_replay | 20 | -0.001556 | `-0.023279` to `0.021602` | -0.002004 | `-0.027988` to `0.024793` | 0.063575 | 0.001 | 0.010525 |
| tsplib_failure_replay vs tsplib_random_replay | 20 | 0.026674 | `-0.005591` to `0.056743` | 0.02911 | `-0.010083` to `0.064428` | 0.069622 | -0.069 | -0.025174 |
| tsplib_failure_replay_compression vs tsplib_failure_replay | 20 | -0.006023 | `-0.030618` to `0.018585` | -0.003742 | `-0.035531` to `0.027774` | -0.519458 | 0.039 | 0.015433 |
| tsplib_failure_replay_compression vs tsplib_no_replay | 20 | -0.00758 | `-0.031668` to `0.016734` | -0.005747 | `-0.035992` to `0.024612` | -0.455883 | 0.04 | 0.025957 |

### Paired Notes
- `tsplib_random_replay` vs `tsplib_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.028231` with 95% CI `-0.052034` to `-0.002934`; candidate better on 55.0% of paired runs.
- Mean TSPLIB-gap delta: `-0.031114` with 95% CI `-0.060232` to `-0.000821`.
- `tsplib_failure_replay` vs `tsplib_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.001556` with 95% CI `-0.023279` to `0.021602`; candidate better on 35.0% of paired runs.
- Mean TSPLIB-gap delta: `-0.002004` with 95% CI `-0.027988` to `0.024793`.
- `tsplib_failure_replay` vs `tsplib_random_replay` used 20 paired runs.
- Mean transfer-gap delta: `0.026674` with 95% CI `-0.005591` to `0.056743`; candidate better on 20.0% of paired runs.
- Mean TSPLIB-gap delta: `0.02911` with 95% CI `-0.010083` to `0.064428`.
- `tsplib_failure_replay_compression` vs `tsplib_failure_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.006023` with 95% CI `-0.030618` to `0.018585`; candidate better on 35.0% of paired runs.
- Mean TSPLIB-gap delta: `-0.003742` with 95% CI `-0.035531` to `0.027774`.
- `tsplib_failure_replay_compression` vs `tsplib_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.00758` with 95% CI `-0.031668` to `0.016734`; candidate better on 30.0% of paired runs.
- Mean TSPLIB-gap delta: `-0.005747` with 95% CI `-0.035992` to `0.024612`.
