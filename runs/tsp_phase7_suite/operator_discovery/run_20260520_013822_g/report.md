# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_baseline_heuristic_only`.
- Best held-out TSPLIB gap: `phase7_full_solver_evolution`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_013822_g
- started_at_local: 2026-05-20 01:38:22
- finished_at_local: 2026-05-20 02:10:40
- duration_hhmm: 00:32
- duration_seconds: 1938.115
- seed_offset: 6000
- replicate_label: g
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.880405 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.752867 | 0.4475 | False | 0.002607 | 0.005797 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235667 | 0.054968 | 0.121542 | 0.903553 | 0.445 | False | 0.00807 | 0.562244 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235667 | 0.054968 | 0.121542 | 0.844238 | 0.4475 | False | 0.002904 | 0.179435 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.44 | False | 0.002151 | 0.033207 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.238386 | 0.064041 | 0.128273 | 0.722793 | 0.4425 | False | 0.003018 | 0.015857 |

## Condition Notes
### phase7_baseline_heuristic_only
- Execution mode `baseline_only` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.0`, and adaptation efficiency `0.0`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_full_solver_evolution
- Execution mode `full_solver` on host scaffold `whole_solver`.
- Final gaps: TSPLIB `0.213387`, family holdout `0.064916`, combined `0.159398`.
- Accepted novelty `0.880405`, complexity `0.56`, and adaptation efficiency `-0.028288`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.752867`, complexity `0.4475`, and adaptation efficiency `0.007298`.
- Last-epoch runtime `67.9039` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.002607`, positive scaffolds `0`, Pareto runtime inflation `0.005797`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.005797, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.903553`, complexity `0.445`, and adaptation efficiency `-0.005611`.
- Last-epoch runtime `49.282625` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.00807`, positive scaffolds `1`, Pareto runtime inflation `0.562244`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.404735, "gap_delta": 0.000224, "runtime_inflation": 0.562244, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.844238`, complexity `0.4475`, and adaptation efficiency `0.009629`.
- Last-epoch runtime `202.169275` ms and distance evaluations `6995.75`.
- Validation: surviving `False`, transplant delta `0.002904`, positive scaffolds `1`, Pareto runtime inflation `0.179435`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.156445, "gap_delta": 0.000224, "runtime_inflation": 0.179435, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.0`, complexity `0.44`, and adaptation efficiency `0.0`.
- Last-epoch runtime `72.158575` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.002151`, positive scaffolds `0`, Pareto runtime inflation `0.033207`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.033207, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.238386`, family holdout `0.064041`, combined `0.128273`.
- Accepted novelty `0.722793`, complexity `0.4425`, and adaptation efficiency `0.006842`.
- Last-epoch runtime `134.850475` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003018`, positive scaffolds `0`, Pareto runtime inflation `0.015857`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006956, "runtime_inflation": 0.015857, "same_gap_faster": false}

## Judge Appendix
```markdown
# Summary of TSP Modular-Operator Discovery Results

## Key Criteria Recap
- **Main transfer evidence:** held-out TSPLIB gap and family holdout gap.
- **Modular operator interest:** requires validation surviving transplant and ablation tests.
- **Claims:** focus on reusable operator structure over full-solver performance.
- **Algorithm discovery:** requires operator survival in scaffold and family tests.

---

## Overview of Conditions

| Condition Name                            | Execution Mode      | Operator Type    | Final Family Gap | Final TSPLIB Gap | Transfer Gap | Surviving Candidate | Transplant Mean Gap Delta | Ablation Result | Comments                            |
|-----------------------------------------|--------------------|------------------|------------------|------------------|--------------|---------------------|---------------------------|-----------------|-----------------------------------|
| phase7_baseline_heuristic_only          | baseline_only      | n/a              | 0.054968         | 0.235058         | 0.121317     | No                  | 0.0                       | N/A             | Baseline reference                |
| phase7_full_solver_evolution             | full_solver        | n/a              | 0.064916         | 0.213387         | 0.159398     | No                  | 0.0                       | N/A             | Full solver evolution, no operator |
| phase7_modular_operator_evolution        | modular_operator   | perturbation     | 0.054968         | 0.235058         | 0.121317     | No                  | 0.002607                  | No effect       | No improvement; ablation disables operator effect |
| phase7_modular_operator_random_replay    | modular_operator   | candidate_pruner | 0.054968         | 0.235667         | 0.121542     | No                  | 0.00807                   | No effect       | Runtime inflation high; no positive family gain |
| phase7_modular_operator_diversity_residual_replay | modular_operator | candidate_pruner | 0.054968         | 0.235667         | 0.121542     | No                  | 0.002904                  | No effect       | Similar to above; no validation gain |
| phase7_modular_operator_compression_pressure | modular_operator | perturbation     | 0.054968         | 0.235058         | 0.121317     | No                  | 0.002151                  | No effect       | Operator disables w/o loss; no transplant success |
| phase7_modular_operator_pareto_selection | modular_operator   | candidate_ranker | 0.064041         | 0.238386         | 0.128273     | No                  | 0.003018                  | No effect       | Underperforms on grid_like_tsp; no transplant success |

---

## Detailed Interpretation

### 1. Held-Out and Transfer Performance
- **Held-out TSPLIB gaps** remain large (~0.21-0.24) across conditions.
- **Family gaps** mostly unchanged (~0.05-0.06), consistent with the baseline.
- **Transfer gaps** show no meaningful improvement compared to baseline; some operators have marginally negative or zero impact.
- None of the operators demonstrate consistent or statistically significant improvements on held-out TSPLIB or family holdouts.

### 2. Transplantation Checks
- Mean transplant gap deltas are small and often positive (indicating slight worsening).
- No operator shows a positive transplant scaffold count above zero except candidate pruners in random and residual replay modes (positive scaffold count=1), but gap deltas remain negligible or slightly negative.
- Perturbation operators fail to transplant cleanly into other scaffolds (notably `clustered_local_search`).
- Candidate ranker does not transplant cleanly anywhere.

### 3. Ablation Results
- In all modular operators tested, disabling the operator has **zero or negative gap delta**:
  - Disabling does not degrade performance, indicating no clear positive operator effect.
- Variants (simplified, alternate, shuffled) do not improve or meaningfully change gaps.
- This undermines claims about real operator effects or reusable structures.

### 4. Pareto Tradeoffs
- Pareto gap deltas for candidate ranker are positive (worse gaps), and runtime is slightly inflated.
- Runtime inflation for candidate pruners is substantial (up to 56%), with no gap improvement.
- Perturbation operators show negligible runtime inflation (~0-3%) but no gap gains.
- No operator achieves strictly better gap for equal or less runtime.

### 5. Operator Survival and Reusability
- No condition produces a **surviving candidate operator** per conditions.
- No operator survives all validation phases including ablation, transplant, and family holdout.
- Operators fail transplant tests into multiple scaffolds, limiting reusability.
- Lack of positive family gap improvement undermines reuse claims.

### 6. Special Notes on Operator Core Ideas
- Perturbations aim at deterministic stagnation escape via double-bridge style moves but fail to improve gaps or survive ablations.
- Candidate pruners adapt neighborhood sizes using instance features but incur runtime inflation without quality gain.
- Candidate ranker prioritizes bottleneck edges but shows performance regressions and fails transplant.

---

## Conclusion

- **No modular operator candidate currently demonstrates convincing transfer or transplant validation.**
- Ablation analysis universally shows disabling operators does not harm performance, thus no confirmed positive modular effect.
- Held-out TSPLIB and family gaps remain at baseline levels without meaningful improvements.
- Runtime tradeoffs are either neutral or negative (inflation without quality gain).
- Operators do not reliably transplant to other scaffolds, limiting claims on reusable operator structures.
- **No algorithm discovery or reusable operator claims are warranted given the lack of survival through ablation, transplant, and family validation.**

---

## Recommendation

- Continue exploration with stronger family holdout and transplant validations.
- Focus on operators showing positive ablation effects and consistent family improvements before claiming reusability or discovery.
- Avoid claiming modular operator effectiveness or solver improvement absent clear validation.
```
