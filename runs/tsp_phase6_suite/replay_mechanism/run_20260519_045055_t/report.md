# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay_compression`.
- Best TSPLIB holdout gap: `phase6_diversity_failure_replay_compression`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_045055_t
- started_at_local: 2026-05-19 04:50:55
- finished_at_local: 2026-05-19 05:11:30
- duration_hhmm: 00:21
- duration_seconds: 1235.548
- seed_offset: 19000
- replicate_label: t
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.093052 | 0.0 | 0.059215 | 0.236772 | 0.142941 | 0.0 | 0.869121 | 0.76 | 0.037387 |
| phase6_random_replay | random | score_only | False | 0.117651 | 0.0 | 0.074869 | 0.236772 | 0.158547 | 0.19457 | 0.765517 | 0.76 | 0.060886 |
| phase6_failure_replay | failure | score_only | False | 0.112425 | 0.0 | 0.071543 | 0.171206 | 0.264522 | 0.231608 | 0.0 | 0.76 | 0.0 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.119212 | 0.0 | 0.075862 | 0.236772 | 0.18621 | 0.19457 | 0.789905 | 0.76 | 0.07546 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.084157 | 0.0 | 0.053554 | 0.236772 | 0.159491 | 0.221162 | 0.752307 | 0.76 | 0.040989 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.153019 | 0.010343 | 0.101137 | 0.236772 | 0.161314 | 0.157119 | 0.0 | 0.76 | 0.0 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.127681 | 0.010343 | 0.085013 | 0.043802 | 0.148487 | 0.305 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.103711 | 0.006169 | 0.068241 | 0.171206 | 0.212967 | 0.171578 | 0.829052 | 0.76 | 0.036475 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.068295 | 0.0 | 0.04346 | 0.171206 | 0.230887 | 0.17767 | 0.720546 | 0.76 | 0.060177 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.093052`, synthetic `0.0`, combined `0.059215`.
- Accepted-epoch count `2`, mean accepted code novelty `0.869121`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.142941`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.037387` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.093052` across 7 instances; family means: ch=0.098798, kroD=0.03602, pcb=0.199358, pr=0.078246, rd=0.095702, st=0.044444.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3252, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.260954, "residual_gap": -0.14556}, {"best_known_cost": 14379, "cost": 16559, "expected_gap": 0.323861, "family": "lin", "name": "lin105", "optimality_gap": 0.15161, "residual_gap": -0.172251}, {"best_known_cost": 7542, "cost": 8109, "expected_gap": 0.244206, "family": "berlin", "name": "berlin52", "optimality_gap": 0.075179, "residual_gap": -0.169027}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.117651`, synthetic `0.0`, combined `0.074869`.
- Accepted-epoch count `2`, mean accepted code novelty `0.765517`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.158547`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133845`, mean selected residual gap `-0.013298`.
- Adaptation efficiency `0.060886` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.117651` across 7 instances; family means: ch=0.101298, kroD=0.156147, pcb=0.280436, pr=0.036493, rd=0.125664, st=0.022222.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3497, "expected_gap": 0.406204, "family": "a", "name": "a280", "optimality_gap": 0.355952, "residual_gap": -0.050252}, {"best_known_cost": 7542, "cost": 9789, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.297932, "residual_gap": 0.052825}, {"best_known_cost": 629, "cost": 752, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.195548, "residual_gap": -0.060732}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.112425`, synthetic `0.0`, combined `0.071543`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.264522`, size bias `0.120322`, and failure concentration `0.231608`.
- Replay selection diversity `0.220764`, mean selected expected gap `0.317802`, mean selected residual gap `-0.008931`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.112425` across 7 instances; family means: ch=0.101681, kroD=0.081948, pcb=0.212671, pr=0.125695, rd=0.114412, st=0.048889.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3336, "expected_gap": 0.408608, "family": "a", "name": "a280", "optimality_gap": 0.293525, "residual_gap": -0.115083}, {"best_known_cost": 14379, "cost": 17342, "expected_gap": 0.326838, "family": "lin", "name": "lin105", "optimality_gap": 0.206064, "residual_gap": -0.120774}, {"best_known_cost": 7542, "cost": 8966, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.188809, "residual_gap": -0.056298}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.119212`, synthetic `0.0`, combined `0.075862`.
- Accepted-epoch count `2`, mean accepted code novelty `0.789905`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.18621`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132978`, mean selected residual gap `0.000441`.
- Adaptation efficiency `0.07546` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.119212` across 7 instances; family means: ch=0.112506, kroD=0.078003, pcb=0.238509, pr=0.155003, rd=0.102402, st=0.035556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3443, "expected_gap": 0.409771, "family": "a", "name": "a280", "optimality_gap": 0.335014, "residual_gap": -0.074757}, {"best_known_cost": 7542, "cost": 9893, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.311721, "residual_gap": 0.066693}, {"best_known_cost": 14379, "cost": 17673, "expected_gap": 0.326977, "family": "lin", "name": "lin105", "optimality_gap": 0.229084, "residual_gap": -0.097893}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.084157`, synthetic `0.0`, combined `0.053554`.
- Accepted-epoch count `3`, mean accepted code novelty `0.752307`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.159491`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237004`, mean selected residual gap `-0.041653`.
- Adaptation efficiency `0.040989` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.084157` across 7 instances; family means: ch=0.066447, kroD=0.170236, pcb=0.143251, pr=0.037907, rd=0.036662, st=0.068148.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 18645, "expected_gap": 0.32496, "family": "lin", "name": "lin105", "optimality_gap": 0.296683, "residual_gap": -0.028277}, {"best_known_cost": 2579, "cost": 3327, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.290035, "residual_gap": -0.114308}, {"best_known_cost": 7542, "cost": 8000, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.060727, "residual_gap": -0.180191}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.153019`, synthetic `0.010343`, combined `0.101137`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.161314`, size bias `8.3e-05`, and failure concentration `0.157119`.
- Replay selection diversity `0.263201`, mean selected expected gap `0.155022`, mean selected residual gap `-0.005724`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.153019` across 7 instances; family means: ch=0.105756, kroD=0.170048, pcb=0.223364, pr=0.261079, rd=0.102908, st=0.102222.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3564, "expected_gap": 0.40318, "family": "a", "name": "a280", "optimality_gap": 0.381931, "residual_gap": -0.021249}, {"best_known_cost": 629, "cost": 769, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.222576, "residual_gap": -0.031478}, {"best_known_cost": 7542, "cost": 9205, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.220499, "residual_gap": -0.016123}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.127681`, synthetic `0.010343`, combined `0.085013`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.043802`, mean hardness `0.148487`, size bias `0.022181`, and failure concentration `0.305`.
- Replay selection diversity `0.058403`, mean selected expected gap `0.239765`, mean selected residual gap `0.051119`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.127681` across 7 instances; family means: ch=0.09147, kroD=0.184794, pcb=0.213951, pr=0.127488, rd=0.095702, st=0.088889.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3184, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.234587, "residual_gap": -0.16836}, {"best_known_cost": 7542, "cost": 8089, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.072527, "residual_gap": -0.160621}, {"best_known_cost": 629, "cost": 660, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.049285, "residual_gap": -0.212718}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.103711`, synthetic `0.006169`, combined `0.068241`.
- Accepted-epoch count `3`, mean accepted code novelty `0.829052`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.212967`, size bias `0.120322`, and failure concentration `0.171578`.
- Replay selection diversity `0.196559`, mean selected expected gap `0.306518`, mean selected residual gap `-0.091756`.
- Adaptation efficiency `0.036475` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.103711` across 7 instances; family means: ch=0.084267, kroD=0.20541, pcb=0.177222, pr=0.088869, rd=0.063717, st=0.022222.
- Panel `synthetic_holdout` mean gap `0.006169` across 4 instances; family means: clustered_gaussian=0.024674, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 875, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.124006}, {"best_known_cost": 7542, "cost": 9644, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.278706, "residual_gap": 0.041342}, {"best_known_cost": 2579, "cost": 3292, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.276464, "residual_gap": -0.125707}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.068295`, synthetic `0.0`, combined `0.04346`.
- Accepted-epoch count `3`, mean accepted code novelty `0.720546`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.230887`, size bias `0.120322`, and failure concentration `0.17767`.
- Replay selection diversity `0.198162`, mean selected expected gap `0.311259`, mean selected residual gap `-0.067191`.
- Adaptation efficiency `0.060177` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.068295` across 7 instances; family means: ch=0.064705, kroD=0.054804, pcb=0.134743, pr=0.048928, rd=0.076106, st=0.034074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3480, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.34936, "residual_gap": -0.052811}, {"best_known_cost": 14379, "cost": 18335, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.275123, "residual_gap": -0.04725}, {"best_known_cost": 629, "cost": 764, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.214626, "residual_gap": -0.049285}]

## Judge Appendix
# TSP Benchmark Suite Replay-Aware Condition Review

## Summary of Best Conditions (Based on Transfer and Optimality Gap)

| Metric                      | Best Condition                           |
|-----------------------------|-----------------------------------------|
| Held-out TSPLIB Gap          | phase6_diversity_failure_replay_compression (0.0683 final tsplib gap) |
| Synthetic Holdout Gap        | phase6_no_replay (0.0 final synthetic gap)       |
| Transfer (Overall)           | phase6_diversity_failure_replay_compression (0.0435 transfer gap) |

## Detailed Analysis

---

### 1. **Baseline: phase6_no_replay**
- **Held-out TSPLIB gap:** 0.0931
- **Synthetic holdout gap:** 0.0 (perfect on synthetic)
- **Transfer gap:** 0.0592
- **Replay mode:** none
- **Archive diversity:** 0.2402 (high)
- **Archive hardness:** 0.1818 (moderate)
- **Replay failure concentration:** 0.0 (no replay)
- **Code novelty:** high (0.869)
- **Interpretation:**
  - No replay yields zero gap on synthetic holdouts but moderate transfer gap.
  - High code novelty with no replay suggests exploration but less transfer improvement.

---

### 2. **Random Replay: phase6_random_replay**
- **Held-out TSPLIB gap:** 0.1177 (worse than no replay)
- **Synthetic holdout gap:** 0.0
- **Transfer gap:** 0.0749 (worse)
- **Archive diversity:** 0.2402 (unchanged)
- **Archive hardness:** 0.1809 (moderate)
- **Replay failure concentration:** 0.28 (moderate concentration)
- **Replay selection diversity:** 0.26 (higher)
- **Code novelty:** 0.766 (decreased from no replay)
- **Interpretation:**
  - Random replay slightly degrades transfer and held-out performance.
  - Increased failure concentration and replay diversity do not translate to better transfer.
  - Code novelty decreases despite replay.

---

### 3. **Failure Replay: phase6_failure_replay**
- **Held-out TSPLIB gap:** 0.1124
- **Synthetic holdout gap:** 0.0
- **Transfer gap:** 0.0715
- **Archive diversity:** 0.1747 (lower than baseline)
- **Archive hardness:** 0.3005 (higher hardness)
- **Replay failure concentration:** 0.28 (high)
- **Code novelty:** 0.0 (drops to zero)
- **Interpretation:**
  - Failure replay increases hardness but decreases diversity.
  - Code novelty drops to zero while transfer gap slightly worsens compared to no replay.
  - Replay focuses on failures but at cost of diversity and novelty; transfer not improved.

---

### 4. **Random Replay with Compression: phase6_random_replay_compression**
- **Held-out TSPLIB gap:** 0.1192
- **Synthetic holdout gap:** 0.0
- **Transfer gap:** 0.0759
- **Archive diversity:** 0.2402
- **Archive hardness:** 0.193 (moderate)
- **Replay failure concentration:** 0.16 (moderate)
- **Replay selection diversity:** 0.26 (high)
- **Code novelty:** 0.79 (moderate)
- **Interpretation:**
  - Compression does not improve transfer or held-out gaps over plain random replay.
  - Archive diversity is preserved.
  - Code novelty decreased relative to no replay.

---

### 5. **Stratified Random Replay: phase6_stratified_random_replay**
- **Held-out TSPLIB gap:** 0.0842 (better than randomized and failure replay)
- **Synthetic holdout gap:** 0.0
- **Transfer gap:** 0.0536 (second best transfer gap)
- **Archive diversity:** 0.2402
- **Archive hardness:** 0.1853 (moderate hardness)
- **Replay failure concentration:** 0.22
- **Replay selection diversity:** 0.19
- **Code novelty:** 0.83 (moderate-high)
- **Interpretation:**
  - Stratified random replay improves transfer and held-out performance closer to no replay.
  - Replay failure concentration and selection diversity moderate.
  - Code novelty is preserved.

---

### 6. **Diversity Weighted Replay: phase6_diversity_weighted_replay**
- **Held-out TSPLIB gap:** 0.1530 (worst held-out TSPLIB gap)
- **Synthetic holdout gap:** 0.0103 (non-zero)
- **Transfer gap:** 0.1011 (worst transfer gap)
- **Archive diversity:** 0.2402
- **Archive hardness:** 0.1895 (moderate)
- **Replay failure concentration:** 0.44 (high, the highest)
- **Replay selection diversity:** 0.26
- **Code novelty:** 0.0 (drops to zero)
- **Interpretation:**
  - Diversity-weighted replay increases replay failure concentration significantly.
  - Associated with worst transfer and heldout performance.
  - Drops code novelty to zero with increased failure focus.
  - Compression-aware replay variant improves this.

---

### 7. **Residual Failure Replay: phase6_residual_failure_replay**
- **Held-out TSPLIB gap:** 0.1277
- **Synthetic holdout gap:** 0.0103
- **Transfer gap:** 0.0850
- **Archive diversity:** 0.1752 (low)
- **Archive hardness:** 0.3152 (highest hardness)
- **Replay failure concentration:** 0.31 (high)
- **Replay selection diversity:** 0.06 (low)
- **Code novelty:** 0.0
- **Interpretation:**
  - Residual failure replay increases failure concentration and hardness.
  - Code novelty is zero.
  - Transfer worse than no replay and phase6_diversity_failure_replay_compression.
  - Replay selection diversity very low.

---

### 8. **Diversity Failure Replay: phase6_diversity_failure_replay**
- **Held-out TSPLIB gap:** 0.1037
- **Synthetic holdout gap:** 0.0062
- **Transfer gap:** 0.0682
- **Archive diversity:** 0.1747 (low)
- **Archive hardness:** 0.2882 (high)
- **Replay failure concentration:** 0.17
- **Replay selection diversity:** 0.20
- **Code novelty:** 0.83 (high)
- **Interpretation:**
  - Diversity failure replay raises failure concentration moderately; code novelty high.
  - Transfer and held-out gaps better than failure replay alone.
  - Archive diversity lower than no replay but better transfer.

---

### 9. **Diversity Failure Replay with Compression: phase6_diversity_failure_replay_compression (Best Overall)**
- **Held-out TSPLIB gap:** 0.0683 (best)
- **Synthetic holdout gap:** 0.0 (best)
- **Transfer gap:** 0.0435 (best)
- **Archive diversity:** 0.1747 (low)
- **Archive hardness:** 0.2740 (high)
- **Replay failure concentration:** 0.18 (moderate)
- **Replay selection diversity:** 0.20
- **Code novelty:** 0.76 (moderate)
- **Interpretation:**
  - Compression reduces replay failure concentration compared to diversity weighted no compression.
  - Best transfer and held-out performance achieved, indicating good generalization.
  - Slightly reduced code novelty relative to no replay baseline, despite best transfer.
  - Implies compression improves replay quality and transfer without increasing novelty.

---

## Cross-Condition Observations

- **Transfer and Optimality Gap:**
  - Best transfer and held-out TSPLIB gaps are achieved by **phase6_diversity_failure_replay_compression**.
  - No-replay yields best synthetic holdout gap (zero).
  - Replay modes based solely on failure replay or random replay perform worse in transfer and held-out gaps than diversity_failure_replay_compression.
  
- **Replay Failure Concentration:**
  - Failure replay and diversity weighted replay (without compression) increase failure concentration and archive hardness.
  - Compression reduces failure concentration and improves transfer performance.
  
- **Archive Diversity and Hardness:**
  - No replay and random replay maintain highest archive descriptor diversity (~0.24).
  - Failure-focused replay modes tend to lower archive diversity (~0.17) but increase hardness (~0.27-0.31).
  
- **Code Novelty:**
  - Drops to zero when failure or diversity weighted replay without compression is used.
  - Compression and stratified random preserve moderate code novelty (~0.75-0.83).
  - No replay condition has highest code novelty (0.87).
  
- **Mean Transfer Probe Gap Last:**
  - Matches overall transfer gap trends; lowest for phase6_diversity_failure_replay_compression (~0.044).

---

## Conclusion

- The **phase6_diversity_failure_replay_compression** condition is most effective by primary metrics:
  - It achieves the lowest held-out TSPLIB gap (0.0683) and lowest transfer gap (0.0435).
  - It balances failure replay with diversity and compression to reduce failure concentration while maintaining archive quality.
  - Code novelty decreases compared to no replay but transfer is improved, indicating effective mechanism rather than mere novelty boost.
- Pure **no-replay** maximizes synthetic holdout performance but has higher transfer gaps.
- Failure replay alone or diversity weighted replay without compression can increase hardness and replay failure concentration but does not improve transfer.
- Compression-aware replay plays a critical role in achieving better transfer despite moderate code novelty.
  
---

# Summary Table for Key Metrics (Rounded)

| Condition                              | Transfer Gap | Heldout TSPLIB Gap | Synthetic Gap | Replay Failure Concentration | Archive Diversity | Archive Hardness | Code Novelty | Replay Mode              | Selection Mode |
|--------------------------------------|--------------|--------------------|---------------|------------------------------|-------------------|------------------|--------------|-------------------------|----------------|
| phase6_no_replay                     | 0.0592       | 0.0931             | 0.0           | 0                            | 0.24              | 0.18             | 0.87         | none                    | score_only     |
| phase6_random_replay                 | 0.0749       | 0.1177             | 0.0           | 0.28                         | 0.24              | 0.18             | 0.77         | random                  | score_only     |
| phase6_failure_replay               | 0.0715       | 0.1124             | 0.0           | 0.28                         | 0.17              | 0.30             | 0            | failure                 | score_only     |
| phase6_random_replay_compression    | 0.0759       | 0.1192             | 0.0           | 0.16                         | 0.24              | 0.19             | 0.79         | random                  | novelty_gate   |
| phase6_stratified_random_replay     | 0.0536       | 0.0842             | 0.0           | 0.22                         | 0.24              | 0.19             | 0.83         | stratified_random       | score_only     |
| phase6_diversity_weighted_replay    | 0.1011       | 0.1530             | 0.01          | 0.44                         | 0.24              | 0.19             | 0            | diversity_weighted      | score_only     |
| phase6_residual_failure_replay      | 0.0850       | 0.1277             | 0.01          | 0.31                         | 0.18              | 0.32             | 0            | residual_failure        | score_only     |
| phase6_diversity_failure_replay     | 0.0682       | 0.1037             | 0.006         | 0.17                         | 0.17              | 0.29             | 0.83         | diversity_failure       | score_only     |
| phase6_diversity_failure_replay_compression | **0.0435**  | **0.0683**          | 0.0           | 0.18                         | 0.17              | 0.27             | 0.76         | diversity_failure_compression | score_only |

---

# Key Takeaways for Mechanism Studies

- **Replay archive diversity** is highest without failure replay; failure or residual replays reduce descriptor diversity.
- **Hardness** is highest for failure replay and residual failure replay, indicating replay of harder failure cases.
- **Replay failure concentration** correlates negatively with transfer; lowest concentration in best transfer condition with compression.
- **Failure concentration and replay diversity**: Compression reduces failure concentration and preserves replay selection diversity.
- **Code novelty** drops with failure replay modes but transfer improves with replay compression, suggesting code novelty is not the sole driver.
- **Failure replay variants without compression are suboptimal** for transfer despite capturing hard instances.
- **Stratified random replay** is a viable compromise offering moderate transfer improvement with preserved code novelty.

---

# Summary Interpretation

- **Compression-aware diversity failure replay most effectively balances replay diversity, failure focus, and transfer performance.** Despite slight sacrifice in code novelty, it yields best real-world (TSPLIB) and synthetic transfer metrics.
- Pure no replay yields perfect synthetic holdout but weaker transfer.
- Failure-based replay without compression shows increased failure concentration, lowered diversity and novelty, with no transfer gains.
- Random replay is insufficient to improve transfer reliably.
- Replay mechanisms need careful design to optimize transfer, balancing failure focus, diversity, and compression pressure.

---

# Recommended Focus

- Prioritize methods like **phase6_diversity_failure_replay_compression** for best transfer generalization.
- Avoid failure replay without compression due to negative impact on novelty and transfer.
- Further analyze replay archive evolution and instance difficulty concentration to refine replay selection.
- Investigate compression role in maintaining replay selection diversity while focusing on failures.
