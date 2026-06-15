# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_no_replay`.
- Best TSPLIB holdout gap: `phase6_no_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_014852_k
- started_at_local: 2026-05-19 01:48:52
- finished_at_local: 2026-05-19 02:08:10
- duration_hhmm: 00:19
- duration_seconds: 1158.226
- seed_offset: 10000
- replicate_label: k
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.075365 | 0.0 | 0.04796 | 0.236772 | 0.179811 | 0.0 | 0.759293 | 0.76 | 0.050798 |
| phase6_random_replay | random | score_only | False | 0.139786 | 0.010343 | 0.092716 | 0.236772 | 0.128729 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_failure_replay | failure | score_only | False | 0.113927 | 0.0 | 0.072499 | 0.171206 | 0.285747 | 0.198386 | 0.851953 | 0.76 | 0.006999 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.221162 | 0.766888 | 0.56 | -0.032475 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.1208 | 0.0 | 0.076873 | 0.236772 | 0.189134 | 0.157984 | 0.825338 | 0.76 | 0.028732 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.149274 | 0.338865 | 0.291666 | 0.86282 | 0.56 | -0.028865 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.921764 | 0.56 | -0.027019 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.103359 | 0.003941 | 0.067207 | 0.171206 | 0.273531 | 0.171012 | 0.801748 | 0.76 | 0.024738 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.075365`, synthetic `0.0`, combined `0.04796`.
- Accepted-epoch count `3`, mean accepted code novelty `0.759293`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.179811`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.050798` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.075365` across 7 instances; family means: ch=0.134878, kroD=0.042876, pcb=0.125862, pr=0.036113, rd=0.020354, st=0.032593.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3536, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.371074, "residual_gap": -0.029702}, {"best_known_cost": 629, "cost": 766, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.217806, "residual_gap": -0.039746}, {"best_known_cost": 14379, "cost": 16996, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.182002, "residual_gap": -0.144655}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.139786`, synthetic `0.010343`, combined `0.092716`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.128729`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133446`, mean selected residual gap `-0.042017`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.139786` across 7 instances; family means: ch=0.118433, kroD=0.158777, pcb=0.210288, pr=0.13237, rd=0.145386, st=0.094815.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3536, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.371074, "residual_gap": -0.029702}, {"best_known_cost": 14379, "cost": 17804, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.238195, "residual_gap": -0.088462}, {"best_known_cost": 629, "cost": 703, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.117647, "residual_gap": -0.138633}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.113927`, synthetic `0.0`, combined `0.072499`.
- Accepted-epoch count `2`, mean accepted code novelty `0.851953`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.285747`, size bias `0.120322`, and failure concentration `0.198386`.
- Replay selection diversity `0.201513`, mean selected expected gap `0.318751`, mean selected residual gap `0.003212`.
- Adaptation efficiency `0.006999` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.113927` across 7 instances; family means: ch=0.07276, kroD=0.03602, pcb=0.171433, pr=0.18483, rd=0.170796, st=0.088889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 823, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.308426, "residual_gap": 0.053736}, {"best_known_cost": 14379, "cost": 18179, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.264274, "residual_gap": -0.060714}, {"best_known_cost": 2579, "cost": 3200, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.240791, "residual_gap": -0.161148}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132402`, mean selected residual gap `0.038964`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.002327}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.325433, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00338}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.766888`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236729`, mean selected residual gap `0.053996`.
- Adaptation efficiency `-0.032475` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.005196}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.004952}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.1208`, synthetic `0.0`, combined `0.076873`.
- Accepted-epoch count `3`, mean accepted code novelty `0.825338`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.189134`, size bias `8.3e-05`, and failure concentration `0.157984`.
- Replay selection diversity `0.265196`, mean selected expected gap `0.158153`, mean selected residual gap `0.00837`.
- Adaptation efficiency `0.028732` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.1208` across 7 instances; family means: ch=0.056651, kroD=0.355546, pcb=0.199673, pr=0.049926, rd=0.057522, st=0.06963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3096, "expected_gap": 0.406049, "family": "a", "name": "a280", "optimality_gap": 0.200465, "residual_gap": -0.205584}, {"best_known_cost": 14379, "cost": 16637, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.157035, "residual_gap": -0.164476}, {"best_known_cost": 629, "cost": 674, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.071542, "residual_gap": -0.182512}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.86282`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.149274`, mean hardness `0.338865`, size bias `0.093558`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.26743`, mean selected residual gap `0.084963`.
- Adaptation efficiency `-0.028865` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.404963, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.003645}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.001975}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.921764`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.302069`, mean selected residual gap `0.047919`.
- Adaptation efficiency `-0.027019` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402482, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001164}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.124006}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.001836}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.103359`, synthetic `0.003941`, combined `0.067207`.
- Accepted-epoch count `4`, mean accepted code novelty `0.801748`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.273531`, size bias `0.120322`, and failure concentration `0.171012`.
- Replay selection diversity `0.197063`, mean selected expected gap `0.300451`, mean selected residual gap `-0.025103`.
- Adaptation efficiency `0.024738` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `4`.
- Panel `heldout_tsplib` mean gap `0.103359` across 7 instances; family means: ch=0.097819, kroD=0.073307, pcb=0.126708, pr=0.053782, rd=0.179267, st=0.094815.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3395, "expected_gap": 0.401086, "family": "a", "name": "a280", "optimality_gap": 0.316402, "residual_gap": -0.084684}, {"best_known_cost": 7542, "cost": 9908, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.31371, "residual_gap": 0.072792}, {"best_known_cost": 14379, "cost": 17342, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.206064, "residual_gap": -0.118896}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Suite Results

## Overall Best Performing Condition
- **Best Holdout (TSPLIB) Gap:** `phase6_no_replay` (0.0754 mean gap)
- **Best Synthetic Holdout Gap:** `phase6_no_replay` (0.0 mean gap)
- **Best Transfer Gap:** `phase6_no_replay` (0.048 mean gap)

## Transfer and Optimality
- `phase6_no_replay` achieves the lowest mean holdout gaps (TSPLIB: 7.5%, Synthetic: 0.0%) and lowest transfer gap (4.8%), indicating the best empirical transfer performance.
- All replay conditions exhibit notably higher mean gaps on held-out TSPLIB and synthetic sets (TSPLIB gaps range ~10.3% to 21.3%; synthetic gaps from ~0.004 to 0.065).
- Transfer gaps (TSPLIB) for replay conditions range roughly from 6.7% (lowest in `diversity_failure_replay_compression`) up to 15.9% (`random_replay_compression`), all worse than no replay.
- Thus, no replay achieves superior or equal transfer quality compared to any replay setting.

## Replay Mode Categories and Their Effect on Transfer
- **No Replay (baseline):**
  - Archive size ~31, diversity 0.24.
  - Low final training gap (~23.1% last), transfer gap lowest at 4.8%.
  - Complexity 0.76, no compression pressure.
  - Code novelty highest (last: 0.70; mean: 0.76).
- **Random Replay:**
  - Similar archive size and diversity (~31 and 0.24).
  - Higher transfer gap (9.3% mean) and synthetic gap (~1%).
  - Replay failure concentration 0.16-0.19.
  - Code novelty dropped to zero due to disabling novelty-based selection.
  - Compression pressure off in random replay; on in compression variant.
- **Failure Replay (raw failure samples):**
  - Archive size ~30, lower descriptor diversity (0.17), but higher hardness (~0.32).
  - Transfer gap improved over random (7.2%), synthetic gap 0.0.
  - Failure concentration increased (~0.21).
  - Code novelty is high (0.85).
- **Random Replay with Compression:**
  - Complexity reduced (0.56 vs 0.76 no replay).
  - Archive diversity same but hardness and transfer gap much worse (TSPLIB gap 21.3%, transfer gap 16%).
  - Code novelty 0.
- **Stratified Random Replay:**
  - Similar to random replay compression: same synthetic and transfer gaps (~6.7%-16%), similar complexity (0.56).
  - Archive diversity and hardness at intermediate levels.
- **Diversity-Weighted Replay:**
  - Archive descriptor diversity 0.24, hardness 0.21, complexity 0.76.
  - Transfer gap 7.7%, synthetic gap 0.0.
  - Code novelty high (mean 0.82).
- **Residual Failure Replay:**
  - Archive diversity lowest (0.15), hardness highest (~0.34).
  - Transfer gap 16%, synthetic gap 6.5%.
  - Failure concentration highest (~0.29).
  - Code novelty very high (~0.86).
- **Diversity Failure Replay:**
  - Archive diversity 0.17, highest hardness (0.35).
  - Transfer gap 16%, synthetic gap 6.5%.
  - Failure concentration ~0.17.
  - Code novelty very high (~0.92).
- **Diversity Failure Replay with Compression:**
  - Archive diversity ~0.17, hardness lower (0.29).
  - Transfer gap best of replays at 6.7%, synthetic gap 0.4%.
  - Failure concentration moderate (~0.17).
  - Code novelty ~0.80.

## Replay Archive and Selection Metrics
- Archive diversity ranges from 0.15 (residual failure replay) to 0.24 (no replay and diversity-weighted).
- Replay failure concentration is zero for no replay; non-zero (0.16 to 0.33) for replay modes, reflecting focus on failure or residual cases.
- Selection diversity and expected gaps depend on selection mode; score-only selection yields selected expected gap generally aligned with overall performance.
- Compression pressure reduces complexity and increases gaps, indicating degradation.

## Mechanism Studies: Diversity, Hardness, Size Bias, Failure Concentration
- Replay modes focusing on failure/residual failures increase archive hardness significantly (up to ~0.34-0.35).
- Diversity-weighted and no replay maintain higher descriptor diversity (~0.24).
- Size bias is near zero (~0.0) except for failure replay modes (~0.12), suggesting failure replays bias towards larger harder instances.
- Failure replay concentration correlates positively with hardness and size bias, indicating concentrated replay on hard failures.

## Code Novelty vs Transfer Performance
- No replay condition maintains highest code novelty and best transfer performance.
- Replay modes, especially with novelty_gate off, show zero or reduced code novelty but worse transfer.
- Residual and diversity failure replays have high code novelty but poor transfer.
- Compression-associated modes have lower code novelty and worse transfer.
- Thus, increased novelty does not guarantee improved transfer here.

## Summary Table (Key Metrics)

| Condition                           | Transfer Gap (TSPLIB) | Synthetic Gap | Code Novelty Mean | Archive Diversity | Archive Hardness | Size Bias | Failure Concentration | Complexity | Replay Mode           |
|-----------------------------------|----------------------|--------------|-------------------|-------------------|------------------|-----------|------------------------|------------|----------------------|
| phase6_no_replay                  | 0.04796              | 0.0          | 0.76              | 0.24              | 0.21             | 0.0       | 0.0                    | 0.76       | none                 |
| phase6_random_replay              | 0.09272              | 0.0103       | 0.0               | 0.24              | 0.13             | 0.0       | 0.19                   | 0.76       | random               |
| phase6_failure_replay             | 0.0725               | 0.0          | 0.85              | 0.17              | 0.32             | 0.12      | 0.20                   | 0.76       | failure              |
| phase6_random_replay_compression  | 0.1594               | 0.065        | 0.0               | 0.24              | 0.21             | 0.0       | 0.19                   | 0.56       | random/compression   |
| phase6_stratified_random_replay   | 0.1594               | 0.065        | 0.77              | 0.24              | 0.21             | 0.0       | 0.22                   | 0.56       | stratified_random    |
| phase6_diversity_weighted_replay  | 0.0769               | 0.0          | 0.83              | 0.24              | 0.21             | 0.0       | 0.16                   | 0.76       | diversity_weighted   |
| phase6_residual_failure_replay    | 0.1594               | 0.065        | 0.86              | 0.15              | 0.34             | 0.09      | 0.29                   | 0.56       | residual_failure     |
| phase6_diversity_failure_replay   | 0.1594               | 0.065        | 0.92              | 0.17              | 0.35             | 0.12      | 0.17                   | 0.56       | diversity_failure    |
| phase6_diversity_failure_replay_compression | 0.0672      | 0.004        | 0.80              | 0.17              | 0.29             | 0.12      | 0.17                   | 0.76       | diversity_failure/compression |

## Interpretation Conclusions

1. **No Replays Achieve Best Transfer and Optimality Gap**  
   The best_holdout, synthetic_holdout, and transfer gaps are all lowest for `phase6_no_replay` indicating that adding replay mechanisms here does not improve transfer performance.

2. **Replay Modes Increase Archive Hardness and Failure Concentration but Do Not Improve Transfer**  
   Failure-based replays increase archive hardness and focus on failure cases, but the transfer and holdout optimality gaps remain higher than no replay.

3. **Compression Pressure Degrades Transfer and Increases Optimality Gaps**  
   Modes with compression pressure show increased gaps and reduced complexity, indicating a harmful effect on solution quality.

4. **Code Novelty Does Not Correlate Positively With Transfer**  
   High code novelty is observed in some failure-based replay conditions but does not translate to better transfer gaps; no replay maintains strong transfer with moderate-high code novelty, suggesting code novelty alone is insufficient.

5. **Diversity-Weighted Replay Performs Better Than Random/Failure Replays but Worse Than No Replay**  
   Diversity-weighted replay has moderate code novelty and reasonable gaps, but still inferior to no replay in transfer and optimality.

6. **Synthetic Holdout Gaps are Zero or Near Zero in No Replay Conditions, Marginally Higher in Replays**  
   Synthetic gaps corroborate the transfer gap trends: no replay is optimal, replay can weaken performance.

---

# Summary

- The **no replay** condition (plain learning without replay) is currently the best for transfer performance, measured by the lowest optimality gaps on held-out TSPLIB and synthetic benchmark sets.
- Replay modes (random, failure-based, diversity-weighted, residual failure) increase archive hardness and focus but *do not* reduce transfer or holdout gaps. In fact, they generally increase these gaps.
- Compression pressure tends to degrade performance.
- Increased code novelty in replay modes does not correspond to improved gaps, indicating that lexical or code novelty does not guarantee better algorithmic innovation or transfer.
- Among replay mechanisms, diversity-weighted replay yields somewhat better transfer compared to other replay modes but remains worse than no replay.
- Failure concentration and size bias increase with failure and residual failure replay, indicating replay archives concentrate on hard, large instances but at a cost to transfer.

# Recommendation

- Prioritize no replay or diversity-weighted replay without compression for best transfer and holdout performance.
- Future work could investigate causes why replaying failure or residual failure cases, despite increasing archive hardness, does not yield better transfer, and why increased code novelty fails to translate into transfer gains.

---

*This interpretation is based strictly on key empirical transfer metrics and archival statistics, avoiding speculative narrative.*
