# Replay-Aware TSP Benchmark Report

## Overview
- Condition count: 9.
- Best final transfer gap: `phase6_residual_failure_replay`.
- Best TSPLIB holdout gap: `phase6_residual_failure_replay`.
- Best synthetic holdout gap: `phase6_random_replay`.

## Run Metadata
- run_name: run_20260519_001148_f
- started_at_local: 2026-05-19 00:11:48
- finished_at_local: 2026-05-19 00:31:50
- duration_hhmm: 00:20
- duration_seconds: 1202.299
- seed_offset: 5000
- replicate_label: f
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Replay | Selection | Compression | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Archive Diversity | Archive Hardness | Failure Concentration | Mean Accepted Novelty | Mean Complexity | Adaptation Efficiency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase6_no_replay | none | score_only | False | 0.232246 | 0.020958 | 0.155414 | 0.236772 | 0.170476 | 0.0 | 0.805346 | 0.76 | -0.022765 |
| phase6_random_replay | random | score_only | False | 0.122006 | 0.0 | 0.07764 | 0.236772 | 0.145007 | 0.19457 | 0.685363 | 0.76 | 0.054841 |
| phase6_failure_replay | failure | score_only | False | 0.213387 | 0.064916 | 0.159398 | 0.171206 | 0.348017 | 0.261637 | 0.79099 | 0.56 | -0.031486 |
| phase6_random_replay_compression | random | novelty_gate | True | 0.098726 | 0.0 | 0.062826 | 0.236772 | 0.113866 | 0.19457 | 0.817438 | 0.76 | 0.011577 |
| phase6_stratified_random_replay | stratified_random | score_only | False | 0.121156 | 0.010343 | 0.08086 | 0.236772 | 0.149538 | 0.221162 | 0.0 | 0.76 | 0.0 |
| phase6_diversity_weighted_replay | diversity_weighted | score_only | False | 0.13595 | 0.0 | 0.086514 | 0.236772 | 0.155695 | 0.130039 | 0.827986 | 0.76 | 0.023865 |
| phase6_residual_failure_replay | residual_failure | score_only | False | 0.082341 | 0.0 | 0.052399 | 0.129767 | 0.296745 | 0.276871 | 0.832596 | 0.76 | 0.039093 |
| phase6_diversity_failure_replay | diversity_failure | score_only | False | 0.096401 | 0.0 | 0.061346 | 0.171206 | 0.291624 | 0.17024 | 0.828815 | 0.76 | 0.032532 |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate | True | 0.234344 | 0.022049 | 0.157146 | 0.171206 | 0.261064 | 0.17767 | 0.0 | 0.76 | 0.0 |

## Condition Notes
### phase6_no_replay
- Replay mode: `none` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.232246`, synthetic `0.020958`, combined `0.155414`.
- Accepted-epoch count `2`, mean accepted code novelty `0.805346`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.170476`, size bias `8.3e-05`, and failure concentration `0.0`.
- Replay selection diversity `0.0`, mean selected expected gap `0.0`, mean selected residual gap `0.0`.
- Adaptation efficiency `-0.022765` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.232246` across 7 instances; family means: ch=0.241182, kroD=0.218371, pcb=0.275671, pr=0.322044, rd=0.268015, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.020958` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.083832, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3388, "expected_gap": 0.406514, "family": "a", "name": "a280", "optimality_gap": 0.313687, "residual_gap": -0.092827}, {"best_known_cost": 7542, "cost": 9109, "expected_gap": 0.245107, "family": "berlin", "name": "berlin52", "optimality_gap": 0.20777, "residual_gap": -0.037337}, {"best_known_cost": 14379, "cost": 17073, "expected_gap": 0.328729, "family": "lin", "name": "lin105", "optimality_gap": 0.187357, "residual_gap": -0.141372}]

### phase6_random_replay
- Replay mode: `random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.122006`, synthetic `0.0`, combined `0.07764`.
- Accepted-epoch count `2`, mean accepted code novelty `0.685363`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.145007`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.13412`, mean selected residual gap `-0.025781`.
- Adaptation efficiency `0.054841` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 2, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.122006` across 7 instances; family means: ch=0.129981, kroD=0.037757, pcb=0.201997, pr=0.15872, rd=0.170417, st=0.025185.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3529, "expected_gap": 0.406204, "family": "a", "name": "a280", "optimality_gap": 0.36836, "residual_gap": -0.037844}, {"best_known_cost": 629, "cost": 774, "expected_gap": 0.25628, "family": "eil", "name": "eil101", "optimality_gap": 0.230525, "residual_gap": -0.025755}, {"best_known_cost": 14379, "cost": 17377, "expected_gap": 0.328131, "family": "lin", "name": "lin105", "optimality_gap": 0.208499, "residual_gap": -0.119632}]

### phase6_failure_replay
- Replay mode: `failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.213387`, synthetic `0.064916`, combined `0.159398`.
- Accepted-epoch count `3`, mean accepted code novelty `0.79099`, and final complexity `0.56`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.348017`, size bias `0.120322`, and failure concentration `0.261637`.
- Replay selection diversity `0.177669`, mean selected expected gap `0.310218`, mean selected residual gap `0.065539`.
- Adaptation efficiency `-0.031486` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.213387` across 7 instances; family means: ch=0.1282, kroD=0.262046, pcb=0.264938, pr=0.350299, rd=0.22225, st=0.137778.
- Panel `synthetic_holdout` mean gap `0.064916` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.259662, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3614, "expected_gap": 0.408608, "family": "a", "name": "a280", "optimality_gap": 0.401318, "residual_gap": -0.00729}, {"best_known_cost": 629, "cost": 875, "expected_gap": 0.25469, "family": "eil", "name": "eil101", "optimality_gap": 0.391097, "residual_gap": 0.136407}, {"best_known_cost": 14379, "cost": 19107, "expected_gap": 0.329634, "family": "lin", "name": "lin105", "optimality_gap": 0.328813, "residual_gap": -0.000821}]

### phase6_random_replay_compression
- Replay mode: `random` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.098726`, synthetic `0.0`, combined `0.062826`.
- Accepted-epoch count `3`, mean accepted code novelty `0.817438`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.113866`, size bias `8.3e-05`, and failure concentration `0.19457`.
- Replay selection diversity `0.262174`, mean selected expected gap `0.132632`, mean selected residual gap `-0.059201`.
- Adaptation efficiency `0.011577` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 1, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.098726` across 7 instances; family means: ch=0.122658, kroD=0.069597, pcb=0.196069, pr=0.085273, rd=0.074083, st=0.020741.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 7542, "cost": 10132, "expected_gap": 0.240918, "family": "berlin", "name": "berlin52", "optimality_gap": 0.34341, "residual_gap": 0.102492}, {"best_known_cost": 2579, "cost": 3407, "expected_gap": 0.409771, "family": "a", "name": "a280", "optimality_gap": 0.321055, "residual_gap": -0.088716}, {"best_known_cost": 14379, "cost": 17920, "expected_gap": 0.322762, "family": "lin", "name": "lin105", "optimality_gap": 0.246262, "residual_gap": -0.0765}]

### phase6_stratified_random_replay
- Replay mode: `stratified_random` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.121156`, synthetic `0.010343`, combined `0.08086`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.149538`, size bias `8.3e-05`, and failure concentration `0.221162`.
- Replay selection diversity `0.187367`, mean selected expected gap `0.236305`, mean selected residual gap `-0.048527`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.121156` across 7 instances; family means: ch=0.105887, kroD=0.111017, pcb=0.236067, pr=0.092327, rd=0.105057, st=0.091852.
- Panel `synthetic_holdout` mean gap `0.010343` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.041372, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3452, "expected_gap": 0.404343, "family": "a", "name": "a280", "optimality_gap": 0.338503, "residual_gap": -0.06584}, {"best_known_cost": 14379, "cost": 18103, "expected_gap": 0.322164, "family": "lin", "name": "lin105", "optimality_gap": 0.258989, "residual_gap": -0.063175}, {"best_known_cost": 7542, "cost": 9348, "expected_gap": 0.236622, "family": "berlin", "name": "berlin52", "optimality_gap": 0.239459, "residual_gap": 0.002837}]

### phase6_diversity_weighted_replay
- Replay mode: `diversity_weighted` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.13595`, synthetic `0.0`, combined `0.086514`.
- Accepted-epoch count `2`, mean accepted code novelty `0.827986`, and final complexity `0.76`.
- Active replay archive `experience_archive` with mean diversity `0.236772`, mean hardness `0.155695`, size bias `8.3e-05`, and failure concentration `0.130039`.
- Replay selection diversity `0.261003`, mean selected expected gap `0.167655`, mean selected residual gap `-0.021397`.
- Adaptation efficiency `0.023865` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `2`.
- Panel `heldout_tsplib` mean gap `0.13595` across 7 instances; family means: ch=0.109508, kroD=0.201277, pcb=0.226771, pr=0.095766, rd=0.149558, st=0.059259.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3698, "expected_gap": 0.40318, "family": "a", "name": "a280", "optimality_gap": 0.433889, "residual_gap": 0.030709}, {"best_known_cost": 629, "cost": 733, "expected_gap": 0.254054, "family": "eil", "name": "eil101", "optimality_gap": 0.165342, "residual_gap": -0.088712}, {"best_known_cost": 14379, "cost": 15330, "expected_gap": 0.329244, "family": "lin", "name": "lin105", "optimality_gap": 0.066138, "residual_gap": -0.263106}]

### phase6_residual_failure_replay
- Replay mode: `residual_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.082341`, synthetic `0.0`, combined `0.052399`.
- Accepted-epoch count `3`, mean accepted code novelty `0.832596`, and final complexity `0.76`.
- Active replay archive `residual_archive` with mean diversity `0.129767`, mean hardness `0.296745`, size bias `0.069117`, and failure concentration `0.276871`.
- Replay selection diversity `0.148354`, mean selected expected gap `0.277755`, mean selected residual gap `0.061728`.
- Adaptation efficiency `0.039093` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `3`.
- Panel `heldout_tsplib` mean gap `0.082341` across 7 instances; family means: ch=0.062421, kroD=0.076453, pcb=0.217909, pr=0.038767, rd=0.042857, st=0.075556.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 2579, "cost": 3304, "expected_gap": 0.402947, "family": "a", "name": "a280", "optimality_gap": 0.281117, "residual_gap": -0.12183}, {"best_known_cost": 629, "cost": 726, "expected_gap": 0.262003, "family": "eil", "name": "eil101", "optimality_gap": 0.154213, "residual_gap": -0.10779}, {"best_known_cost": 7542, "cost": 7964, "expected_gap": 0.237364, "family": "berlin", "name": "berlin52", "optimality_gap": 0.055953, "residual_gap": -0.181411}]

### phase6_diversity_failure_replay
- Replay mode: `diversity_failure` with selection mode `score_only`.
- Final transfer gaps: TSPLIB `0.096401`, synthetic `0.0`, combined `0.061346`.
- Accepted-epoch count `5`, mean accepted code novelty `0.828815`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.291624`, size bias `0.120322`, and failure concentration `0.17024`.
- Replay selection diversity `0.199284`, mean selected expected gap `0.300697`, mean selected residual gap `-0.009641`.
- Adaptation efficiency `0.032532` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 4, 'adversarial_layouts': 4}` / elite `5`.
- Panel `heldout_tsplib` mean gap `0.096401` across 7 instances; family means: ch=0.06478, kroD=0.060862, pcb=0.218796, pr=0.120452, rd=0.087358, st=0.057778.
- Panel `synthetic_holdout` mean gap `0.0` across 4 instances; family means: clustered_gaussian=0.0, grid_outliers=0.0, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 14379, "cost": 19073, "expected_gap": 0.328006, "family": "lin", "name": "lin105", "optimality_gap": 0.326448, "residual_gap": -0.001558}, {"best_known_cost": 2579, "cost": 3212, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.245444, "residual_gap": -0.156727}, {"best_known_cost": 629, "cost": 714, "expected_gap": 0.267091, "family": "eil", "name": "eil101", "optimality_gap": 0.135135, "residual_gap": -0.131956}]

### phase6_diversity_failure_replay_compression
- Replay mode: `diversity_failure` with selection mode `novelty_gate`.
- Final transfer gaps: TSPLIB `0.234344`, synthetic `0.022049`, combined `0.157146`.
- Accepted-epoch count `1`, mean accepted code novelty `0.0`, and final complexity `0.76`.
- Active replay archive `worst_archive` with mean diversity `0.171206`, mean hardness `0.261064`, size bias `0.120322`, and failure concentration `0.17767`.
- Replay selection diversity `0.201519`, mean selected expected gap `0.315683`, mean selected residual gap `-0.035024`.
- Adaptation efficiency `0.0` and archive sizes `{'experience_cases': 10, 'worst_cases': 6, 'failure_cases': 6, 'residual_failures': 3, 'adversarial_layouts': 4}` / elite `1`.
- Panel `heldout_tsplib` mean gap `0.234344` across 7 instances; family means: ch=0.194363, kroD=0.272518, pcb=0.236086, pr=0.336884, rd=0.26397, st=0.142222.
- Panel `synthetic_holdout` mean gap `0.022049` across 4 instances; family means: clustered_gaussian=0.010624, grid_outliers=0.077572, ring_bridge=0.0, two_corridors=0.0.
- Worst recent training cases: [{"best_known_cost": 629, "cost": 819, "expected_gap": 0.263911, "family": "eil", "name": "eil101", "optimality_gap": 0.302067, "residual_gap": 0.038156}, {"best_known_cost": 2579, "cost": 3262, "expected_gap": 0.402171, "family": "a", "name": "a280", "optimality_gap": 0.264831, "residual_gap": -0.13734}, {"best_known_cost": 14379, "cost": 15975, "expected_gap": 0.326657, "family": "lin", "name": "lin105", "optimality_gap": 0.110995, "residual_gap": -0.215662}]

## Judge Appendix
### Summary of Main Evidence (Held-out TSPLIB Gap & Synthetic Holdout Gap)

| Condition                            | Replay Mode               | Selection Mode | Archive Size | Final TSPLIB Gap | Final Synthetic Gap | Final Transfer Gap | Adaptation Efficiency | Code Novelty (Mean) | Complexity | Failure Concentration (Mean) | Replay Failure Concentration (Final) |
|------------------------------------|--------------------------|----------------|--------------|------------------|---------------------|--------------------|-----------------------|---------------------|------------|------------------------------|-------------------------------------|
| phase6_no_replay                   | none                     | score_only     | 29           | 0.232246         | 0.020958            | 0.155414           | -0.022765             | 0.805346            | 0.76       | 0.0                          | 0.0                                 |
| phase6_random_replay               | random                   | score_only     | 28           | 0.122006         | 0.0                 | 0.07764            | 0.054841              | 0.685363            | 0.76       | 0.19457                      | 0.16                                |
| phase6_failure_replay              | failure                  | score_only     | 30           | 0.213387         | 0.064916            | 0.159398           | -0.031486             | 0.79099             | 0.56       | 0.261637                     | 0.306122                            |
| phase6_random_replay_compression   | random                   | novelty_gate   | 27           | 0.098726         | 0.0                 | 0.062826           | 0.011577              | 0.817438            | 0.76       | 0.262174                     | 0.16                                |
| phase6_stratified_random_replay    | stratified_random        | score_only     | 29           | 0.121156         | 0.010343            | 0.08086            | 0.0                   | 0.0                 | 0.76       | 0.0                          | 0.251701                            |
| phase6_diversity_weighted_replay   | diversity_weighted       | score_only     | 30           | 0.13595          | 0.0                 | 0.086514           | 0.023865              | 0.827986            | 0.76       | 0.261003                     | 0.130039                            |
| phase6_residual_failure_replay     | residual_failure         | score_only     | 29           | 0.082341         | 0.0                 | 0.052399           | 0.039093              | 0.832596            | 0.76       | 0.148354                     | 0.33564                             |
| phase6_diversity_failure_replay    | diversity_failure        | score_only     | 30           | 0.096401         | 0.0                 | 0.061346           | 0.032532              | 0.828815            | 0.76       | 0.199284                     | 0.17024                             |
| phase6_diversity_failure_replay_compression | diversity_failure | novelty_gate   | 29           | 0.234344         | 0.022049            | 0.157146           | 0.0                   | 0.0                 | 0.76       | 0.201519                     | 0.188209                            |

- **Best synthetic (lowest synthetic gap):** phase6_random_replay and its compression variant (0.0 synthetic gap).
- **Best held-out TSPLIB gap:** phase6_residual_failure_replay (0.082341), followed by phase6_random_replay_compression (0.098726).
- **Best transfer gap:** phase6_residual_failure_replay (0.052399), followed by phase6_random_replay_compression (0.062826).
- **Best overall transfer performance:** phase6_residual_failure_replay.
- **phase6_no_replay** has worst transfer and heldout TSPLIB gap, despite high code novelty.

---

### Transfer Analysis and Replay Mechanism Insights

- **phase6_residual_failure_replay** (best transfer):
  - Replay Mode: residual_failure
  - Low heldout TSPLIB gap (0.0823) and best transfer gap (0.0524).
  - Archive hardness and failure concentration fairly high (~0.3), indicating focused replay on hard residual failures.
  - Moderate archive descriptor diversity (0.15).
  - Code novelty remains high (~0.83 mean).
  - Indicates that replay focused on residual failures yields best transfer to held-out TSPLIB.

- **phase6_random_replay** (best synthetic):
  - Replay Mode: random
  - Zero synthetic gap, good heldout TSPLIB gap (0.122) and transfer gap (0.078).
  - Replay failure concentration moderate (~0.19 final).
  - Archive diversity high (~0.24), size bias zero.
  - Moderate code novelty (~0.69 mean).
  - Shows broad coverage random replay supports synthetic performance but less so on real TSPLIB.

- **phase6_failure_replay:**
  - Replay Mode: failure
  - Higher heldout TSPLIB gap (0.213) and transfer gap (0.159), worse than random replay.
  - Highest failure concentration (~0.26-0.31), low behavior profile complexity (0.56).
  - Somewhat elevated archive hardness (~0.35) and size bias (0.12).
  - Zero compression pressure but lower code novelty (~0.79), no transfer improvement.
  - Replay on all failures without residual focus less effective.

- **Compression-aware replays** (random_replay_compression and diversity_failure_replay_compression):
  - Showed reduced final TSPLIB gap and transfer gap compared to their non-compression counterparts.
  - However, compression correlated with drops in code novelty (0.0 in some cases) without consistent large transfer gains.
  - Indicating memory pressure may reduce lexical novel exploration but not necessarily harm transfer.

- **phase6_diversity_weighted_replay** and **phase6_diversity_failure_replay**:
  - Intermediate transfer gaps (0.061-0.086).
  - Replay failure concentration moderate (0.13-0.26).
  - Maintain high code novelty (0.82+).
  - Behaviors cluster around "clustered_constructor" or "balanced".
  - Indicates diversity-weighted replay effective at balancing coverage and failure focus.

- **phase6_no_replay**:
  - Worst TSPLIB gap (0.232), highest transfer gap (0.155).
  - No replay results in minimal replay failure concentration (0.0).
  - Highest code novelty by a margin (0.805).
  - Suggests code novelty alone without replay does not improve transfer.

---

### Mechanism Studies Summary

- **Archive Diversity:**
  - Broad coverage replay (random, stratified_random, diversity_weighted) maintain high archive diversity (~0.24).
  - Failure and residual failure replays have lower diversity (0.13-0.17).
  - Diversity-weighted replay balances high diversity plus targeted failure replay.

- **Archive Hardness:**
  - Failure and residual failure playback achieve highest hardness (~0.3-0.35).
  - Random replay and no replay conditions have lower hardness (~0.15-0.18).
  - Hardness indicates replay targets more challenging failure instances.

- **Archive Size Bias:**
  - Failure-related archive keys (worst_archive) show size bias (~0.12), indicating replay preferences for larger instances.
  - Experience archive-based replays have zero size bias.

- **Failure Concentration:**
  - Failure and residual failure replay conditions concentrate replay on failure modes (0.17-0.33 final).
  - Random replay less so (~0.16-0.22).
  - No replay zero by definition.

- **Failure Residuals (mean_selected_residual_gap):**
  - Residual failure replay achieves negative mean residual gaps consistently (-0.13 to -0.27), suggesting targeted reduction of systematic failures.
  - Other replays show mixed or near-zero residual gaps.

---

### Code Novelty vs Transfer Tradeoff

- Highest code novelty in no replay (0.805) but worst transfer and TSPLIB gaps.
- Residual_failure_replay achieves best transfer but slightly reduced code novelty (~0.83) - still high.
- Random replay variants show slight decrease code novelty in exchange for improved transfer.
- Compression pressure reduces code novelty to zero in novelty_gate selection modes but may improve heldout TSPLIB and synthetic gaps modestly.
- Overall, code novelty and transfer are related but not strictly correlated; replay focused on hard residuals trades some novelty for better transfer.

---

### Summary of Replay Condition Categories

- **Broad-coverage replay:** random, stratified_random, diversity_weighted
  - High archive descriptor diversity (~0.24)
  - Moderate hardness (~0.15-0.19)
  - Moderate failure concentration (~0.13-0.26)
  - Good synthetic holdout performance (0 or near-zero gaps)
  - Moderate transfer performance (TSPLIB gaps approx 0.1-0.14)

- **Raw-failure replay:** failure replay
  - High hardness (~0.35)
  - High final failure concentration (~0.31)
  - Largest archive size bias (~0.12)
  - Higher TSPLIB gaps (about 0.21) and higher transfer gaps (about 0.16)
  - Lower code novelty (~0.79)

- **Residual-failure replay:** residual_failure replay
  - High hardness (~0.34)
  - Moderate diversity (~0.15)
  - Moderate failure concentration (~0.17)
  - Best TSPLIB and transfer gaps (0.082 and 0.052)
  - High code novelty (~0.83)

- **Diversity-weighted failure replay:** diversity_failure replay
  - Archive hardness about 0.29-0.32
  - Archive diversity moderate (0.17)
  - Failure concentration ~0.17-0.20
  - TSPLIB gaps around 0.09-0.1
  - Transfer gaps around 0.06
  - High code novelty (~0.83)

- **Compression-aware replay:** random_replay_compression and diversity_failure_replay_compression
  - Compression reduces code novelty to 0.0 in novelty_gate selection mode
  - Slight improvements in TSPLIB gaps and transfer gaps compared to non-compression variants
  - Archive diversity remains high

---

### Conservative Interpretation

1. **Best Transfer:** 
   - phase6_residual_failure_replay achieves the best TSPLIB and transfer gaps, showing that replay focused on residual failures improves transfer generalization.
   - High archive hardness and moderate diversity supports efficient replay of challenging failures.

2. **Synthetic Holdout:**
   - phase6_random_replay reaches zero mean synthetic holdout gap, suggesting broad coverage replay is sufficient for synthetic test cases.
   - This comes with moderate transfer and TSPLIB improvements but less than residual_failure replay.

3. **No Replay:**
   - Highest code novelty but worst gaps and no replay failures or failure concentration.
   - Code novelty alone does not translate into transfer gain.

4. **Failure Replay (raw failures):**
   - High failure concentration and hardness but transfer gaps remain high.
   - Suggests replaying raw failures without residual focus may not efficiently drive transfer.

5. **Compression Effects:**
   - Compression reduces code novelty sharply in novelty_gate selections but can modestly improve transfer metrics.
   - Shows a tradeoff between code novelty and replay efficiency under memory pressure.

6. **Diversity-weighted and diversity failure replay:**
   - Offer a balanced compromise, good code novelty and transfer performance with moderate failure concentration.

---

### Recommendations

- Prioritize **residual failure replay** mechanisms for improved transfer performance on TSPLIB benchmarks.
- Incorporate **broad coverage replay** (random or diversity-weighted) to maintain zero synthetic holdout gaps.
- Use compression carefully; while it may improve transfer, it reduces code novelty substantially.
- Avoid relying solely on code novelty without replay, as it does not yield transfer benefits.
- Consider failure concentration and archive hardness as key replay archive properties influencing transfer.
- Distinguish replay modes carefully as they have systematic effects on archive properties and generalization.

---

*This conservative analysis focuses on quantitative gaps and replay archive metrics to inform transfer improvements in replay-aware TSP benchmarks.*
