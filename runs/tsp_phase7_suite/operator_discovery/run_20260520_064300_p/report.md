# Modular Operator Discovery TSP Report

## Overview
- Condition count: 7.
- Best final transfer gap: `phase7_modular_operator_random_replay`.
- Best held-out TSPLIB gap: `phase7_modular_operator_random_replay`.
- Surviving modular candidates: none.

## Run Metadata
- run_name: run_20260520_064300_p
- started_at_local: 2026-05-20 06:43:00
- finished_at_local: 2026-05-20 07:17:07
- duration_hhmm: 00:34
- duration_seconds: 2047.07
- seed_offset: 15000
- replicate_label: p
- judge_status: enabled
- judge_provider: openai
- judge_model: gpt-4.1-mini

## Condition Comparison
| Condition | Mode | Replay | Selection | Final TSPLIB Gap | Final Family Gap | Final Transfer Gap | Mean Novelty | Mean Complexity | Surviving Candidate | Transplant Delta | Pareto Runtime Inflation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| phase7_baseline_heuristic_only | baseline_only | none | score_only | 0.235058 | 0.054968 | 0.121317 | 0.0 | 0.0 | False | 0.0 | 0.0 |
| phase7_full_solver_evolution | full_solver | none | score_only | 0.213387 | 0.064916 | 0.159398 | 0.903718 | 0.56 | False | 0.0 | 0.0 |
| phase7_modular_operator_evolution | modular_operator | none | score_only | 0.235058 | 0.046321 | 0.115856 | 0.862441 | 0.445 | False | 0.009454 | 0.790432 |
| phase7_modular_operator_random_replay | modular_operator | random | score_only | 0.174128 | 0.074362 | 0.111118 | 0.0 | 0.445 | False | -0.036453 | 1.105281 |
| phase7_modular_operator_diversity_residual_replay | modular_operator | diversity_residual | score_only | 0.235058 | 0.049737 | 0.118013 | 0.821465 | 0.445 | False | 0.009816 | 0.825788 |
| phase7_modular_operator_compression_pressure | modular_operator | none | novelty_gate | 0.235058 | 0.050827 | 0.118702 | 0.862626 | 0.44 | False | 0.010373 | 0.821431 |
| phase7_modular_operator_pareto_selection | modular_operator | none | pareto | 0.255674 | 0.119719 | 0.169808 | 0.0 | 0.4425 | False | 0.042452 | 1.679113 |

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
- Accepted novelty `0.903718`, complexity `0.56`, and adaptation efficiency `-0.027558`.
- Last-epoch runtime `0.0` ms and distance evaluations `0.0`.
- Validation: surviving `False`, transplant delta `0.0`, positive scaffolds `0`, Pareto runtime inflation `0.0`.

### phase7_modular_operator_evolution
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.046321`, combined `0.115856`.
- Accepted novelty `0.862441`, complexity `0.445`, and adaptation efficiency `0.034424`.
- Last-epoch runtime `116.588075` ms and distance evaluations `5381.5`.
- Validation: surviving `False`, transplant delta `0.009454`, positive scaffolds `1`, Pareto runtime inflation `0.790432`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.856118, "gap_delta": -0.002615, "runtime_inflation": 0.790432, "same_gap_faster": false}

### phase7_modular_operator_random_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.174128`, family holdout `0.074362`, combined `0.111118`.
- Accepted novelty `0.0`, complexity `0.445`, and adaptation efficiency `0.0`.
- Last-epoch runtime `68.09175` ms and distance evaluations `3810.75`.
- Validation: surviving `False`, transplant delta `-0.036453`, positive scaffolds `4`, Pareto runtime inflation `1.105281`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 11.887779, "gap_delta": -0.014035, "runtime_inflation": 1.105281, "same_gap_faster": false}

### phase7_modular_operator_diversity_residual_replay
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.049737`, combined `0.118013`.
- Accepted novelty `0.821465`, complexity `0.445`, and adaptation efficiency `0.009255`.
- Last-epoch runtime `139.094125` ms and distance evaluations `4770.25`.
- Validation: surviving `False`, transplant delta `0.009816`, positive scaffolds `1`, Pareto runtime inflation `0.825788`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.892165, "gap_delta": -0.005462, "runtime_inflation": 0.825788, "same_gap_faster": false}

### phase7_modular_operator_compression_pressure
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.235058`, family holdout `0.050827`, combined `0.118702`.
- Accepted novelty `0.862626`, complexity `0.44`, and adaptation efficiency `0.016828`.
- Last-epoch runtime `75.22365` ms and distance evaluations `4892.0`.
- Validation: surviving `False`, transplant delta `0.010373`, positive scaffolds `1`, Pareto runtime inflation `0.821431`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 12, "complexity_score": 0.44, "distance_eval_inflation": 0.869479, "gap_delta": -0.003304, "runtime_inflation": 0.821431, "same_gap_faster": false}

### phase7_modular_operator_pareto_selection
- Execution mode `modular_operator` on host scaffold `nearest_neighbor_2opt`.
- Final gaps: TSPLIB `0.255674`, family holdout `0.119719`, combined `0.169808`.
- Accepted novelty `0.0`, complexity `0.4425`, and adaptation efficiency `0.0`.
- Last-epoch runtime `71.39275` ms and distance evaluations `4515.0`.
- Validation: surviving `False`, transplant delta `0.042452`, positive scaffolds `0`, Pareto runtime inflation `1.679113`.
- Validation summary: {"better_gap_same_runtime": false, "code_length_lines": 13, "complexity_score": 0.46, "distance_eval_inflation": 2.049916, "gap_delta": 0.042667, "runtime_inflation": 1.679113, "same_gap_faster": false}

## Judge Appendix
```markdown
# TSP Modular-Operator Discovery Suite: Summary & Interpretation

## Main Transfer/Generalization Evidence (Held-out TSPLIB & Family Holdout Gap)

- **Held-out TSPLIB gap:**  
  - Baseline heuristic (phase7_baseline_heuristic_only): 0.235058  
  - Operators with modular execution modes show no improvement or slightly worse gaps on held-out TSPLIB instances (all around 0.174-0.235, none better than baseline).  
  - Best modular operator condition on TSPLIB gap:  
    - `phase7_modular_operator_random_replay` achieves 0.174128 but suffers from ablation and transplant weaknesses (see below).

- **Family holdout gap (family gap):**  
  - The smaller final family gap relative to baseline (0.054968) indicates potential transfer; modular operators sometimes show modest improvements or slight regressions.  
  - Best family gap results are from restart controllers (`phase7_modular_operator_evolution`, `phase7_modular_operator_diversity_residual_replay`, `phase7_modular_operator_compression_pressure`) showing ~0.046–0.050, slightly better than baseline heuristic at 0.054968.  
  - Scaffold selectors show mixed or worse family gap results (sometimes severe regressions).

## Operator Validation: Transplant & Ablation Checks

### Restart Controllers (`restart_controller` type)

- **Abalation:**  
  - Ablation gap deltas near zero (≤ 0.005) indicating operator effect is small but present (restarts contribute small but consistent gap gains).  
  - Variants disabling the restart operators increase gap slightly, consistent with a modest real effect.

- **Transplant:**  
  - Transplant mean gap deltas mostly positive (~+0.009 to +0.010), indicating transplant hurts performance overall.  
  - Positive scaffold transplant count is low (1 per restart operator), transplanting only cleanly into the native scaffold (nearest_neighbor_2opt) or few others.  
  - Does not transplant cleanly into `sparse_three_opt` or `clustered_local_search`.

- **Runtime Inflation:**  
  - Significant runtime inflation (~0.82 to 0.83), which is a downside.

- **Overall:**  
  Restart controllers provide **some transferable operator structure** (modest gap reduction on family holdout + stable ablation), but transfer beyond native scaffold is weak, with runtime costs and transplant issues. No surviving candidate.

### Scaffold Selectors (`scaffold_selector` type)

- Example: `phase7_modular_operator_random_replay` (best TSPLIB performer) and `phase7_modular_operator_pareto_selection`:

- **Ablation:**  
  - Disabling operator does not hurt or even improves performance in some variants (e.g., `flattened_selector`).  
  - Some variants (shuffled selector) improve gap further, suggesting core operator effect is not robust or clear.

- **Transplant:**  
  - Varying transplant gap delta:  
    - `random_replay` selection shows mean transplant gap delta -0.036 (positive effect in transplant) with 4 positive scaffolds.  
    - However, severe regressions on several families balance this out.  
    - Other scaffold selectors show negative transplant results and do not transplant cleanly in multiple scaffolds.

- **Family & Held-out Gaps:**  
  - Mixed signals: underperforms in several important families (e.g., heldout_tsplib, grid_like_tsp, nearest_neighbor_trap_tsp).  
  - Positive signal mainly in two_cluster_bottleneck_tsp but not uniformly.

- **Runtime Inflation:**  
  - High runtime inflation (>1.0, up to 1.68 in pareto selection), a negative tradeoff.

- **Overall:**  
  Scaffold selectors fail ablation validation (disabling does not hurt), show mixed or poor transfer with multiple severe regressions, and suffer high runtime inflation. No robust reusable operator structure demonstrated.

## Pareto Tradeoffs

- None of the modular operators simultaneously improve gap and runtime over baseline.  
- Pareto gap deltas are marginal negative (small gap reductions) or even positive (worse gap), while runtime inflation consistently high (≥0.79 for restart controllers, >1.0 for scaffold selectors).  
- No condition shows "better gap at same runtime" or "same gap faster."

## Surviving Candidates

- **None** survived all checks including transplant, ablation, and family holdout tests.  
- The modular restart controllers show the most promise with modest positive family holdout gap improvement and some ablation evidence but fail transplant cleanly and suffer runtime cost.  
- Scaffold selectors have inconsistent benefit and fail ablation validation.

---

# **Conservative Conclusions**

1. **No modular operator qualifies as a surviving, fully transferable reusable operator** given the failure in transplant and ablation checks, plus runtime inflation.

2. **Restart controllers (adaptive restart schedules) show modest validation support**:  
   - They yield small consistent improvements on family holdout gap (~0.046 vs 0.055 baseline).  
   - Ablation shows some operator effect.  
   - However, poor transplant performance, runtime inflation (~82%), and failure on key scaffold transplants limit claims.

   This supports **reusable operator structure related to adaptive restart control in nearest_neighbor_2opt and closely related scaffolds only**, but no broad transfer or solver discovery.

3. **Scaffold selectors exhibit unstable performance with ablation failing to show clear operator effect**, have multiple severe regressions on families, and runtime overhead. Transfer and transplant is inconsistent. No clear reusable abstraction.

4. **Full-solver evolution and baseline remain the strongest references**:  
   - Neither baseline nor full-solvers produce reusable modular operators per criteria.  
   - The modular operator conditions do not clearly outperform baseline on held-out TSPLIB gap.

5. **Best performing condition on held-out TSPLIB gap, `phase7_modular_operator_random_replay`, does not survive ablation nor transplant fully; thus no claim of real reusable discovery.**

---

# **Summary Table**

| Operator Type             | Best Family Gap | Held-out TSPLIB Gap | Ablation Valid? | Transplant Valid? | Runtime Inflation | Surviving Candidate? | Notes                              |
|--------------------------|-----------------|---------------------|-----------------|-------------------|-------------------|---------------------|------------------------------------|
| Restart Controllers       | ~0.046 (vs 0.055 baseline) | ~0.235 (same as baseline)   | Modest +        | No (fails cleanly on multiple scaffolds) | ~0.82             | No                  | Reusable restart structure in native scaffold only; runtime cost |
| Scaffold Selectors        | Mixed (some severe regressions) | ~0.174 best (random replay) but with ablation failures | No              | Mixed; some transplant benefit but severe regressions | High (>1.0)        | No                  | Operator effect unclear; poor robustness |
| Full-solver (non-modular) | N/A             | ~0.213               | N/A             | N/A               | Low               | No                  | Baseline for comparison           |
| Baseline Heuristic Only   | 0.055           | 0.235                 | N/A             | N/A               | N/A               | N/A                 | Base reference                    |

---

# **Final Interpretation**

- The suite has **not discovered a validated modular operator that generalizes robustly across held-out TSPLIB and family holdouts with surviving ablation and transplant checks**.

- Restart controllers offer a **partially reusable operator pattern related to adaptive restart control in specific scaffold contexts**, but lack broad transfer or pareto improvements.

- Scaffold selectors lack robust modular operator evidence; ablation and transfer analyses suggest no true operator effect.

- No full solver algorithm discoveries from these modular operators under the strict criteria.

---

# **Recommendation**

- Focus further research on improving restart controller transplantability and runtime efficiency to enhance practical transfer.

- Reconsider scaffold selector designs to produce clearer ablation signals and across-family generalization.

- Maintain baseline and full-solver evolutions as important performance baselines, as no modular operator yet overcomes them consistently.

```
