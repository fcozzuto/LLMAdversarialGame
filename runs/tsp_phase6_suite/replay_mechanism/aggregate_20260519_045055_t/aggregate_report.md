# Phase 6 TSP Replay Mechanism Report

## Overview
- Run count: 20.
- Condition count: 9.
- Best mean transfer gap: `phase6_diversity_failure_replay`.

## Mechanism Answers
1. Why did random replay beat failure replay? Random replay beat raw failure replay only narrowly, but the paired comparison points in the same direction as the coverage hypothesis. Relative to no replay, random replay changed transfer by -0.003123. Relative to random replay, failure replay changed transfer by 0.001361, archive diversity by -0.065566, and archive hardness by 0.128613.
2. Does replay archive diversity explain transfer better than replay hardness? Archive hardness explains transfer at least as strongly as diversity.
3. Does compression help once applied to the best replay mechanism? Random-replay compression changed transfer by 0.014874 and complexity by -0.03 relative to plain random replay.
4. Are the final heuristics genuinely different, or just differently tuned? Final heuristics should be treated as genuinely different only when transfer, novelty, and complexity move together; the paired novelty and complexity deltas in this aggregate are the main evidence for that distinction.

## Condition Comparison
| Condition | Mean Transfer Gap | Mean TSPLIB Gap | Mean Synthetic Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_diversity_failure_replay | 0.089519 | 0.132031 | 0.015122 | 0.171206 | 0.279086 | 0.172965 | 0.652934 | 0.72 | 0.023136 |
| phase6_diversity_failure_replay_compression | 0.111045 | 0.161437 | 0.022859 | 0.171206 | 0.288591 | 0.172553 | 0.284606 | 0.7 | 0.017447 |
| phase6_diversity_weighted_replay | 0.1035 | 0.152842 | 0.017152 | 0.236772 | 0.180063 | 0.143749 | 0.643928 | 0.72 | 0.022408 |
| phase6_failure_replay | 0.098156 | 0.142676 | 0.020247 | 0.171206 | 0.296396 | 0.234171 | 0.639973 | 0.7 | 0.016269 |
| phase6_no_replay | 0.099918 | 0.14391 | 0.022932 | 0.236772 | 0.179815 | 0.0 | 0.74868 | 0.7035 | 0.015112 |
| phase6_random_replay | 0.096795 | 0.143616 | 0.014856 | 0.236772 | 0.167783 | 0.19457 | 0.676544 | 0.72 | 0.029828 |
| phase6_random_replay_compression | 0.111669 | 0.161783 | 0.023969 | 0.236772 | 0.181505 | 0.19457 | 0.395132 | 0.69 | 0.015059 |
| phase6_residual_failure_replay | 0.120734 | 0.172899 | 0.029446 | 0.118795 | 0.278985 | 0.299628 | 0.548243 | 0.68 | -0.002814 |
| phase6_stratified_random_replay | 0.095646 | 0.141696 | 0.015057 | 0.236772 | 0.174478 | 0.221162 | 0.62979 | 0.72 | 0.020423 |

## Archive-Diversity Diagnostics
- Diversity vs TSPLIB gap Pearson r: `-0.009478`.
- Diversity vs TSPLIB gap Spearman rho: `-0.041013`.
- Hardness vs TSPLIB gap Pearson r: `0.39687`.
- Hardness vs TSPLIB gap Spearman rho: `0.371779`.

## Paired Comparisons
Negative deltas favor the candidate for transfer gap, benchmark gap, synthetic gap, hardness, concentration, novelty, and complexity. Positive deltas favor the candidate for archive diversity and adaptation efficiency.

| Comparison | Paired Runs | Transfer Delta | TSPLIB Delta | Archive Diversity Delta | Archive Hardness Delta | Novelty Delta | Complexity Delta | Adaptation Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_random_replay vs phase6_no_replay | 20 | -0.003123 | -0.000293 | 0.0 | -0.012032 | -0.072135 | 0.0165 | 0.014716 |
| phase6_failure_replay vs phase6_random_replay | 20 | 0.001361 | -0.000941 | -0.065566 | 0.128613 | -0.036571 | -0.02 | -0.013558 |
| phase6_random_replay_compression vs phase6_random_replay | 20 | 0.014874 | 0.018166 | 0.0 | 0.013722 | -0.281412 | -0.03 | -0.014769 |
| phase6_stratified_random_replay vs phase6_random_replay | 20 | -0.001149 | -0.001921 | 0.0 | 0.006695 | -0.046754 | 0.0 | -0.009405 |
| phase6_diversity_weighted_replay vs phase6_random_replay | 20 | 0.006706 | 0.009226 | 0.0 | 0.01228 | -0.032616 | 0.0 | -0.007419 |
| phase6_residual_failure_replay vs phase6_failure_replay | 20 | 0.022578 | 0.030223 | -0.052411 | -0.017411 | -0.09173 | -0.02 | -0.019083 |
| phase6_diversity_failure_replay vs phase6_failure_replay | 20 | -0.008637 | -0.010644 | 0.0 | -0.01731 | 0.012961 | 0.02 | 0.006866 |
| phase6_diversity_failure_replay_compression vs phase6_diversity_failure_replay | 20 | 0.021526 | 0.029405 | 0.0 | 0.009505 | -0.368327 | -0.02 | -0.005689 |

### Paired Notes
- `phase6_random_replay` vs `phase6_no_replay` used 20 paired runs.
- Transfer delta `-0.003123` with 95% CI `-0.027964` to `0.021061`.
- TSPLIB delta `-0.000293` with 95% CI `-0.032786` to `0.031526`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
- `phase6_failure_replay` vs `phase6_random_replay` used 20 paired runs.
- Transfer delta `0.001361` with 95% CI `-0.022536` to `0.025457`.
- TSPLIB delta `-0.000941` with 95% CI `-0.028763` to `0.027462`.
- Archive-diversity delta `-0.065566` with 95% CI `-0.065566` to `-0.065566`.
- `phase6_random_replay_compression` vs `phase6_random_replay` used 20 paired runs.
- Transfer delta `0.014874` with 95% CI `-0.006282` to `0.035586`.
- TSPLIB delta `0.018166` with 95% CI `-0.008968` to `0.044141`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
- `phase6_stratified_random_replay` vs `phase6_random_replay` used 20 paired runs.
- Transfer delta `-0.001149` with 95% CI `-0.023074` to `0.02094`.
- TSPLIB delta `-0.001921` with 95% CI `-0.029404` to `0.02615`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
- `phase6_diversity_weighted_replay` vs `phase6_random_replay` used 20 paired runs.
- Transfer delta `0.006706` with 95% CI `-0.020065` to `0.033445`.
- TSPLIB delta `0.009226` with 95% CI `-0.023988` to `0.041405`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
- `phase6_residual_failure_replay` vs `phase6_failure_replay` used 20 paired runs.
- Transfer delta `0.022578` with 95% CI `-0.005643` to `0.04867`.
- TSPLIB delta `0.030223` with 95% CI `-0.004028` to `0.062114`.
- Archive-diversity delta `-0.052411` with 95% CI `-0.073656` to `-0.033974`.
- `phase6_diversity_failure_replay` vs `phase6_failure_replay` used 20 paired runs.
- Transfer delta `-0.008637` with 95% CI `-0.035972` to `0.017862`.
- TSPLIB delta `-0.010644` with 95% CI `-0.044114` to `0.021829`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
- `phase6_diversity_failure_replay_compression` vs `phase6_diversity_failure_replay` used 20 paired runs.
- Transfer delta `0.021526` with 95% CI `-0.004764` to `0.047151`.
- TSPLIB delta `0.029405` with 95% CI `-0.003787` to `0.06157`.
- Archive-diversity delta `0.0` with 95% CI `0.0` to `0.0`.
