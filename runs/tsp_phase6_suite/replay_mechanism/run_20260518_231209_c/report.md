# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_weighted_replay`.
- Best synthetic holdout gap: `phase6_failure_replay`.

## Run Metadata
- run_name: run_20260518_231209_c
- started_at_local: 2026-05-18 23:12:09
- finished_at_local: 2026-05-18 23:32:53
- duration_hhmm: 00:21
- duration_seconds: 1243.645
- seed_offset: 2000
- replicate_label: c
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.086291 | 0.010343 | 0.058674 | 0.236772 | 0.162469 | 0.0 | 0.764505 | 0.76 | 0.036986 |
| phase6_random_replay | random | score_only | False | 0.210832 | 0.012044 | 0.138545 | 0.236772 | 0.153461 | 0.19457 | 0.0 | 0.76 | 0.0 |
| phase6_failure_replay | failure | score_only | False | 0.143482 | 0.0 | 0.091307 | 0.171206 | 0.27492 | 0.222081 | 0.0 | 0.76 | 0.0 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.114249 | 0.0 | 0.072704 | 0.236772 | 0.16683 | 0.19457 | 0.805692 | 0.76 | 0.013487 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.141226 | 0.0 | 0.089871 | 0.236772 | 0.186949 | 0.221162 | 0.853725 | 0.76 | 0.044302 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.084761 | 0.003941 | 0.055372 | 0.236772 | 0.16044 | 0.157119 | 0.817261 | 0.76 | 0.04933 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.197162 | 0.0 | 0.125467 | 0.158073 | 0.331945 | 0.367262 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.086663 | 0.0 | 0.055149 | 0.171206 | 0.230022 | 0.174426 | 0.814708 | 0.76 | 0.059496 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.134684 | 0.003941 | 0.087141 | 0.171206 | 0.3043 | 0.17767 | 0.645429 | 0.76 | 0.049276 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.086291`, synthetic `0.010343`, combined `0.058674`.
- Accepted-epoch count `3`, mean accepted code novelty `0.764505`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.162469`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.036986` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.086291` across 7 instances; family means: ch=0.068918, kroD=0.037287, pcb=0.155796, pr=0.111484, rd=0.069785, st=0.091852.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3178, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.232261, "residual_gap": -0.171229}, {"best_known_cost": 7542, "cost": 8291, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.099311, "residual_gap": -0.141607}, {"best_known_cost": 14379, "cost": 15300, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.064052, "residual_gap": -0.260908}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.210832`, synthetic `0.012044`, combined `0.138545`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.153461`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133388`, mean selected residual gap `-0.016771`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.210832` across 7 instances; family means: ch=0.195686, kroD=0.215835, pcb=0.267833, pr=0.315646, rd=0.176991, st=0.108148.
- Panel `synthetic_holdout` mean gap `0.012044` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.048176, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3347, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.29779, "residual_gap": -0.1057}, {"best_known_cost": 14379, "cost": 18560, "expected_gap": 0.321761, "family": "lin", "name": "lin105", "optimality_gap": 0.290771, "residual_gap": -0.03099}, {"best_known_cost": 7542, "cost": 8325, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.103819, "residual_gap": -0.132803}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.143482`, synthetic `0.0`, combined `0.091307`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.27492`, size bias `0.120322`, and failure concentration `0.222081`.
- Replay selection diversity `0.176857`, mean selected expected gap `0.314562`, mean selected residual gap `-0.010364`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.143482` across 7 instances; family means: ch=0.091634, kroD=0.177374, pcb=0.206901, pr=0.236171, rd=0.175474, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3358, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.302055, "residual_gap": -0.10159}, {"best_known_cost": 7542, "cost": 9372, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.242641, "residual_gap": 0.009493}, {"best_known_cost": 629, "cost": 756, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.201908, "residual_gap": -0.052782}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.114249`, synthetic `0.0`, combined `0.072704`.
- Accepted-epoch count `3`, mean accepted code novelty `0.805692`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.16683`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132188`, mean selected residual gap `0.004372`.
- Adaptation efficiency `0.013487` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.114249` across 7 instances; family means: ch=0.061092, kroD=0.237767, pcb=0.221041, pr=0.113721, rd=0.082807, st=0.022222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19562, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.360456, "residual_gap": 0.037262}, {"best_known_cost": 629, "cost": 788, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.252782, "residual_gap": -0.000636}, {"best_known_cost": 7542, "cost": 8785, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.16481, "residual_gap": -0.072554}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.141226`, synthetic `0.0`, combined `0.089871`.
- Accepted-epoch count `2`, mean accepted code novelty `0.853725`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.186949`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236357`, mean selected residual gap `0.014864`.
- Adaptation efficiency `0.044302` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.141226` across 7 instances; family means: ch=0.181646, kroD=0.139852, pcb=0.174052, pr=0.044388, rd=0.124779, st=0.142222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3629, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.407135, "residual_gap": 0.005196}, {"best_known_cost": 7542, "cost": 9857, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.306948, "residual_gap": 0.069584}, {"best_known_cost": 629, "cost": 752, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.195548, "residual_gap": -0.060732}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.084761`, synthetic `0.003941`, combined `0.055372`.
- Accepted-epoch count `3`, mean accepted code novelty `0.817261`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.16044`, size bias `8.3e-05`, and failure concentration `0.157119`.
- Replay selection diversity `0.271932`, mean selected expected gap `0.156152`, mean selected residual gap `-0.0152`.
- Adaptation efficiency `0.04933` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.084761` across 7 instances; family means: ch=0.066491, kroD=0.091528, pcb=0.203415, pr=0.034523, rd=0.037547, st=0.093333.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3289, "expected_gap": 0.400853, "family": "a", "name": "a280", "optimality_gap": 0.275301, "residual_gap": -0.125552}, {"best_known_cost": 629, "cost": 686, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.09062, "residual_gap": -0.163434}, {"best_known_cost": 7542, "cost": 8088, "expected_gap": 0.233068, "family": "berlin", "name": "berlin52", "optimality_gap": 0.072395, "residual_gap": -0.160673}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.197162`, synthetic `0.0`, combined `0.125467`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.158073`, mean hardness `0.331945`, size bias `0.148439`, and failure concentration `0.367262`.
- Replay selection diversity `0.14525`, mean selected expected gap `0.290998`, mean selected residual gap `0.034844`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.197162` across 7 instances; family means: ch=0.106733, kroD=0.360618, pcb=0.231104, pr=0.256363, rd=0.213401, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3620, "expected_gap": 0.399923, "family": "a", "name": "a280", "optimality_gap": 0.403645, "residual_gap": 0.003722}, {"best_known_cost": 14379, "cost": 17908, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.245427, "residual_gap": -0.076084}, {"best_known_cost": 629, "cost": 678, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.077901, "residual_gap": -0.184102}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.086663`, synthetic `0.0`, combined `0.055149`.
- Accepted-epoch count `3`, mean accepted code novelty `0.814708`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.230022`, size bias `0.120322`, and failure concentration `0.174426`.
- Replay selection diversity `0.196176`, mean selected expected gap `0.308952`, mean selected residual gap `-0.071071`.
- Adaptation efficiency `0.059496` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 1, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.086663` across 7 instances; family means: ch=0.094119, kroD=0.067061, pcb=0.177498, pr=0.058063, rd=0.083186, st=0.032593.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3435, "expected_gap": 0.398294, "family": "a", "name": "a280", "optimality_gap": 0.331912, "residual_gap": -0.066382}, {"best_known_cost": 14379, "cost": 18335, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.275123, "residual_gap": -0.046388}, {"best_known_cost": 629, "cost": 764, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.214626, "residual_gap": -0.052465}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.134684`, synthetic `0.003941`, combined `0.087141`.
- Accepted-epoch count `2`, mean accepted code novelty `0.645429`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.3043`, size bias `0.120322`, and failure concentration `0.17767`.
- Replay selection diversity `0.205344`, mean selected expected gap `0.31085`, mean selected residual gap `0.004015`.
- Adaptation efficiency `0.049276` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.134684` across 7 instances; family means: ch=0.160789, kroD=0.131492, pcb=0.224822, pr=0.091698, rd=0.068015, st=0.105185.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3604, "expected_gap": 0.39969, "family": "a", "name": "a280", "optimality_gap": 0.397441, "residual_gap": -0.002249}, {"best_known_cost": 14379, "cost": 19202, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.33542, "residual_gap": 0.014146}, {"best_known_cost": 7542, "cost": 9685, "expected_gap": 0.238849, "family": "berlin", "name": "berlin52", "optimality_gap": 0.284142, "residual_gap": 0.045293}]

## Judge Appendix
# Summary of Replay-Aware TSP Benchmark Results

## Key Metrics (Main Evidence for Transfer)
- **Held-out TSPLIB Gap** (mean_optimality_gap on heldout TSPLIB instances)
- **Synthetic Holdout Gap**
- **Transfer Gap**

| Condition                         | Held-out TSPLIB Gap | Synthetic Holdout Gap | Transfer Gap  | Archive Diversity | Archive Hardness | Archive Size Bias | Failure Concentration | Replay Mode               | Selection Mode   | Code Novelty (mean) | Notes                                                                                  |
|----------------------------------|---------------------|----------------------|---------------|-------------------|------------------|-------------------|-----------------------|--------------------------|------------------|---------------------|----------------------------------------------------------------------------------------|
| phase6_no_replay                 | 0.086291            | 0.010343             | 0.058674      | 0.240179          | 0.188586         | 0.0               | 0.0                   | none                     | score_only       | 0.764505            | Baseline; moderate gaps; no replay selection diversity or failure concentration          |
| phase6_random_replay             | 0.210832            | 0.012044             | 0.138545      | 0.236772          | 0.153461         | 8.3e-05           | 0.19457               | random                   | score_only       | 0.0                 | Poor transfer & tsplib gaps; no code novelty; moderate failure concentration             |
| phase6_failure_replay            | 0.143482            | 0.0                  | 0.091307      | 0.174718          | 0.319117         | 0.124979          | 0.23356               | failure                  | score_only       | 0.0                 | Best synthetic gap; improved transfer vs random replay; higher hardness and size bias   |
| phase6_random_replay_compression | 0.114249            | 0.0                  | 0.072704      | 0.236772          | 0.188799         | 0.0               | 0.19457               | random                   | novelty_gate     | 0.805692            | Compression active; intermediate transfer; high code novelty with similar archive diversity |
| phase6_stratified_random_replay  | 0.141226            | 0.0                  | 0.089871      | 0.240179          | 0.209654         | 0.0               | 0.221162              | stratified_random        | score_only       | 0.0                 | Slightly worse than failure replay on transfer; moderate failure concentration           |
| phase6_diversity_weighted_replay | 0.084761            | 0.003941             | 0.055372      | 0.240179          | 0.172416         | 0.0               | 0.105               | diversity_weighted       | score_only       | 0.817261            | Best held-out TSPLIB gap (0.08476); best synthetic gap near zero; best transfer gap also near top |
| phase6_residual_failure_replay   | 0.197162            | 0.0                  | 0.125467      | 0.18975           | 0.336098         | 0.127321          | 0.367262              | residual_failure         | score_only       | 0.0                 | Worst transfer & tsplib gaps; highest hardness and failure concentration                 |
| phase6_diversity_failure_replay  | 0.086663            | 0.0                  | 0.055149      | 0.174718          | 0.263054         | 0.124979          | 0.174426              | diversity_failure        | score_only       | 0.814708            | Best transfer gap (0.05515); near best held-out TSPLIB gap; reasonable hardness and failure concentration |
| phase6_diversity_failure_replay_compression | 0.134684   | 0.003941             | 0.087141      | 0.174718          | 0.348079         | 0.124979          | 0.17767               | diversity_failure        | novelty_gate     | 0.645429            | Compression on diversity_failure; transfer gap worse than non-compressed variant         |

## Interpretation:

### Transfer Performance
- **Top Transfer Performance:** Achieved by phase6_diversity_failure_replay (mean transfer gap 0.05515) and phase6_diversity_weighted_replay (0.05537), both significantly better than random or no-replay baselines.
- **Synthetic Holdout Gap:** Best synthetic gaps are near zero for phase6_failure_replay, phase6_diversity_weighted_replay, and compressed variants of diversity replay, implying better generalization to synthetic holdout distribution compared to random replay.
- **Held-out TSPLIB Gap:** phase6_diversity_weighted_replay achieves best held-out TSPLIB gap (0.08476), slightly better than no replay and diversity_failure replay.

### Replay Archive Characteristics (Mechanism Studies)
- **Archive Diversity:** Highest in no_replay, random replay with compression, and diversity-weighted replay (~0.24); lower in failure replay and diversity_failure variants (~0.17).
- **Archive Hardness:** Failure replay and residual_failure replay have higher hardness (~0.32–0.34). Diversity_failure replay adds hardness (~0.26).
- **Size Bias:** Failure replay and related diversity_failure variants have non-zero positive archive size bias (~0.12); others near zero.
- **Failure Concentration:** Residual_failure replay has highest (0.367), failure replay 0.234, diversity_failure replay ~0.17–0.19, random replay ~0.19, and no replay 0.0.

### Code Novelty vs Transfer
- **Code Novelty:** Lowest (0.0 mean) in replay modes involving failure or random replay without novelty gate.
- **High Code Novelty:** Observed with novelty gate and diversity-weighted replay (around 0.76–0.85).
- **Effect:** Despite code novelty drop in failure replay, transfer improves. Hence, better transfer is not due to increased code novelty but replay strategy.

### Replay Modes Comparison
- **No Replay ("none"):** Baseline has moderate transfer and held-out gaps.
- **Random Replay:** High transfer and optimality gaps, poor transfer.
- **Failure Replay:** Improves synthetic holdout gap to zero, better transfer but higher hardness and archive size bias.
- **Diversity Weighted Replay:** Achieves best held-out and synthetic holdout gaps with moderate hardness and low failure concentration.
- **Diversity Failure Replay:** Best transfer, balanced hardness, and failure concentration.
- **Residual Failure Replay:** Worst transfer and held-out gaps with highest hardness and failure concentration.
- **Compression-aware Replay:** Slight decrease in transfer over non-compressed variants but increase in code novelty.

---

# Overall Conclusions

- **Phase6 Diversity Weighted Replay** and **Phase6 Diversity Failure Replay** conditions achieve the best balance between transfer performance and solver optimality gaps, supported by low held-out TSPLIB and synthetic holdout gaps.
- Improved transfer does **not** correlate systematically with code novelty; failure-related replay modes lowered code novelty but improved transfer.
- Failure replay modes enhance archive hardness and concentrate on difficult instances but tend to increase failure concentration and size bias.
- Compression-aware variants reduce synthetic gap but at some cost to transfer performance.
- Random replay lacks transfer effectiveness despite moderate archive diversity.

---

# Recommendations

- Prioritize **diversity weighted replay** or **diversity failure replay** for benchmark scenarios aiming at optimal balance of transfer accuracy and archive quality.
- Avoid pure random replay due to poor transfer and large optimality gaps.
- Leverage failure replay archives to improve synthetic holdout performance but monitor for failure concentration bias effects.
- Use novelty gate selectively; increases code novelty but does not always improve transfer metric.
- Further analysis on archive diversity and failure concentration dynamics can refine replay sample selection.
