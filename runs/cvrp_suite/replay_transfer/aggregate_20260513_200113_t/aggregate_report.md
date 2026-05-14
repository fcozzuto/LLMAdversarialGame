# Replay-Aware CVRP Aggregate Report

## Overview
- Run count: 20.
- Condition count: 4.
- Best mean transfer gap: `cvrp_no_replay`.

## Condition Comparison
| Condition | Mean Transfer Gap | Mean CVRPLIB Gap | Mean Synthetic Gap | Mean Accepted Novelty | Mean Complexity | Mean Adaptation Efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cvrp_failure_replay | 0.137238 | 0.238397 | 0.010788 | 0.596004 | 0.67 | 0.020111 |
| cvrp_failure_replay_compression | 0.140394 | 0.243836 | 0.011093 | 0.511511 | 0.63 | 0.018193 |
| cvrp_no_replay | 0.136873 | 0.235779 | 0.01324 | 0.711362 | 0.7 | 0.013129 |
| cvrp_random_replay | 0.139859 | 0.246032 | 0.007144 | 0.766976 | 0.63 | 0.013062 |

## Bootstrap Confidence Intervals
### cvrp_failure_replay
- Transfer gap 95% CI: `0.133831` to `0.14071`.
- CVRPLIB gap 95% CI: `0.233061` to `0.243465`.
- Synthetic gap 95% CI: `0.005491` to `0.017588`.
- Mean accepted novelty 95% CI: `0.418211` to `0.764053`.
### cvrp_failure_replay_compression
- Transfer gap 95% CI: `0.135442` to `0.145871`.
- CVRPLIB gap 95% CI: `0.236307` to `0.250893`.
- Synthetic gap 95% CI: `0.005107` to `0.018784`.
- Mean accepted novelty 95% CI: `0.328095` to `0.68867`.
### cvrp_no_replay
- Transfer gap 95% CI: `0.133036` to `0.140191`.
- CVRPLIB gap 95% CI: `0.229341` to `0.241658`.
- Synthetic gap 95% CI: `0.007953` to `0.019903`.
- Mean accepted novelty 95% CI: `0.570133` to `0.831854`.
### cvrp_random_replay
- Transfer gap 95% CI: `0.13685` to `0.143267`.
- CVRPLIB gap 95% CI: `0.240936` to `0.251195`.
- Synthetic gap 95% CI: `0.005376` to `0.009667`.
- Mean accepted novelty 95% CI: `0.63726` to `0.863645`.

## Paired Comparisons
Negative delta favors the candidate for transfer gap, benchmark gap, synthetic gap, novelty, and complexity. Positive delta favors the candidate for adaptation efficiency.

| Comparison | Paired Runs | Transfer Delta | Transfer 95% CI | CVRPLIB Delta | CVRPLIB 95% CI | Novelty Delta | Complexity Delta | Adaptation Delta |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: |
| cvrp_random_replay vs cvrp_no_replay | 20 | 0.002987 | `-0.001817` to `0.008152` | 0.010253 | `0.002587` to `0.018356` | 0.055614 | -0.07 | -6.7e-05 |
| cvrp_failure_replay vs cvrp_no_replay | 20 | 0.000365 | `-0.004065` to `0.005159` | 0.002618 | `-0.002573` to `0.007785` | -0.115358 | -0.03 | 0.006981 |
| cvrp_failure_replay vs cvrp_random_replay | 20 | -0.002622 | `-0.006831` to `0.001333` | -0.007634 | `-0.014563` to `-0.000625` | -0.170972 | 0.04 | 0.007048 |
| cvrp_failure_replay_compression vs cvrp_failure_replay | 20 | 0.003157 | `-0.001624` to `0.007804` | 0.005438 | `-0.002502` to `0.012963` | -0.084493 | -0.04 | -0.001918 |
| cvrp_failure_replay_compression vs cvrp_no_replay | 20 | 0.003522 | `-0.002561` to `0.010426` | 0.008056 | `-0.000843` to `0.01684` | -0.199851 | -0.07 | 0.005064 |

### Paired Notes
- `cvrp_random_replay` vs `cvrp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `0.002987` with 95% CI `-0.001817` to `0.008152`; candidate better on 50.0% of paired runs.
- Mean CVRPLIB-gap delta: `0.010253` with 95% CI `0.002587` to `0.018356`.
- `cvrp_failure_replay` vs `cvrp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `0.000365` with 95% CI `-0.004065` to `0.005159`; candidate better on 50.0% of paired runs.
- Mean CVRPLIB-gap delta: `0.002618` with 95% CI `-0.002573` to `0.007785`.
- `cvrp_failure_replay` vs `cvrp_random_replay` used 20 paired runs.
- Mean transfer-gap delta: `-0.002622` with 95% CI `-0.006831` to `0.001333`; candidate better on 65.0% of paired runs.
- Mean CVRPLIB-gap delta: `-0.007634` with 95% CI `-0.014563` to `-0.000625`.
- `cvrp_failure_replay_compression` vs `cvrp_failure_replay` used 20 paired runs.
- Mean transfer-gap delta: `0.003157` with 95% CI `-0.001624` to `0.007804`; candidate better on 35.0% of paired runs.
- Mean CVRPLIB-gap delta: `0.005438` with 95% CI `-0.002502` to `0.012963`.
- `cvrp_failure_replay_compression` vs `cvrp_no_replay` used 20 paired runs.
- Mean transfer-gap delta: `0.003522` with 95% CI `-0.002561` to `0.010426`; candidate better on 45.0% of paired runs.
- Mean CVRPLIB-gap delta: `0.008056` with 95% CI `-0.000843` to `0.01684`.
