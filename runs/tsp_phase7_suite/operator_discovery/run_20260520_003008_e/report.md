# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_random_replay`.
- Best held-out TSPLIB gap: `phase7_modular_operator_random_replay`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_003008_e
- started_at_local: 2026-05-20 00:30:08
- finished_at_local: 2026-05-20 01:02:42
- duration_hhmm: 00:33
- duration_seconds: 1954.167
- seed_offset: 4000
- replicate_label: e
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.86775 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.888331 | 0.44 | False | 0.010203 | 0.770705 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.200044 | 0.053637 | 0.107576 | 0.0 | 0.4425 | False | -0.012613 | 1.366747 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.054968 | 0.121317 | 0.844828 | 0.4425 | False | 0.00152 | -0.00642 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.054968 | 0.121317 | 0.903885 | 0.4425 | False | 0.002619 | 0.016329 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.235058 | 0.054968 | 0.121317 | 0.886294 | 0.445 | False | 0.003188 | -0.044844 |

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
- Accepted novelty `0.86775`, complexity `0.56`, and adaptation efficiency `-0.028701`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.888331`, complexity `0.44`, and adaptation efficiency `0.006515`.
- Last-epoch runtime `78.9645` ms and distance evaluations `4223.5`.
- Validation: surviving `False`, transplant delta `0.010203`, positive scaffolds `1`, Pareto runtime inflation `0.770705`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.84967, "gap_delta": -0.002615, "runtime_inflation": 0.770705, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.200044`, family holdout `0.053637`, combined `0.107576`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `54.432625` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.012613`, positive scaffolds `4`, Pareto runtime inflation `1.366747`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 26.433505, "gap_delta": -0.013741, "runtime_inflation": 1.366747, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.844828`, complexity `0.4425`, and adaptation efficiency `0.014087`.
- Last-epoch runtime `168.1671` ms and distance evaluations `7395.75`.
- Validation: surviving `False`, transplant delta `0.00152`, positive scaffolds `0`, Pareto runtime inflation `-0.00642`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 11, "complexity_score": 0.42, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.00642, "same_gap_faster": true}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.903885`, complexity `0.4425`, and adaptation efficiency `0.032435`.
- Last-epoch runtime `68.9473` ms and distance evaluations `4116.5`.
- Validation: surviving `False`, transplant delta `0.002619`, positive scaffolds `0`, Pareto runtime inflation `0.016329`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": 0.016329, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.054968`, combined `0.121317`.
- Accepted novelty `0.886294`, complexity `0.445`, and adaptation efficiency `0.018599`.
- Last-epoch runtime `101.57055` ms and distance evaluations `7393.75`.
- Validation: surviving `False`, transplant delta `0.003188`, positive scaffolds `0`, Pareto runtime inflation `-0.044844`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.0, "gap_delta": 0.0, "runtime_inflation": -0.044844, "same_gap_faster": true}

## Judge Appendix
# TSP Modular-Operator Discovery Suite Evaluation

## Summary of Main Results

| Condition                                   | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Surviving Candidate | Transplant Mean Gap Delta | Ablation Validation | Comments                                                                                       |
|---------------------------------------------|------------------|------------------|--------------------|---------------------|--------------------------|---------------------|------------------------------------------------------------------------------------------------|
| **phase7_baseline_heuristic_only**          | 0.235058         | 0.054968         | 0.121317           | No                  | 0.0                      | N/A                 | Baseline heuristic reference.                                                                 |
| **phase7_full_solver_evolution**             | 0.213387         | 0.064916         | 0.159398           | No                  | 0.0                      | N/A                 | No modular operator; no surviving candidate.                                                  |
| **phase7_modular_operator_evolution**        | 0.235058         | 0.046321         | 0.115856           | No                  | +0.010203                | Pass (small gap deltas on ablations) | Operator: restart_controller; shows positive family signal in 2 families, but fails transplant on key scaffolds; runtime inflated (0.77x slower); transplant gap increased; no survival status. |
| **phase7_modular_operator_random_replay**    | **0.200044**     | 0.053637         | 0.107576           | No                  | -0.012613                | Pass (ablation shows some gap delta but mixed) | Operator: scaffold_selector; best TSPLIB gap; positive transplant on 4 scaffolds; runtime inflation high (1.36x); fails clean transplant on a scaffold; mixed family signals with some regressions. No surviving candidate. |
| **phase7_modular_operator_diversity_residual_replay** | 0.235058 | 0.054968  | 0.121317           | No                  | +0.00152                 | No (ablation shows no effect) | Operator: acceptance; no family improvements; no transplant success; disabling no effect; no survival. |
| **phase7_modular_operator_compression_pressure** | 0.235058       | 0.054968         | 0.121317           | No                  | +0.002619                | No (no ablation effect) | Operator: perturbation; no family improvements; no clear transplant gains; no survival.         |
| **phase7_modular_operator_pareto_selection** | 0.235058        | 0.054968         | 0.121317           | No                  | +0.003188                | No (no ablation effect) | Operator: perturbation; same as above in structure; no ablation or family signal; no survival. |

---

## Conservative Interpretation and Prioritization

### Main Transfer Evidence

- The best transfer gap is **lowest** (best) for `phase7_modular_operator_random_replay` condition (0.107576).
- The best held-out TSPLIB gap also belongs to the same condition (0.200044).
- Family holdout gaps marginally better for modular operator evolution (0.046321) but with worse TSPLIB gap (0.235058).

### Transplant Assessment

- The `phase7_modular_operator_random_replay` operator (scaffold_selector) shows **positive transplant mean gap delta (-0.012613)** over multiple scaffolds and 4 positive scaffolds (out of 5 tested).
- The restart_controller operator in `phase7_modular_operator_evolution` condition shows **positive transplant gap delta (+0.010203)**, indicating worse performance after transplant.
- Perturbation and acceptance operators have near-zero or slightly positive transplant gap deltas (worse), and low or zero positive scaffold counts.

### Ablation Checks

- Only two operators show ablation survival with small positive or zero gap deltas:
  - **restart_controller** operator: small ablation effect (gap delta 0.002615).
  - **scaffold_selector** operator: ablation shows gap increases when disabled or flattened selector variant (gap delta 0.0137); shuffled selector variant improved gap by -0.0087.
- Perturbation and acceptance operators fail ablation validation as disabling causes no performance drop.

### Pareto and Runtime Tradeoffs

- The scaffold_selector operator has largest runtime inflation (1.366747), which is significant for practical use.
- restart_controller has runtime inflation ~0.77x (slower).
- Perturbation and acceptance operators show minor runtime changes (near zero or slight reduction).
- No operator improves gap with faster runtime (no "better gap same runtime").

### Survival

- No operator survived overall modular scaffold and family holdout tests to be accepted as a surviving candidate.
- Though scaffold_selector and restart_controller have some positive signals, they fail transplant robustness or runtime inflation criteria.

---

## Claims Supported by Data (Conservative)

1. **No modular-operator discovery resulted in a surviving candidate by scaffold and family holdout criteria.**

2. The **scaffold_selector operator (phase7_modular_operator_random_replay)** shows:
   - Best held-out TSPLIB gap (0.2000) and best transfer gap (0.1076) among conditions.
   - Ablation validations indicate some effect.
   - Positive transplant mean gap delta (-0.0126, improvement) and 4/5 scaffolds positive.
   - However, high runtime inflation (1.37x) and failure on clean transplant on one scaffold, preventing survival.
   - Demonstrates a reusable structure-to-scaffold mapping concept that improves performance on held-out instances conservatively.
   
3. The **restart_controller operator (phase7_modular_operator_evolution)** exhibits:
   - Some family holdout improvement (-0.0074 mean gap delta).
   - Ablation confirms a small but consistent effect.
   - Fails clean transplant on 2 excluded scaffolds and shows runtime overhead (~0.77x).
   - Transplant gap worsened (+0.0102), indicating less robust transfer.
   - Not a surviving candidate.
   - Operator effectively regulates restart pressure for exploration but lacks transfer robustness.

4. The **perturbation and acceptance operators**:
   - Show no meaningful transfer or family holdout gap improvements.
   - Ablation disables had no detrimental effects, thus no robust operator effect.
   - No surviving candidate.

5. The **full solver evolution** improved training but not transfer or held-out test, no modular structure, no operator survival.

---

## Conclusion

- Despite some promising partial signals in the **scaffold_selector** and **restart_controller** operators, **none pass modular operator survival checks across scaffold transplant and family holdouts**.
- The main transfer gap improvements appear modest (around 1-3% absolute reduction in family gaps) but come at significant runtime costs and transplant fragilities.
- No operator demonstrates clear, robust reusable operator structure proven by survival and transplant.
- No claims about algorithm discovery or reusable operator component survival can be made based on results.
- The scaffold_selector operator is the most promising reusable modular operator candidate in this suite but requires further refinement for runtime efficiency and transplant robustness.

---

# Summary table of interesting modular operators (no survival)

| Operator Name                                | Type              | Transfer Gap | Family Gap | Ablation Validity | Transplant Gap Delta | Runtime Inflation | Surviving? | Notes                                |
|---------------------------------------------|-------------------|--------------|------------|-------------------|---------------------|-------------------|------------|-------------------------------------|
| `context_scaffold_selector_bottleneck_cluster` | scaffold_selector | 0.107576     | 0.053637   | Partial           | -0.012613           | +1.37x            | No         | Best transfer gap, transplant gains, high runtime |
| `restart_controller_stagnation_restart_perturb` | restart_controller | 0.115856    | 0.046321   | Partial           | +0.010203           | +0.77x            | No         | Positive family signal, fragile transplant |
| `acceptance_threshold_worse_moves_with_stagnation_bonus` | acceptance | 0.121317  | 0.054968   | No                | +0.00152            | ~1.0x             | No         | No ablation effect                  |
| `det_escape_perturbation_doublebridge_escalate`     | perturbation      | 0.121317     | 0.054968   | No                | +0.002619           | ~1.0x             | No         | No ablation / family signal         |

---

# Final Recommendations

- Focus on improving **runtime efficiency** and achieving **clean transplant across multiple scaffolds** for scaffold_selector and restart_controller.
- Investigate why ablation signals are missing for acceptance and perturbation modular operators before further pursuit.
- Increase emphasis on robustness of family and held-out transfer gaps, alongside runtime tradeoffs, before declaring reusable modular operators.
- No operator is ready to be used as a modular discovery in production or claimed as an algorithm discovery.

---

*End of report.*
