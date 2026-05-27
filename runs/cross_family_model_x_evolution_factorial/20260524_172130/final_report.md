# Budget-Matched Controls Limit Model-Strength and Replay Claims in LLM Code Evolution

## Purpose

This factorial analysis tests whether evolutionary code search adds performance above base model coding strength across simple games, symmetric TSP, and real-world CVRP.

## Experimental design

Rows analyzed: 750. Task families present: cvrp_phase9_real_world, simple_games, tsp.

The planned full design is 3 model tiers x 5 techniques with 10 simple-game seeds and 20 TSP/CVRP seeds per cell. Partial or smoke outputs are marked by their row counts.

## Model tiers and benchmark strength scores

See `model_strength_table.csv`. The analysis supports both categorical `model_tier` and continuous `benchmark_strength_score`.

## Evolutionary techniques

Techniques: `single_shot`, `budget_matched_no_replay`, `random_replay`, `failure_replay`, and `failure_replay_compression`.

## Task-specific results

| task | model | technique | n | mean performance_z | mean raw | mean novelty |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| cvrp_phase9_real_world | medium_model | budget_matched_no_replay | 20 | 0.3708 | -8.585 | 0.6181 |
| cvrp_phase9_real_world | medium_model | failure_replay | 20 | -0.1425 | -11.14 | 0.2734 |
| cvrp_phase9_real_world | medium_model | failure_replay_compression | 20 | -0.2991 | -11.92 | 0.3233 |
| cvrp_phase9_real_world | medium_model | random_replay | 20 | -0.4003 | -12.42 | 0.3095 |
| cvrp_phase9_real_world | medium_model | single_shot | 20 | -0.1432 | -11.14 | 0 |
| cvrp_phase9_real_world | strong_model | budget_matched_no_replay | 20 | 0.8589 | -6.156 | 0.569 |
| cvrp_phase9_real_world | strong_model | failure_replay | 20 | 1.484 | -3.047 | 0.4093 |
| cvrp_phase9_real_world | strong_model | failure_replay_compression | 20 | -0.1675 | -11.26 | 0.366 |
| cvrp_phase9_real_world | strong_model | random_replay | 20 | 1.097 | -4.974 | 0.3702 |
| cvrp_phase9_real_world | strong_model | single_shot | 20 | -0.2717 | -11.78 | 0 |
| cvrp_phase9_real_world | weak_model | budget_matched_no_replay | 20 | -0.5287 | -13.06 | 0.6193 |
| cvrp_phase9_real_world | weak_model | failure_replay | 20 | -0.5287 | -13.06 | 0.3648 |
| cvrp_phase9_real_world | weak_model | failure_replay_compression | 20 | -0.5287 | -13.06 | 0.369 |
| cvrp_phase9_real_world | weak_model | random_replay | 20 | -0.2709 | -11.78 | 0.3818 |
| cvrp_phase9_real_world | weak_model | single_shot | 20 | -0.5287 | -13.06 | 0 |
| simple_games | medium_model | budget_matched_no_replay | 10 | 0.5659 | 0.5273 | 0.6598 |
| simple_games | medium_model | failure_replay | 10 | -0.9354 | 0.1909 | 0.07102 |
| simple_games | medium_model | failure_replay_compression | 10 | -0.7812 | 0.2255 | 0.0605 |
| simple_games | medium_model | random_replay | 10 | -0.2294 | 0.3491 | 0.04661 |
| simple_games | medium_model | single_shot | 10 | -0.9029 | 0.1982 | 0 |
| simple_games | strong_model | budget_matched_no_replay | 10 | 0.8823 | 0.5982 | 0.5775 |
| simple_games | strong_model | failure_replay | 10 | 0.4604 | 0.5036 | 0.562 |
| simple_games | strong_model | failure_replay_compression | 10 | 0.6308 | 0.5418 | 0.506 |
| simple_games | strong_model | random_replay | 10 | 0.8418 | 0.5891 | 0.5432 |
| simple_games | strong_model | single_shot | 10 | -0.2943 | 0.3345 | 0 |
| simple_games | weak_model | budget_matched_no_replay | 10 | 0.6064 | 0.5364 | 0.6699 |
| simple_games | weak_model | failure_replay | 10 | -0.02651 | 0.3945 | 0.2251 |
| simple_games | weak_model | failure_replay_compression | 10 | -0.09954 | 0.3782 | 0.1744 |
| simple_games | weak_model | random_replay | 10 | 0.03841 | 0.4091 | 0.2129 |
| simple_games | weak_model | single_shot | 10 | -0.7568 | 0.2309 | 0 |
| tsp | medium_model | budget_matched_no_replay | 20 | 0.07828 | -0.2134 | 0.728 |
| tsp | medium_model | failure_replay | 20 | 0.07828 | -0.2134 | 0.06069 |
| tsp | medium_model | failure_replay_compression | 20 | -0.003437 | -0.2136 | 0.2038 |
| tsp | medium_model | random_replay | 20 | -0.1953 | -0.214 | 0.05938 |
| tsp | medium_model | single_shot | 20 | 0.07828 | -0.2134 | 0 |
| tsp | strong_model | budget_matched_no_replay | 20 | -0.7406 | -0.2151 | 0.6953 |
| tsp | strong_model | failure_replay | 20 | 0.07828 | -0.2134 | 0.4104 |
| tsp | strong_model | failure_replay_compression | 20 | 0.07828 | -0.2134 | 0.3182 |
| tsp | strong_model | random_replay | 20 | 0.07828 | -0.2134 | 0.4169 |
| tsp | strong_model | single_shot | 20 | 0.07828 | -0.2134 | 0 |
| tsp | weak_model | budget_matched_no_replay | 20 | 0.07828 | -0.2134 | 0.7468 |
| tsp | weak_model | failure_replay | 20 | 0.07828 | -0.2134 | 0.3393 |
| tsp | weak_model | failure_replay_compression | 20 | 0.07828 | -0.2134 | 0.2511 |
| tsp | weak_model | random_replay | 20 | 0.07828 | -0.2134 | 0.3484 |
| tsp | weak_model | single_shot | 20 | 0.07828 | -0.2134 | 0 |

## Model x evolution matrices

CSV matrices and matching matrix heatmaps are in `model_x_evolution_matrices/`; duplicated report heatmaps are in `figures/`.

## Variance decomposition

Formulas:

- Task continuous: `performance_z ~ benchmark_strength_score + C(evolution_technique) + benchmark_strength_score:C(evolution_technique)`.
- Task categorical: `performance_z ~ C(model_tier) * C(evolution_technique)`.
- Pooled continuous: `performance_z ~ C(task_family) * benchmark_strength_score * C(evolution_technique)`.
- Pooled categorical: `performance_z ~ C(task_family) * C(model_tier) * C(evolution_technique)`.

Pooled continuous model: model-strength R2=0.0008843, evolution-technique R2=0.01002, interaction R2=0.06909, residual variance=0.8298.

## Effect sizes relative to single-shot

10 comparisons have bootstrap CIs above zero relative to single-shot.

## Effect sizes relative to budget-matched no-replay

0 comparisons have bootstrap CIs above zero relative to budget-matched no-replay.

## Cross-family interpretation

The interpretation should focus on the budget control. Replay/failure/compression techniques beat budget-matched no-replay in 0 tested task/model comparisons with positive bootstrap support; therefore, gains over single-shot should be interpreted primarily as effects of extra search budget unless a task-specific budget-control comparison supports a stronger claim. Pooled continuous model: model-strength R2=0.0008843, evolution-technique R2=0.01002, interaction R2=0.06909, residual variance=0.8298.

## Main conclusion

The budget-feasible model ladder does not show clean model-strength dominance, and replay/failure/compression do not beat the budget-matched no-replay control. Pooled model-strength R2=0.0008843, evolution-technique R2=0.01002, and interaction R2=0.06909; the strongest conclusion is that apparent gains over single-shot mostly reflect search budget and task/model-specific interactions rather than robust replay-specific value.

## Limitations

- Do not overclaim algorithmic discovery; this phase compares model strength and search technique, not novelty of discovered algorithms.
- Replay/failure/compression should be claimed useful only when they beat `budget_matched_no_replay`, not merely when they beat `single_shot`.
- Smoke runs validate schema only; scientific conclusions require the full paid campaign.
- P-values use reduced-model OLS/ANOVA approximations implemented locally to avoid adding heavy statistics dependencies.

## Required Questions

1. How much variance is explained by model strength? 0.0008843.
2. How much variance is explained by evolutionary technique? 0.01002.
3. Is there a model strength x technique interaction? 0.06909.
4. Do replay/failure/compression techniques beat a budget-matched no-replay control? 0 comparisons beat budget-matched no-replay with positive bootstrap support.
5. Are evolutionary gains larger for weak models than strong models? insufficient or no positive budget-control gains.
6. Is the strongest conclusion model strength dominates, evolution adds independent value, or evolution only helps under certain task/model regimes? The budget-feasible model ladder does not show clean model-strength dominance, and replay/failure/compression do not beat the budget-matched no-replay control. Pooled model-strength R2=0.0008843, evolution-technique R2=0.01002, and interaction R2=0.06909; the strongest conclusion is that apparent gains over single-shot mostly reflect search budget and task/model-specific interactions rather than robust replay-specific value.

## Artifact Paths

- `all_runs_long.csv`: `runs\cross_family_model_x_evolution_factorial\20260524_172130\all_runs_long.csv`
- `variance_partition_summary.csv`: `runs\cross_family_model_x_evolution_factorial\20260524_172130\variance_decomposition\variance_partition_summary.csv`