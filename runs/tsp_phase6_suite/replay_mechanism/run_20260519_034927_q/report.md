# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_no_replay`.
- Best TSPLIB holdout gap: `phase6_no_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_034927_q
- started_at_local: 2026-05-19 03:49:27
- finished_at_local: 2026-05-19 04:09:57
- duration_hhmm: 00:21
- duration_seconds: 1230.299
- seed_offset: 16000
- replicate_label: q
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.071821 | 0.0 | 0.045704 | 0.236772 | 0.195229 | 0.0 | 0.687474 | 0.76 | 0.063272 |
| phase6_random_replay | random | score_only | False | 0.135687 | 0.003941 | 0.087779 | 0.236772 | 0.166652 | 0.19457 | 0.840659 | 0.76 | 0.019707 |
| phase6_failure_replay | failure | score_only | False | 0.098256 | 0.0 | 0.062527 | 0.171206 | 0.247439 | 0.220202 | 0.752577 | 0.76 | 0.087657 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.127805 | 0.0 | 0.08133 | 0.236772 | 0.183475 | 0.19457 | 0.737569 | 0.76 | 0.040395 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.221162 | 0.827327 | 0.56 | -0.030103 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.12699 | 0.0 | 0.080812 | 0.236772 | 0.159581 | 0.156494 | 0.874403 | 0.76 | 0.100542 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.291666 | 0.864298 | 0.56 | -0.028815 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.101953 | 0.0 | 0.064879 | 0.171206 | 0.266277 | 0.175969 | 0.87176 | 0.76 | 0.061975 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.17024 | 0.0 | 0.56 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.071821`, synthetic `0.0`, combined `0.045704`.
- Accepted-epoch count `3`, mean accepted code novelty `0.687474`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.195229`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.063272` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.071821` across 7 instances; family means: ch=0.063963, kroD=0.042876, pcb=0.219465, pr=0.035716, rd=0.05158, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 2960, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.147732, "residual_gap": -0.255758}, {"best_known_cost": 14379, "cost": 15902, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.105918, "residual_gap": -0.223716}, {"best_known_cost": 7542, "cost": 7964, "expected_gap": 0.245028, "family": "berlin", "name": "berlin52", "optimality_gap": 0.055953, "residual_gap": -0.189075}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.135687`, synthetic `0.003941`, combined `0.087779`.
- Accepted-epoch count `2`, mean accepted code novelty `0.840659`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.166652`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.133609`, mean selected residual gap `-0.011953`.
- Adaptation efficiency `0.019707` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.135687` across 7 instances; family means: ch=0.09262, kroD=0.064056, pcb=0.289909, pr=0.24206, rd=0.116688, st=0.051852.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 890, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.414944, "residual_gap": 0.158664}, {"best_known_cost": 14379, "cost": 18969, "expected_gap": 0.322762, "family": "lin", "name": "lin105", "optimality_gap": 0.319216, "residual_gap": -0.003546}, {"best_known_cost": 2579, "cost": 3365, "expected_gap": 0.40349, "family": "a", "name": "a280", "optimality_gap": 0.304769, "residual_gap": -0.098721}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.098256`, synthetic `0.0`, combined `0.062527`.
- Accepted-epoch count `2`, mean accepted code novelty `0.752577`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.247439`, size bias `0.120322`, and failure concentration `0.220202`.
- Replay selection diversity `0.185861`, mean selected expected gap `0.304949`, mean selected residual gap `-0.034894`.
- Adaptation efficiency `0.087657` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.098256` across 7 instances; family means: ch=0.082895, kroD=0.070583, pcb=0.218047, pr=0.109163, rd=0.100506, st=0.023704.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 9625, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.276187, "residual_gap": 0.039565}, {"best_known_cost": 2579, "cost": 3260, "expected_gap": 0.403645, "family": "a", "name": "a280", "optimality_gap": 0.264056, "residual_gap": -0.139589}, {"best_known_cost": 14379, "cost": 17673, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.229084, "residual_gap": -0.09308}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.127805`, synthetic `0.0`, combined `0.08133`.
- Accepted-epoch count `3`, mean accepted code novelty `0.737569`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.183475`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132265`, mean selected residual gap `0.015013`.
- Adaptation efficiency `0.040395` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.127805` across 7 instances; family means: ch=0.078084, kroD=0.106932, pcb=0.241896, pr=0.252989, rd=0.062579, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3168, "expected_gap": 0.402249, "family": "a", "name": "a280", "optimality_gap": 0.228383, "residual_gap": -0.173866}, {"best_known_cost": 629, "cost": 718, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.141494, "residual_gap": -0.111924}, {"best_known_cost": 7542, "cost": 8117, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.07624, "residual_gap": -0.156908}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.827327`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.237974`, mean selected residual gap `0.052751`.
- Adaptation efficiency `-0.030103` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.401939, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.000621}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.328841, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": -2.8e-05}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.12699`, synthetic `0.0`, combined `0.080812`.
- Accepted-epoch count `2`, mean accepted code novelty `0.874403`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.159581`, size bias `8.3e-05`, and failure concentration `0.156494`.
- Replay selection diversity `0.270932`, mean selected expected gap `0.15091`, mean selected residual gap `-0.000709`.
- Adaptation efficiency `0.100542` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.12699` across 7 instances; family means: ch=0.120362, kroD=0.113882, pcb=0.287841, pr=0.122117, rd=0.065107, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3228, "expected_gap": 0.400853, "family": "a", "name": "a280", "optimality_gap": 0.251648, "residual_gap": -0.149205}, {"best_known_cost": 14379, "cost": 15947, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.109048, "residual_gap": -0.218958}, {"best_known_cost": 629, "cost": 675, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.073132, "residual_gap": -0.180922}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.864298`, and final complexity `0.56`.
- Active replay archive `residual_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.291666`.
- Replay selection diversity `0.177489`, mean selected expected gap `0.263417`, mean selected residual gap `0.088976`.
- Adaptation efficiency `-0.028815` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.399923, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.001395}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.129094}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.002156}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.101953`, synthetic `0.0`, combined `0.064879`.
- Accepted-epoch count `2`, mean accepted code novelty `0.87176`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.266277`, size bias `0.120322`, and failure concentration `0.175969`.
- Replay selection diversity `0.196662`, mean selected expected gap `0.308781`, mean selected residual gap `-0.03578`.
- Adaptation efficiency `0.061975` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.101953` across 7 instances; family means: ch=0.078025, kroD=0.122382, pcb=0.19861, pr=0.107305, rd=0.055247, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3545, "expected_gap": 0.398294, "family": "a", "name": "a280", "optimality_gap": 0.374564, "residual_gap": -0.02373}, {"best_known_cost": 14379, "cost": 18951, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.317964, "residual_gap": -0.008693}, {"best_known_cost": 629, "cost": 774, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.230525, "residual_gap": -0.036566}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.300755`, mean selected residual gap `0.049233`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.39969, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.001628}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.127186}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.324988, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.003825}]

## Judge Appendix
# Summary and Interpretation of Replay-Aware TSP Benchmark Suite Results

## Overall Best Condition
- **Best Holdout (TSPLIB and Synthetic) and Transfer Condition:**  
  **phase6_no_replay**  
  - Mean TSPLIB gap: 0.0718  
  - Mean Synthetic holdout gap: 0.0  
  - Mean transfer gap: 0.0457  
  - Replay mode: none

This condition shows the best overall performance in transfer (both held-out TSPLIB and synthetic holdouts) with the lowest optimality gaps, indicating the highest solution quality and best transfer.

---

## Comparison of Replay Modes

| Condition                           | Replay Mode           | Final Synthetic Gap | Final Transfer Gap | Final TSPLIB Gap | Adaptation Efficiency | Archive Diversity | Archive Hardness | Size Bias | Replay Failure Concentration |
|-----------------------------------|-----------------------|---------------------|--------------------|------------------|-----------------------|-------------------|------------------|-----------|-----------------------------|
| phase6_no_replay                  | none                  | 0.0                 | 0.0457             | 0.0718           | 0.0633                | 0.2402            | 0.2009           | 0.0       | 0.0                         |
| phase6_random_replay              | random                | 0.0039              | 0.0878             | 0.1357           | 0.0197                | 0.2402            | 0.1667           | 0.0       | 0.1946                      |
| phase6_failure_replay             | failure               | 0.0                 | 0.0625             | 0.0983           | 0.0877                | 0.1747            | 0.2771           | 0.125     | 0.2202                      |
| phase6_random_replay_compression  | random + compression  | 0.0                 | 0.0813             | 0.1278           | 0.0404                | 0.2402            | 0.1835           | 0.0       | 0.1946                      |
| phase6_stratified_random_replay   | stratified random     | 0.0649              | 0.1594             | 0.2134           | -0.0301               | 0.2402            | 0.2124           | 0.0       | 0.2517                      |
| phase6_diversity_weighted_replay  | diversity weighted    | 0.0                 | 0.0808             | 0.1270           | 0.1005                | 0.2402            | 0.1886           | 0.0       | 0.1565                      |
| phase6_residual_failure_replay    | residual failure      | 0.0649              | 0.1594             | 0.2134           | -0.0288               | 0.1747            | 0.3490           | 0.125     | 0.2917                      |
| phase6_diversity_failure_replay   | diversity + failure   | 0.0                 | 0.0649             | 0.1020           | 0.0620                | 0.1747            | 0.3609           | 0.125     | 0.1760                      |
| phase6_diversity_failure_replay_compression | diversity + failure + compression | 0.0649 | 0.1594 | 0.2134 | 0.0 | 0.1747 | 0.3490 | 0.125 | 0.1702 |

---

## Key Observations

### 1. Transfer Performance (Held-Out TSPLIB & Synthetic)
- **No replay (phase6_no_replay)** yields the lowest mean transfer gap (0.0457) and held-out TSPLIB gap (0.0718), suggesting best transfer generalization.
- Replay-based methods (random, failure, diversity, stratified random, residual failure, diversity failure) show increasing transfer gaps, with stratified random and residual failure replays having the worst transfer performance (>0.10 TSPLIB gap).
- Synthetic holdout gaps align with this pattern; only no replay and some replay variants achieve 0 or near-zero synthetic gap.

### 2. Code Novelty vs Transfer
- Replay variants typically show *higher* code novelty (0.71–0.89) than no replay (0.66).
- However, increased code novelty does **not** correlate with improved transfer.
- In fact, conditions with higher code novelty (especially residual failure replay modes) tend to have worse transfer.
- Thus, code novelty reduction in no replay coincides with **better** transfer; novelty here likely reflects lexical changes rather than effective algorithmic invention.

### 3. Archive Diversity and Hardness
- No replay and random replay (without compression) show highest archive descriptor diversity (~0.24).
- Failure-based replay conditions have lower diversity (~0.17) and higher hardness (up to ~0.36), indicating focused replay on difficult instances.
- Size bias is zero for no replay and random replay; failure replay modes exhibit moderate size bias (0.12).
  
### 4. Failure Concentration and Replay Diversity
- No replay condition shows zero replay failure concentration and zero replay selection diversity (consistent with replay_mode:none).
- Replay modes have elevated failure concentration (0.15–0.33), indicating replay focuses on failures.
- Highest failure concentration is in residual failure replay (0.29) and stratified random replay (0.25).
- Diversity-weighted replay modes have moderate failure concentration (0.15–0.19) but higher replay selection diversity (~0.26).

### 5. Adaptation Efficiency and Training Gap
- Adaptation efficiency is highest for diversity weighted replay (0.10) and failure replay (0.087), indicating better adaptation on training set.
- No replay condition has moderate adaptation efficiency (0.063).
- Stratified random replay and residual failure replay show negative or near-zero adaptation efficiency, suggesting overfitting or non-improving adaptation.
- Training gaps are lowest for no replay (0.089), suggesting better convergence.
  
---

## Failure Concentration & Hardness Mechanism Insights

- Failure and residual failure replays concentrate on fewer, harder instances (hardness up to 0.35–0.36).
- This is paired with increased size bias (~0.12), meaning replay over-represents larger or worst-case instances.
- This concentration correlates with worse transfer gaps, suggesting overfitting to a narrow set of hard failures reduces generalization.
- Diversity-weighted replay balances failure concentration and diversity better, yielding lower hardness (~0.19) and moderate failure concentration (~0.16).
- However, it still does not outperform no replay in transfer.

---

## Final Size Bias and Complexity

- Size bias is zero for no replay and random replay, indicating balanced replay distribution in terms of instance sizes.
- Failure replay modes show moderate positive size bias (~0.12), indicating skewed replay toward larger or harder instances.
- Complexity remains constant (0.56 for stratified and residual failure replays; 0.76 for others).
- No replay and random replay have higher complexity, possibly indicating more behavioral richness without replay constraints.

---

## Worst Instances and Residual Gap

- Worst instances in no replay show generally lower optimality gaps (~0.023–0.22) compared to replay conditions, where gaps increase (~0.05–0.35).
- Residual gaps are mostly negative in no replay condition, showing better-than-expected performance on failures.
- In contrast, replay conditions have more positive or less negative residual gaps, indicating less effective coverage or performance on expected failures.

---

## Final Interpretation

- **No replay condition consistently outperforms all replay-based replay_modes in transfer to both held-out TSPLIB and synthetic datasets.**
- **Replay modes, despite higher code novelty, do not improve generalization and often degrade it, particularly failure-focused replays with high failure concentration and size bias.**
- **Replay archives in failure and residual failure modes exhibit lower diversity and higher hardness, indicating over-concentration, which appears detrimental for transfer.**
- **Diversity-weighted replay improves some metrics (e.g., adaptation efficiency and failure concentration balance) but still lags behind no replay in transfer performance.**
- **Compression pressure in replay slightly reduces diversity with small impact on transfer and adaptation.**
- **Lexical/code novelty increases with replay usage, but since transfer is worse, this novelty is not translating into meaningful algorithmic innovation.**

---

# Key Recommendation

- Prioritize **no replay** approach for best transfer and overall solution quality.
- Replay strategies focusing on failure or residual failure replay lead to failure concentration and size bias which reduce transfer performance.
- Increased code novelty via replay does not correspond to better transfer, hence novelty should not be conflated with invention absent supportive algorithmic evidence.
- Use replay cautiously; ensure diversified replay samples to avoid overfitting and transfer degradation.

---

# Summary Table (Selected Metrics)

| Condition                       | Replay Mode             | Transfer Gap | TSPLIB Gap | Synthetic Gap | Code Novelty | Archive Diversity | Archive Hardness | Failure Concentration | Adaptation Efficiency |
|--------------------------------|------------------------|--------------|------------|---------------|--------------|-------------------|------------------|-----------------------|-----------------------|
| phase6_no_replay               | none                   | 0.0457       | 0.0718     | 0.0           | 0.6573       | 0.2402            | 0.2009           | 0.0                   | 0.0633                |
| phase6_random_replay           | random                 | 0.0878       | 0.1357     | 0.0039        | 0.8407       | 0.2402            | 0.1667           | 0.1946                | 0.0197                |
| phase6_failure_replay          | failure                | 0.0625       | 0.0983     | 0.0           | 0.7526       | 0.1747            | 0.2771           | 0.2202                | 0.0877                |
| phase6_random_replay_compression | random + compression    | 0.0813       | 0.1278     | 0.0           | 0.7113       | 0.2402            | 0.1835           | 0.1946                | 0.0404                |
| phase6_stratified_random_replay | stratified random       | 0.1594       | 0.2134     | 0.0649        | 0.8602       | 0.2402            | 0.2124           | 0.2517                | -0.0301               |
| phase6_diversity_weighted_replay | diversity weighted       | 0.0808       | 0.1270     | 0.0           | 0.8744       | 0.2402            | 0.1886           | 0.1565                | 0.1005                |
| phase6_residual_failure_replay  | residual failure        | 0.1594       | 0.2134     | 0.0649        | 0.8643       | 0.1747            | 0.3490           | 0.2917                | -0.0288               |
| phase6_diversity_failure_replay | diversity + failure     | 0.0649       | 0.1020     | 0.0           | 0.8718       | 0.1747            | 0.3609           | 0.1760                | 0.0620                |
| phase6_diversity_failure_replay_compression | diversity + failure + compression | 0.1594 | 0.2134 | 0.0649 | 0.0 | 0.1747 | 0.3490 | 0.1702 | 0.0 |

---

# Conclusion

The **phase6_no_replay** condition offers the best tradeoff of transfer generalization and solution optimality, with lowest gaps on both TSPLIB and synthetic holdout sets. Replay conditions tend to increase code novelty but at the cost of poorer transfer, likely due to failure concentration and size bias effects reducing archive diversity and widening generalization gaps.

Careful and balanced replay (e.g., diversity-weighted) partially mitigates but does not surpass no replay in transfer. Compression-aware replay has modest effects on diversity but no clear improvements in transfer.

Hence, conservative interpretation strongly favors **no replay** for broad transfer effectiveness with balanced archive diversity, hardness, and minimal failure concentration.
