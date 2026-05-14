# Replay-Aware ATSP Aggregate Report

## Overview
- Run count: 20.
- Condition count: 4.
- Best mean transfer gap: `atsp_failure_replay_compression`.

## Condition Comparison
| Condition | Mean Transfer Gap | Mean TSPLIB ATSP Gap | Mean Synthetic Gap | Mean Accepted Novelty | Mean Complexity | Mean Adaptation Efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atsp_failure_replay | 0.103224 | 0.188856 | 0.017592 | 0.567311 | 0.660375 | 0.014901 |
| atsp_failure_replay_compression | 0.102242 | 0.187225 | 0.017259 | 0.617612 | 0.66 | 0.017559 |
| atsp_no_replay | 0.108551 | 0.192847 | 0.024256 | 0.36888 | 0.699875 | 0.011466 |
| atsp_random_replay | 0.103757 | 0.192742 | 0.014773 | 0.565185 | 0.64 | 0.014107 |

## Bootstrap Confidence Intervals
### atsp_failure_replay
- Transfer gap 95% CI: `0.098679` to `0.10785`.
- TSPLIB ATSP gap 95% CI: `0.180163` to `0.195733`.
- Synthetic gap 95% CI: `0.012457` to `0.02328`.
- Mean accepted novelty 95% CI: `0.399203` to `0.724716`.
### atsp_failure_replay_compression
- Transfer gap 95% CI: `0.097779` to `0.107925`.
- TSPLIB ATSP gap 95% CI: `0.177656` to `0.197249`.
- Synthetic gap 95% CI: `0.012663` to `0.022272`.
- Mean accepted novelty 95% CI: `0.449587` to `0.764254`.
### atsp_no_replay
- Transfer gap 95% CI: `0.102438` to `0.115582`.
- TSPLIB ATSP gap 95% CI: `0.182104` to `0.204743`.
- Synthetic gap 95% CI: `0.018273` to `0.030237`.
- Mean accepted novelty 95% CI: `0.199128` to `0.54588`.
### atsp_random_replay
- Transfer gap 95% CI: `0.099275` to `0.109755`.
- TSPLIB ATSP gap 95% CI: `0.186304` to `0.201261`.
- Synthetic gap 95% CI: `0.010363` to `0.02`.
- Mean accepted novelty 95% CI: `0.393863` to `0.723033`.

## Paired Comparisons
Negative delta favors the candidate for transfer gap, benchmark gap, synthetic gap, novelty, and complexity. Positive delta favors the candidate for adaptation efficiency.

| Comparison | Paired Runs | Transfer Delta | Transfer 95% CI | ATSP Delta | ATSP 95% CI | Novelty Delta | Complexity Delta | Adaptation Delta |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: |
| atsp_random_replay vs atsp_no_replay | 20 | -0.004794 | `-0.014338` to `0.004763` | -0.000105 | `-0.014844` to `0.014854` | 0.196305 | -0.059875 | 0.002641 |
| atsp_failure_replay vs atsp_no_replay | 20 | -0.005327 | `-0.012952` to `0.001875` | -0.003991 | `-0.016859` to `0.008555` | 0.198431 | -0.0395 | 0.003435 |
| atsp_failure_replay vs atsp_random_replay | 20 | -0.000533 | `-0.008292` to `0.006606` | -0.003886 | `-0.01533` to `0.0059` | 0.002126 | 0.020375 | 0.000794 |
| atsp_failure_replay_compression vs atsp_failure_replay | 20 | -0.000982 | `-0.007357` to `0.00623` | -0.001631 | `-0.014403` to `0.011915` | 0.050301 | -0.000375 | 0.002658 |
| atsp_failure_replay_compression vs atsp_no_replay | 20 | -0.006309 | `-0.0133` to `-0.000173` | -0.005622 | `-0.019126` to `0.007143` | 0.248732 | -0.039875 | 0.006093 |

### Paired Notes
- `atsp_random_replay` vs `atsp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.004794` with 95% CI `-0.014338` to `0.004763`; candidate better on 65.0% of paired runs.
- Mean TSPLIB ATSP-gap delta: `-0.000105` with 95% CI `-0.014844` to `0.014854`.
- `atsp_failure_replay` vs `atsp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.005327` with 95% CI `-0.012952` to `0.001875`; candidate better on 70.0% of paired runs.
- Mean TSPLIB ATSP-gap delta: `-0.003991` with 95% CI `-0.016859` to `0.008555`.
- `atsp_failure_replay` vs `atsp_random_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.000533` with 95% CI `-0.008292` to `0.006606`; candidate better on 50.0% of paired runs.
- Mean TSPLIB ATSP-gap delta: `-0.003886` with 95% CI `-0.01533` to `0.0059`.
- `atsp_failure_replay_compression` vs `atsp_failure_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.000982` with 95% CI `-0.007357` to `0.00623`; candidate better on 50.0% of paired runs.
- Mean TSPLIB ATSP-gap delta: `-0.001631` with 95% CI `-0.014403` to `0.011915`.
- `atsp_failure_replay_compression` vs `atsp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.006309` with 95% CI `-0.0133` to `-0.000173`; candidate better on 45.0% of paired runs.
- Mean TSPLIB ATSP-gap delta: `-0.005622` with 95% CI `-0.019126` to `0.007143`.
