# Phase 8 Aggregate Report

## Overview
- Run count: 20.
- Condition count: 8.
- Best held-out TSPLIB condition: `phase8_best_single_fixed_heuristic`.

## Condition Means
| Condition | Final TSPLIB Gap | Final Transfer Gap | Selector Regret | Runtime-Adjusted Gap | Runtime Inflation | Mean Novelty | Mean Complexity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phase8_best_single_fixed_heuristic | 0.07226 | 0.031222 | 0.0 | 0.07226 | 0.0 | 0.0 | 0.0 |
| phase8_full_solver_evolution | 0.167249 | 0.11025 | 0.094989 | 0.167249 | -0.79877 | 0.732834 | 0.66 |
| phase8_llm_evolved_adaptive_controller | 0.155397 | 0.083357 | 0.083137 | 0.27381 | 0.746118 | 0.283303 | 0.897125 |
| phase8_llm_evolved_controller_diversity_failure_replay | 0.16551 | 0.093285 | 0.09325 | 0.337175 | 1.054372 | 0.503036 | 0.846875 |
| phase8_llm_static_selector | 0.193515 | 0.095613 | 0.121255 | 0.295981 | 0.309192 | 0.0 | 0.746 |
| phase8_oracle_selector | 0.07226 | 0.026678 | 0.0 | 0.07338 | 0.011291 | 0.0 | 0.0 |
| phase8_random_portfolio | 0.191943 | 0.122316 | 0.119683 | 0.258686 | -0.107764 | 0.0 | 0.0 |
| phase8_supervised_ml_selector | 0.07226 | 0.031222 | 0.0 | 0.074051 | 0.020029 | 0.0 | 0.0 |

## Paired Comparisons
### random_vs_best_fixed
- Candidate: `phase8_random_portfolio` versus reference `phase8_best_single_fixed_heuristic` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.119683 (95% CI 0.108269 to 0.130787).
- Transfer gap delta: 0.091094 (95% CI 0.082606 to 0.099808).
- Selector regret delta: 0.119683 (95% CI 0.10817 to 0.130823).
### supervised_vs_best_fixed
- Candidate: `phase8_supervised_ml_selector` versus reference `phase8_best_single_fixed_heuristic` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.0 (95% CI 0.0 to 0.0).
- Transfer gap delta: 0.0 (95% CI 0.0 to 0.0).
- Selector regret delta: 0.0 (95% CI 0.0 to 0.0).
### static_vs_supervised
- Candidate: `phase8_llm_static_selector` versus reference `phase8_supervised_ml_selector` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.121255 (95% CI 0.099278 to 0.140226).
- Transfer gap delta: 0.064391 (95% CI 0.049635 to 0.078397).
- Selector regret delta: 0.121255 (95% CI 0.099839 to 0.140491).
### adaptive_vs_static
- Candidate: `phase8_llm_evolved_adaptive_controller` versus reference `phase8_llm_static_selector` across 20 paired runs.
- Held-out TSPLIB gap delta: -0.038118 (95% CI -0.06868 to -0.00707).
- Transfer gap delta: -0.012256 (95% CI -0.033612 to 0.008575).
- Selector regret delta: -0.038118 (95% CI -0.068547 to -0.006883).
### replay_vs_adaptive
- Candidate: `phase8_llm_evolved_controller_diversity_failure_replay` versus reference `phase8_llm_evolved_adaptive_controller` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.010114 (95% CI -0.020641 to 0.041674).
- Transfer gap delta: 0.009928 (95% CI -0.010223 to 0.031181).
- Selector regret delta: 0.010114 (95% CI -0.02087 to 0.041393).
### full_solver_vs_adaptive
- Candidate: `phase8_full_solver_evolution` versus reference `phase8_llm_evolved_adaptive_controller` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.011853 (95% CI -0.025032 to 0.049041).
- Transfer gap delta: 0.026893 (95% CI -0.004858 to 0.059364).
- Selector regret delta: 0.011853 (95% CI -0.024976 to 0.04907).
### oracle_vs_best_fixed
- Candidate: `phase8_oracle_selector` versus reference `phase8_best_single_fixed_heuristic` across 20 paired runs.
- Held-out TSPLIB gap delta: 0.0 (95% CI 0.0 to 0.0).
- Transfer gap delta: -0.004544 (95% CI -0.004544 to -0.004544).
- Selector regret delta: 0.0 (95% CI 0.0 to 0.0).

## Portfolio Answers
- Selector progress: Supervised selection changed held-out TSPLIB gap by 0.0 versus the best fixed heuristic. Adaptive LLM control changed held-out TSPLIB gap by -0.038118 versus the static LLM selector, while the oracle remained 0.0 better than the best fixed heuristic.
- Replay effect: Diversity-failure replay changed held-out TSPLIB gap by 0.010114 and selector regret by 0.010114 relative to the no-replay adaptive controller.
- Interpretability tradeoff: Full-solver evolution changed held-out TSPLIB gap by 0.011853 and runtime-adjusted gap by -0.106561 relative to the adaptive controller.
