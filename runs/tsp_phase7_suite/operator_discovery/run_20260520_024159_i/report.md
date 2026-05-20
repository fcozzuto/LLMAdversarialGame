# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_compression_pressure`.
- Best held-out TSPLIB gap: `phase7_modular_operator_compression_pressure`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_024159_i
- started_at_local: 2026-05-20 02:41:59
- finished_at_local: 2026-05-20 03:15:15
- duration_hhmm: 00:33
- duration_seconds: 1996.724
- seed_offset: 8000
- replicate_label: i
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.893241 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.806663 | 0.4375 | False | 0.002824 | 0.016003 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.235058 | 0.054968 | 0.121317 | 0.880523 | 0.445 | False | 0.004089 | -0.00556 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235667 | 0.054968 | 0.121542 | 0.84406 | 0.4425 | False | 0.003334 | 0.235658 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.176029 | 0.04601 | 0.093911 | 0.0 | 0.445 | False | -0.038703 | 0.981692 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.236585 | 0.064041 | 0.12761 | 0.81 | 0.4425 | False | 0.002996 | 0.019176 |

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
- Accepted novelty `0.893241`, complexity `0.56`, and adaptation efficiency `-0.027882`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.806663`, complexity `0.4375`, and adaptation efficiency `0.007377`.
- Last-epoch runtime `71.45605` ms and distance evaluations `5179.0`.
- Validation: surviving `False`, transplant delta `0.002824`, positive scaffolds `0`, Pareto runtime inflation `0.016003`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.016003, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.880523`, complexity `0.445`, and adaptation efficiency `0.006758`.
- Last-epoch runtime `60.68015` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.004089`, positive scaffolds `0`, Pareto runtime inflation `-0.00556`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.00556, "same_gap_faster": true}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235667`, family holdout `0.054968`, combined `0.121542`.
- Accepted novelty `0.84406`, complexity `0.4425`, and adaptation efficiency `0.009631`.
- Last-epoch runtime `67.84825` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `0.003334`, positive scaffolds `1`, Pareto runtime inflation `0.235658`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.232518, "gap_delta": 0.000224, "runtime_inflation": 0.235658, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.176029`, family holdout `0.04601`, combined `0.093911`.
- Accepted novelty `0.0`, complexity `0.445`, and adaptation efficiency `0.0`.
- Last-epoch runtime `50.604475` ms and distance evaluations `4998.5`.
- Validation: surviving `False`, transplant delta `-0.038703`, positive scaffolds `4`, Pareto runtime inflation `0.981692`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 11.735255, "gap_delta": -0.02318, "runtime_inflation": 0.981692, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.236585`, family holdout `0.064041`, combined `0.12761`.
- Accepted novelty `0.81`, complexity `0.4425`, and adaptation efficiency `0.006923`.
- Last-epoch runtime `127.286725` ms and distance evaluations `7395.75`.
- Validation: surviving `False`, transplant delta `0.002996`, positive scaffolds `0`, Pareto runtime inflation `0.019176`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 0.003718, "gap_delta": 0.006293, "runtime_inflation": 0.019176, "same_gap_faster": false}

## Judge Appendix
```markdown
# Review Summary of TSP Modular-Operator Discovery Suite

## Key Evaluation Criteria Recap
- **Main Transfer Evidence:** Held-out TSPLIB gap and family holdout gap.
- **Operator Interest:** Only if validation survives transplant and ablation tests.
- **Claims:** Prefer reusable operator structure over full-solver performance.
- **Algorithm Discovery:** Only if operator survives scaffold and family holdout tests.

---

## Overall Outcome
- **No surviving candidates** under the stringent criteria.
- **No operator shows validated benefit** after ablation and transplant tests on held-out sets.

---

## Condition Highlights and Interpretation

| Condition Name                               | Operator Type        | Final Family Gap | Final TSPLIB Gap | Transfer Gap | Ablation Support | Transplant Findings                         | Surviving Candidate? |
|----------------------------------------------|---------------------|------------------|------------------|--------------|------------------|---------------------------------------------|---------------------|
| phase7_baseline_heuristic_only                | n/a                 | 0.05497          | 0.23506          | 0.12132      | n/a              | n/a                                         | No                  |
| phase7_full_solver_evolution                   | n/a                 | 0.06492          | 0.21339          | 0.15940      | n/a              | n/a                                         | No                  |
| phase7_modular_operator_evolution              | perturbation        | 0.05497          | 0.23506          | 0.12132      | Ablation negative (disabled no effect) | No improvement on scaffold transplantation; fails on clustered_local_search | No                  |
| phase7_modular_operator_random_replay          | perturbation        | 0.05497          | 0.23506          | 0.12132      | Ablation negative (disabled no effect) | No positive scaffold transplant; no family gain | No                  |
| phase7_modular_operator_diversity_residual_replay | candidate_pruner    | 0.05497          | 0.23567          | 0.12154      | Ablation negative (disabling no hurt)   | One positive scaffold transplant but no family gap improvement; high runtime inflation | No                  |
| phase7_modular_operator_compression_pressure   | scaffold_selector   | **0.04601 (best)** | **0.17603 (best)** | 0.09391      | Ablation shows disabling hurts (gap +0.0219), some variants better | Positive transplant mean gap delta (-0.0387); mixed family results with 2 positive and 2 severe regressions; runtime inflation high (~98%) | No |
| phase7_modular_operator_pareto_selection       | candidate_ranker    | 0.06404          | 0.23659          | 0.12761      | Ablation negative (disabled improves gap) | No positive scaffold transplant; no family gain | No                  |

---

## Conservative Interpretation

1. **Best Transfer Performance and Holistic Gap:**  
   The *phase7_modular_operator_compression_pressure* condition shows the best held-out TSPLIB gap (0.176 vs baseline 0.235) and the best family gap (0.046), indicating some transfer potential.

2. **Ablation and Operator Effect:**  
   - This compression pressure operator (a scaffold selector) is the only operator where disabling it increases gap substantially (+0.0219), suggesting it has some positive internal effect.  
   - Other operators (perturbations, candidate rankers/pruners) show no loss when disabled, indicating no validated beneficial operator effect.

3. **Transplant Test:**  
   - Compression pressure operator shows a **negative mean transplant gap delta (-0.0387),** meaning it improved performance on transplanted scaffolds in aggregate, with 4 positive scaffolds out of 5 tested.  
   - However, it does not transplant cleanly into some scaffolds (e.g., fails for `cheapest_insertion_2opt`), and shows regressions on some families (nearest_neighbor_trap_tsp, uniform_euclidean).

4. **Family Holdout Signal:**  
   - Compression pressure operator has 2 positive families (heldout_tsplib and two_cluster_bottleneck_tsp) with improved gaps, but also 2 with severe regressions.  
   - Other operators show no meaningful family improvement.

5. **Runtime and Complexity:**  
   - Compression pressure operator incurs high runtime inflation (~98%), which diminishes practical value despite gap improvement.  
   - Other operators have much lower runtime impact but lack validated improvements.

6. **Operator Survival:**  
   - No operator fulfills all criteria: survival under scaffold and family holdout tests AND positive ablation AND positive transplant validation.  
   - Thus, **no modular operator qualifies as a surviving reusable discovery or validated new algorithmic operator.**

---

## Specific Notes on Operator Types

- **Perturbation Operators (double-bridge escalation):**  
  Fail ablation (disabling has zero gap impact), no family transfer gain, do not transplant well—suggesting no validated reusable effect despite novelty.

- **Candidate Pruner / Ranker Operators:**  
  No validated improvement; ablations often show better gaps when operator is disabled, no positive family or transplant validation.

- **Scaffold Selector (compression pressure):**  
  Unique among tested operators: shows a reproducible positive transfer pattern, ablation shows dependency, and transplant improvements, but also runtime cost and inconsistent family effects prevent full validation.

---

## Final Conclusion

- **No modular operator discovered in this suite meets the rigorous criteria for validated reusable operator structure.**  
- **Best candidate is a deterministic scaffold selector** that improves held-out TSPLIB performance and transplant mean gap but suffers from high runtime cost and some family regressions.  
- **No algorithm discovery claim is warranted.**  
- **No modular operator survives ablation and transplant validations simultaneously with positive holdout gains.**  

---

# Summary Table

| Criterion                 | Result                                                  |
|---------------------------|---------------------------------------------------------|
| Best held-out TSPLIB gap  | 0.17603 (compression pressure operator)                 |
| Best family holdout gap   | 0.04601 (compression pressure operator)                 |
| Survival of ablation test | Only compression pressure operator shows gap worsening when disabled; others no effect or better without operator |
| Survival of transplant    | Compression pressure operator shows transplant gap improvements on most scaffolds; others do not |
| Family holdout validation | Mixed for compression pressure (2 positive, 2 regression); none positive for others |
| Runtime inflation         | Very high (~98%) for compression pressure, low for others |
| Surviving candidates      | None                                                    |
| Algorithm discovery       | Not supported                                           |

---

# Recommendations

- Further reduce runtime overhead for promising scaffold selector to improve practical viability.  
- Explore operator variants that preserve or improve ablation signal and broaden family positive signal.  
- Do not claim discovery of new reusable operators nor new full solvers based on current results.  
- Maintain focus on held-out gap, ablation validation, and transplant robustness for future candidates.

---

**End of conservative analysis.**
