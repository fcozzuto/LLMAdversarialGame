# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_diversity_failure_replay`.
- Best TSPLIB holdout gap: `phase6_diversity_failure_replay`.
- Best synthetic holdout gap: `phase6_no_replay`.

## Run Metadata
- run_name: run_20260519_025104_n
- started_at_local: 2026-05-19 02:51:04
- finished_at_local: 2026-05-19 03:10:24
- duration_hhmm: 00:19
- duration_seconds: 1159.78
- seed_offset: 13000
- replicate_label: n
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.174494 | 0.0 | 0.111042 | 0.236772 | 0.172282 | 0.0 | 0.0 | 0.76 | 0.0 |
| phase6_random_replay | random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.877409 | 0.56 | -0.028385 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.858871 | 0.56 | -0.028997 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.19457 | 0.0 | 0.56 | 0.0 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.236772 | 0.214847 | 0.221162 | 0.838815 | 0.56 | -0.029691 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.21187 | 0.012851 | 0.139499 | 0.236772 | 0.20261 | 0.157984 | 0.883171 | 0.76 | 0.03608 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.170999 | 0.033002 | 0.120818 | 0.103588 | 0.279145 | 0.373989 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.086522 | 0.003941 | 0.056493 | 0.171206 | 0.274538 | 0.175969 | 0.75225 | 0.76 | 0.055089 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.097906 | 0.0 | 0.062304 | 0.171206 | 0.297051 | 0.17024 | 0.74822 | 0.76 | 0.07288 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.174494`, synthetic `0.0`, combined `0.111042`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.172282`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.174494` across 7 instances; family means: ch=0.162127, kroD=0.229501, pcb=0.18636, pr=0.308601, rd=0.14311, st=0.02963.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3441, "expected_gap": 0.401318, "family": "a", "name": "a280", "optimality_gap": 0.334238, "residual_gap": -0.06708}, {"best_known_cost": 629, "cost": 815, "expected_gap": 0.257552, "family": "eil", "name": "eil101", "optimality_gap": 0.295707, "residual_gap": 0.038155}, {"best_known_cost": 7542, "cost": 9022, "expected_gap": 0.233148, "family": "berlin", "name": "berlin52", "optimality_gap": 0.196234, "residual_gap": -0.036914}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.877409`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.13344`, mean selected residual gap `0.037926`.
- Adaptation efficiency `-0.028385` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402559, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001241}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.323194, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.005619}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.858871`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.308036`, mean selected residual gap `0.067721`.
- Adaptation efficiency `-0.028997` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402249, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.000931}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.322373, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00644}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.131954`, mean selected residual gap `0.039412`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.402327, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.001009}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.253418, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.137679}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321803, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.00701}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.838815`, and final complexity `0.56`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.214847`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236142`, mean selected residual gap `0.054584`.
- Adaptation efficiency `-0.029691` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.398294, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": 0.003024}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.134817}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": 0.007302}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.21187`, synthetic `0.012851`, combined `0.139499`.
- Accepted-epoch count `2`, mean accepted code novelty `0.883171`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.20261`, size bias `8.3e-05`, and failure concentration `0.157984`.
- Replay selection diversity `0.264539`, mean selected expected gap `0.167566`, mean selected residual gap `0.016546`.
- Adaptation efficiency `0.03608` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 6, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.21187` across 7 instances; family means: ch=0.167822, kroD=0.218841, pcb=0.256272, pr=0.323108, rd=0.224779, st=0.124444.
- Panel `synthetic_holdout` mean gap `0.012851` across 4 instances; family means: clustered_gaussian=0.051405, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3370, "expected_gap": 0.400465, "family": "a", "name": "a280", "optimality_gap": 0.306708, "residual_gap": -0.093757}, {"best_known_cost": 7542, "cost": 9692, "expected_gap": 0.243888, "family": "berlin", "name": "berlin52", "optimality_gap": 0.28507, "residual_gap": 0.041182}, {"best_known_cost": 14379, "cost": 17825, "expected_gap": 0.321511, "family": "lin", "name": "lin105", "optimality_gap": 0.239655, "residual_gap": -0.081856}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.170999`, synthetic `0.033002`, combined `0.120818`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.103588`, mean hardness `0.279145`, size bias `0.063146`, and failure concentration `0.373989`.
- Replay selection diversity `0.123685`, mean selected expected gap `0.26959`, mean selected residual gap `0.049915`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.170999` across 7 instances; family means: ch=0.150645, kroD=0.192683, pcb=0.248454, pr=0.235893, rd=0.122377, st=0.096296.
- Panel `synthetic_holdout` mean gap `0.033002` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.132009, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 9442, "expected_gap": 0.238849, "family": "berlin", "name": "berlin52", "optimality_gap": 0.251923, "residual_gap": 0.013074}, {"best_known_cost": 2579, "cost": 3155, "expected_gap": 0.399612, "family": "a", "name": "a280", "optimality_gap": 0.223342, "residual_gap": -0.17627}, {"best_known_cost": 14379, "cost": 16895, "expected_gap": 0.321274, "family": "lin", "name": "lin105", "optimality_gap": 0.174977, "residual_gap": -0.146297}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.086522`, synthetic `0.003941`, combined `0.056493`.
- Accepted-epoch count `3`, mean accepted code novelty `0.75225`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.274538`, size bias `0.120322`, and failure concentration `0.175969`.
- Replay selection diversity `0.196315`, mean selected expected gap `0.308158`, mean selected residual gap `-0.026056`.
- Adaptation efficiency `0.055089` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.086522` across 7 instances; family means: ch=0.047755, kroD=0.119658, pcb=0.237997, pr=0.031602, rd=0.048293, st=0.072593.
- Panel `synthetic_holdout` mean gap `0.003941` across 4 instances; family means: clustered_gaussian=0.015764, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3373, "expected_gap": 0.398139, "family": "a", "name": "a280", "optimality_gap": 0.307871, "residual_gap": -0.090268}, {"best_known_cost": 14379, "cost": 16278, "expected_gap": 0.317296, "family": "lin", "name": "lin105", "optimality_gap": 0.132068, "residual_gap": -0.185228}, {"best_known_cost": 7542, "cost": 8009, "expected_gap": 0.244206, "family": "berlin", "name": "berlin52", "optimality_gap": 0.06192, "residual_gap": -0.182286}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.097906`, synthetic `0.0`, combined `0.062304`.
- Accepted-epoch count `3`, mean accepted code novelty `0.74822`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.297051`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.301728`, mean selected residual gap `-0.010389`.
- Adaptation efficiency `0.07288` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 5, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.097906` across 7 instances; family means: ch=0.035588, kroD=0.087161, pcb=0.238391, pr=0.108091, rd=0.106448, st=0.074074.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3335, "expected_gap": 0.400776, "family": "a", "name": "a280", "optimality_gap": 0.293137, "residual_gap": -0.107639}, {"best_known_cost": 14379, "cost": 16366, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.138188, "residual_gap": -0.190541}, {"best_known_cost": 629, "cost": 675, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.073132, "residual_gap": -0.190779}]

## Judge Appendix
### Key Overall Results

| Condition                        | Replay Mode           | Selection Mode    | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Code Novelty (mean) | Archive Diversity | Archive Hardness | Failure Concentration (final) |
|---------------------------------|----------------------|-------------------|------------------|---------------------|--------------------|---------------------|-------------------|------------------|------------------------------|
| phase6_no_replay                | none                 | score_only        | 0.174494         | 0.0                 | 0.111042           | 0.0                 | 0.240179          | 0.199806         | 0.0                          |
| phase6_random_replay            | random               | score_only        | 0.213387         | 0.064916            | 0.159398           | 0.877409            | 0.236772          | 0.214847         | 0.306122                     |
| phase6_failure_replay           | failure              | score_only        | 0.213387         | 0.064916            | 0.159398           | 0.858871            | 0.171206          | 0.348017         | 0.261637                     |
| phase6_random_replay_compression| random + compression | novelty_gate      | 0.213387         | 0.064916            | 0.159398           | 0.0                 | 0.236772          | 0.214847         | 0.16                         |
| phase6_stratified_random_replay | stratified_random    | score_only        | 0.213387         | 0.064916            | 0.159398           | 0.838815            | 0.236772          | 0.214847         | 0.251701                     |
| phase6_diversity_weighted_replay| diversity_weighted   | score_only        | 0.21187          | 0.012851            | 0.139499           | 0.883171            | 0.240179          | 0.208335         | 0.105                        |
| phase6_residual_failure_replay  | residual_failure     | score_only        | 0.170999         | 0.033002            | 0.120818           | 0.0                 | 0.127541          | 0.323442         | 0.342222                     |
| phase6_diversity_failure_replay | diversity_failure    | score_only        | **0.086522**     | **0.003941**         | **0.056493**       | 0.75225             | 0.174718          | 0.310845         | 0.174603                     |
| phase6_diversity_failure_replay_compression| diversity_failure + compression| novelty_gate| 0.097906    | 0.0                 | 0.062304           | 0.74822             | 0.174718          | 0.334433         | 0.170068                     |

---

### Conservative Interpretation

- **Best Transfer and Optimality:**  
  The *phase6_diversity_failure_replay* condition achieves the lowest gaps on held-out TSPLIB (0.087) and synthetic holdout (0.004), as well as the best transfer gap (0.056). This indicates superior generalization and transfer performance.

- **Code Novelty vs Transfer:**  
  The conditions with highest code novelty (random replay variants) show worse transfer (TSPLIB gap ~0.21) than diversity_failure replay (transfer gap 0.056, novelty ~0.75). This supports the notion that lexical/code novelty does not necessarily correspond to algorithmic improvement in solving TSP instances and transfer.

- **Replay Archive Properties:**  
  - Diversity_failure replay archives maintain moderate descriptor diversity (~0.17) and hardness (~0.31), with some bias (~0.12) towards size.
  - Residual_failure replay shows lowest diversity (0.13) and highest failure concentration (~0.34), indicating more focused replay on difficult failures.
  - Diversity_weighted replay has the highest archive diversity (0.24) and low failure concentration (0.105).
  - Random replay variants have higher failure concentration (~0.25-0.31) and variable diversity (~0.17-0.24).

- **Failure Concentration and Replay Selection:**  
  The diversity_failure replay condition shows moderate failure concentration (final ~0.17) and maintains diversity in replay selection (mean diversity ~0.19-0.20), consistent with balanced focus on distinct difficult cases rather than over-concentration.

- **Effect of Compression and Selection Mode:**  
  - Compression (random replay compression, diversity_failure replay compression) reduces mean code novelty and slightly affects diversity and hardness but does not improve transfer compared to non-compressed diversity_failure replay.
  - Novelty_gate selection mode (versus score_only) generally lowers code novelty but does not yield better transfer gaps, suggesting novelty gating alone is not sufficient.

---

### Mechanism Insights per Replay Type

- **No replay (baseline):**  
  Good synthetic zero gap (by construction), moderate performance on held-out TSPLIB gaps. No failures replayed (failure concentration = 0), allowing for no experience reuse.

- **Random replay (raw failure samples):**  
  High code novelty (~0.88-0.90), highest final training gaps, and poor transfer gaps (~0.21). Replay failure concentration is moderate (~0.16-0.31) but replay diversity exists (mean selection diversity ~0.26). No transfer gains despite high code novelty.

- **Failure replay (all failures):**  
  Similar performance to random replay but slightly higher failure concentration (~0.26) and lower diversity (~0.18). Also no transfer improvement.

- **Stratified random replay:**  
  Similar to random replay with stratification; transfer and training performance similar, no evident benefit.

- **Diversity-weighted replay:**  
  Balances diversity with failure focus, achieves moderate transfer gap (~0.14) and improved synthetic gap (~0.013). Archive diversity high, failure concentration low, selection diversity high. Offers some algorithmic advantage over raw replay modes.

- **Residual failure replay:**  
  Focuses on residual failures, achieves mid-range transfer gap (0.12) and synthetic gap (0.033). Archive diversity and size bias lower; failure concentration high (~0.34). Indicates more targeted replay on residual failures may help but less than diversity_failure.

- **Diversity failure replay:**  
  Balances failure focus and diversity, leading to best transfer and held-out gaps, low synthetic gap, moderate failure concentration (~0.17), and reasonable archive diversity. This mechanism most effectively improves generalization.

- **Diversity failure replay with compression:**  
  Similar to above but with compression pressure, slightly worse transfer gaps (0.062), zero synthetic gap, and no novelty on code. Compression suppresses code novelty but transfer remains nearly as good, showing code novelty drop does not degrade transfer here.

---

### Summary

- **Top-performing replay mode:** *diversity_failure_replay*  
  - Achieves lowest TSPLIB and synthetic gaps (optimality-gap metric), indicating best transfer.  
  - Maintains balanced archive diversity and failure concentration conducive for learning.  
  - Code novelty is moderate (~0.75), suggesting algorithmic improvements rather than only lexical novelty.

- **Pure random or failure replay without diversity weighting:**  
  - High code novelty but worse transfer and overall gap performance, indicating novelty alone is insufficient.

- **Compression lowers code novelty but does not degrade transfer:**  
  - Observed in diversity failure replay compression and random replay compression conditions, confirming code novelty and transfer are not strictly coupled.

- **Replay archive characteristics critical:**  
  - Diversity in replay archive descriptors and balanced failure concentration correlate with better transfer, rather than larger archive sizes or maximum code novelty.

---

# Final Conclusion

The evidence supports **diversity-weighted failure replay** as the most effective replay mechanism in this TSP benchmark suite for transfer to held-out and synthetic problems, balancing replay diversity, failure focus, and training archive characteristics. High code novelty alone is not predictive of transfer gains. Compression reduces code novelty but can be used without major harm to transfer performance when combined with diversity failure replay.
