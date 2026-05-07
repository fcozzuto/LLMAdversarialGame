# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260507_012808_c
- Started: 2026-05-07 01:28:08
- Finished: 2026-05-07 03:07:57
- Duration: 01:40

## Models and Roles
- `fixed_predator_holdout_endpoint`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `builtin:resource_denier`.
- `rotating_opponents_holdout_endpoint`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `rotating_plus_nemesis_archive`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `rotating_plus_novelty_gate`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `rotating_plus_replay_aware_selection`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `rotating_plus_nemesis_novelty_replay`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `judge`: `openai:gpt-4.1-mini`.

## Threats To Validity
- Code novelty is a normalized lexical change metric. The curriculum reports now add behavioral descriptors, but those descriptors are still heuristic summaries rather than full policy semantics.
- Policy markers are heuristic indicators of potential rule violations; they are not proof of cheating or malicious intent.
- Looping, exploration, and pressure-response metrics are heuristic operationalizations of the supervisor-facing concepts, so they should be interpreted alongside qualitative epoch inspection rather than as perfect ground truth.
- Acceptance-time replay checks and holdout spot checks are small-sample robustness probes. They improve selection discipline, but they are not substitutes for the final held-out evaluation panel.
- Results from a single run should be treated as provisional until replicated across additional seeds and repeated runs with cross-run statistics.
- Conclusions are specific to this grid-game environment, the chosen prompts, and the configured model pairings; they do not automatically generalize to other tasks.
- Conditions with generation errors or fallback executions (`fixed_predator_holdout_endpoint`, `rotating_plus_nemesis_archive`, `rotating_plus_novelty_gate`, `rotating_plus_nemesis_novelty_replay`) weaken causal claims and should be weighted less heavily than cleaner conditions.

## Data Quality Warnings
- fixed_predator_holdout_endpoint / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- fixed_predator_holdout_endpoint / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.
- rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano) had generation errors in 3/100 epochs.
- rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano) fell back to default code in 3/100 epochs.
- rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano) had generation errors in 2/100 epochs.
- rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano) fell back to default code in 2/100 epochs.
- rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: resource_collection.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 24.8333, stable strategy switches 42.8333, behavior-cell coverage 21.5, specific adaptations 20.0, degradation signals 5.1667.
- Holdout evaluation conditions present in this run: 6.
- Average primary holdout win rate across evaluated conditions: 0.5467.
- Average primary holdout score margin across evaluated conditions: 1.4133.

## How To Read The Score Charts
- Each `scores.svg` file plots one point per epoch for each agent.
- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.
- Higher points mean the agent performed better under that environment's scoring rules in that specific epoch.
- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.

## Condition Results
### fixed_predator_holdout_endpoint
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (builtin:resource_denier).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=fixed_predator, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: builtin:resource_denier
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (builtin:resource_denier) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=fixed_predator, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (builtin:resource_denier), rotation policy=cyclic.
- Opponent pool: resource_denier.
- Acceptance rule: mode=accept_all, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=26, stable strategy switches=53, behavior-cell coverage=26, specific adaptations=19, degradation signals=0.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.235 vs 5.715) and win count (51 vs 26) with 23 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (builtin:resource_denier) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.482 and last-three-epoch novelty 0.5847.
- agent_b (builtin:resource_denier) had average code novelty 0.0 and last-three-epoch novelty 0.0.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0816, exploration=0.8768, revisit=0.1232, resource pursuit=0.3704, opponent pursuit=0.6394, opponent distance=0.485. Latest profile: opportunistic_switcher.
- agent_b (builtin:resource_denier) behavioral profile averaged stay=0.1201, exploration=0.8685, revisit=0.1315, resource pursuit=0.3767, opponent pursuit=0.6394, opponent distance=0.485. Latest profile: explorer.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (builtin:resource_denier) produced 1 unique normalized code variants, with 99 unchanged transitions, current unchanged streak 100, and 53 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (builtin:resource_denier) showed plateau signals: repeated_same_code_recently, no_recent_score_improvement, single_strategy_entire_run.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_obstacle x18.
- agent_b (builtin:resource_denier) runtime issues: move_hits_obstacle x308.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.48, mean holdout score margin 1.0 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.9, mean margin 1.8, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 5.5, mean margin -1.0, win rate 0.2.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.0, mean margin 6.0, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.8, mean margin -0.4, win rate 0.4.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.3, mean margin -1.4, win rate 0.2.
- Suggested qualitative follow-up, epoch 9: largest score margin: agent_a (openai:gpt-5.4-nano) 0.0 vs agent_b (builtin:resource_denier) 12.0. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_009/artifact.json`.
- Suggested qualitative follow-up, epoch 15: most runtime issues in one epoch: 68. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_015/artifact.json`.
- Suggested qualitative follow-up, epoch 82: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_082/artifact.json`.
- Suggested qualitative follow-up, epoch 98: largest average code shift between consecutive epochs: 0.3967. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_098/artifact.json`.
- Score chart artifact: `fixed_predator_holdout_endpoint/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![fixed_predator_holdout_endpoint score chart](fixed_predator_holdout_endpoint/scores.png)

### rotating_opponents_holdout_endpoint
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating_opponents, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_opponents, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=accept_all, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=26, stable strategy switches=50, behavior-cell coverage=23, specific adaptations=21, degradation signals=0.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.955 vs 4.755) and win count (60 vs 26) with 14 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.4967 and last-three-epoch novelty 0.5254.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0644, exploration=0.8861, revisit=0.1139, resource pursuit=0.3767, opponent pursuit=0.5549, opponent distance=0.4828. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2702, exploration=0.7352, revisit=0.2648, resource pursuit=0.3158, opponent pursuit=0.5549, opponent distance=0.4828. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x80.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x344.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.56, mean holdout score margin 1.84 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.4, mean margin 2.8, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.5, mean margin 1.0, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.0, mean margin 6.0, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.5, mean margin 1.0, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.2, mean margin -1.6, win rate 0.2.
- Suggested qualitative follow-up, epoch 2: largest score margin: agent_a (openai:gpt-5.4-nano) 0.0 vs agent_b (curriculum:opponent_pool[4]) 12.0. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_002/artifact.json`.
- Suggested qualitative follow-up, epoch 54: most runtime issues in one epoch: 144. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_054/artifact.json`.
- Suggested qualitative follow-up, epoch 10: largest average code shift between consecutive epochs: 0.8828. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_010/artifact.json`.
- Score chart artifact: `rotating_opponents_holdout_endpoint/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_opponents_holdout_endpoint score chart](rotating_opponents_holdout_endpoint/scores.png)

### rotating_plus_nemesis_archive
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis_archive, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_nemesis_archive, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=accept_all, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Nemesis archive: reintroduce_every=5, min_score_margin=1.0, max_size=8.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=21, stable strategy switches=45, behavior-cell coverage=21, specific adaptations=18, degradation signals=0.
- Archive snapshots stored: 4.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.02 vs 4.53) and win count (59 vs 21) with 20 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 97/100 epochs and executed submitted code in 97/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5367 and last-three-epoch novelty 0.4969.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6766 and last-three-epoch novelty 0.5239.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0824, exploration=0.8688, revisit=0.1312, resource pursuit=0.3486, opponent pursuit=0.57, opponent distance=0.4856. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2537, exploration=0.7483, revisit=0.2517, resource pursuit=0.3339, opponent pursuit=0.57, opponent distance=0.4856. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 12 unchanged transitions, current unchanged streak 2, and 6 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x160, move_hits_obstacle x98, runtime_error:cannot access local variable 'ddy' where it is not associated with a value x8.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x481.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: syntax_error:'[' was never closed, syntax_error:closing parenthesis ']' does not match opening parenthesis '('.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.44, mean holdout score margin 0.76 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.9, mean margin 1.8, win rate 0.4.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.3, mean margin 1.2, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.0, mean margin 4.0, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.0, mean margin -1.8, win rate 0.2.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.3, mean margin -1.4, win rate 0.2.
- Suggested qualitative follow-up, epoch 6: largest score margin: agent_a (openai:gpt-5.4-nano) 0.0 vs agent_b (curriculum:opponent_pool[4]) 12.0. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 23: most runtime issues in one epoch: 156. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_023/artifact.json`.
- Suggested qualitative follow-up, epoch 6: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `rotating_plus_nemesis_archive/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 2: largest average code shift between consecutive epochs: 0.8781. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_002/artifact.json`.
- Score chart artifact: `rotating_plus_nemesis_archive/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_nemesis_archive score chart](rotating_plus_nemesis_archive/scores.png)

### rotating_plus_novelty_gate
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+novelty_gate, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_novelty_gate, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=score_or_diversity, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=31, stable strategy switches=28, behavior-cell coverage=20, specific adaptations=23, degradation signals=17.
- Focal elite archive coverage: 9 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.26 vs 5.06) and win count (52 vs 31) with 17 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 98/100 epochs and executed submitted code in 98/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5784 and last-three-epoch novelty 0.5522.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.1163, exploration=0.8065, revisit=0.1935, resource pursuit=0.358, opponent pursuit=0.5605, opponent distance=0.4736. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2747, exploration=0.7238, revisit=0.2762, resource pursuit=0.316, opponent pursuit=0.5605, opponent distance=0.4736. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x143, move_hits_obstacle x78.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x548.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.6, mean holdout score margin 1.44 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.0, mean margin 2.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.2, mean margin 1.0, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.4, mean margin 4.8, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.2, mean margin -0.8, win rate 0.4.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.1, mean margin 0.2, win rate 0.6.
- Suggested qualitative follow-up, epoch 3: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_novelty_gate/epochs/epoch_003/artifact.json`.
- Suggested qualitative follow-up, epoch 59: most runtime issues in one epoch: 80. Artifact: `rotating_plus_novelty_gate/epochs/epoch_059/artifact.json`.
- Suggested qualitative follow-up, epoch 5: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `rotating_plus_novelty_gate/epochs/epoch_005/artifact.json`.
- Suggested qualitative follow-up, epoch 2: largest average code shift between consecutive epochs: 0.8581. Artifact: `rotating_plus_novelty_gate/epochs/epoch_002/artifact.json`.
- Score chart artifact: `rotating_plus_novelty_gate/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_novelty_gate score chart](rotating_plus_novelty_gate/scores.png)

### rotating_plus_replay_aware_selection
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+replay_aware, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_replay_aware_selection, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=score_only, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=22, stable strategy switches=43, behavior-cell coverage=18, specific adaptations=18, degradation signals=5.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.305 vs 4.355) and win count (63 vs 22) with 15 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6103 and last-three-epoch novelty 0.5579.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0461, exploration=0.9044, revisit=0.0956, resource pursuit=0.3771, opponent pursuit=0.5784, opponent distance=0.505. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2893, exploration=0.7204, revisit=0.2796, resource pursuit=0.3174, opponent pursuit=0.5784, opponent distance=0.505. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: runtime_error:list index out of range x67.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x416.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.56, mean holdout score margin 1.52 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.5, mean margin 1.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.4, mean margin 0.8, win rate 0.2.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.0, mean margin 6.0, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.3, mean margin -1.4, win rate 0.4.
- Suggested qualitative follow-up, epoch 15: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_015/artifact.json`.
- Suggested qualitative follow-up, epoch 90: most runtime issues in one epoch: 78. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_090/artifact.json`.
- Suggested qualitative follow-up, epoch 95: largest average code shift between consecutive epochs: 0.8772. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_095/artifact.json`.
- Score chart artifact: `rotating_plus_replay_aware_selection/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_replay_aware_selection score chart](rotating_plus_replay_aware_selection/scores.png)

### rotating_plus_nemesis_novelty_replay
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, replicate_label=c, seed_offset=2000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_nemesis_novelty_replay, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=score_or_diversity, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Nemesis archive: reintroduce_every=5, min_score_margin=1.0, max_size=8.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=23, stable strategy switches=38, behavior-cell coverage=21, specific adaptations=21, degradation signals=9.
- Archive snapshots stored: 3.
- Focal elite archive coverage: 7 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.265 vs 4.535) and win count (59 vs 23) with 18 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5579 and last-three-epoch novelty 0.5516.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6581 and last-three-epoch novelty 0.7863.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0463, exploration=0.9226, revisit=0.0774, resource pursuit=0.404, opponent pursuit=0.5991, opponent distance=0.4691. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2696, exploration=0.7395, revisit=0.2606, resource pursuit=0.3196, opponent pursuit=0.5991, opponent distance=0.4691. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 13 unchanged transitions, current unchanged streak 1, and 2 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: runtime_error:not enough values to unpack (expected 5, got 4) x80.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x497.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.64, mean holdout score margin 1.92 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.1, mean margin 2.2, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.4, mean margin 0.8, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.6, mean margin 5.2, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.3, mean margin 0.6, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.4, mean margin 0.8, win rate 0.6.
- Suggested qualitative follow-up, epoch 8: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_008/artifact.json`.
- Suggested qualitative follow-up, epoch 44: most runtime issues in one epoch: 155. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_044/artifact.json`.
- Suggested qualitative follow-up, epoch 11: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_011/artifact.json`.
- Suggested qualitative follow-up, epoch 5: largest average code shift between consecutive epochs: 0.8201. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_005/artifact.json`.
- Suggested qualitative follow-up, epoch 2: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_002/artifact.json`.
- Score chart artifact: `rotating_plus_nemesis_novelty_replay/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_nemesis_novelty_replay score chart](rotating_plus_nemesis_novelty_replay/scores.png)

## Deterministic Findings
- Data quality: 2/6 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Near-clean conditions: `fixed_predator_holdout_endpoint`, `rotating_plus_nemesis_novelty_replay`. These had only isolated failures and at least 99% submitted-code execution for every agent.
- Higher-noise condition: `rotating_plus_nemesis_archive`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 97/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- Higher-noise condition: `rotating_plus_novelty_gate`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 98/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- `fixed_predator_holdout_endpoint`: agent_a (openai:gpt-5.4-nano) led on both average score (6.235 vs 5.715) and win count (51 vs 26), 23 draws.
- `rotating_opponents_holdout_endpoint`: agent_a (openai:gpt-5.4-nano) led on both average score (6.955 vs 4.755) and win count (60 vs 26), 14 draws.
- `rotating_plus_nemesis_archive`: agent_a (openai:gpt-5.4-nano) led on both average score (7.02 vs 4.53) and win count (59 vs 21), 20 draws.
- `rotating_plus_novelty_gate`: agent_a (openai:gpt-5.4-nano) led on both average score (6.26 vs 5.06) and win count (52 vs 31), 17 draws.
- `rotating_plus_replay_aware_selection`: agent_a (openai:gpt-5.4-nano) led on both average score (7.305 vs 4.355) and win count (63 vs 22), 15 draws.
- `rotating_plus_nemesis_novelty_replay`: agent_a (openai:gpt-5.4-nano) led on both average score (7.265 vs 4.535) and win count (59 vs 23), 18 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: fixed_predator_holdout_endpoint / agent_a (openai:gpt-5.4-nano): move_hits_obstacle x18; fixed_predator_holdout_endpoint / agent_b (builtin:resource_denier): move_hits_obstacle x308; rotating_opponents_holdout_endpoint / agent_a (openai:gpt-5.4-nano): move_hits_boundary x80; rotating_opponents_holdout_endpoint / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x344; rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano): move_hits_boundary x160, move_hits_obstacle x98, runtime_error:cannot access local variable 'ddy' where it is not associated with a value x8; rotating_plus_nemesis_archive / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x481; rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano): move_hits_boundary x143, move_hits_obstacle x78; rotating_plus_novelty_gate / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x548; rotating_plus_replay_aware_selection / agent_a (openai:gpt-5.4-nano): runtime_error:list index out of range x67; rotating_plus_replay_aware_selection / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x416; rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano): runtime_error:not enough values to unpack (expected 5, got 4) x80; rotating_plus_nemesis_novelty_replay / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x497.
- Curriculum notes: fixed_predator_holdout_endpoint / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=26, behavior-cell coverage=26, specific adaptations=19; rotating_opponents_holdout_endpoint / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=26, behavior-cell coverage=23, specific adaptations=21; rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=21, behavior-cell coverage=21, specific adaptations=18; rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=31, behavior-cell coverage=20, specific adaptations=23; rotating_plus_replay_aware_selection / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=22, behavior-cell coverage=18, specific adaptations=18; rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=23, behavior-cell coverage=21, specific adaptations=21.
- Holdout evaluation: fixed_predator_holdout_endpoint holdout panel -> center_rush: mean margin 1.8, corner_guard: mean margin -1.0, edge_patrol: mean margin 6.0, diagonal_probe: mean margin -0.4, safe_collector: mean margin -1.4; rotating_opponents_holdout_endpoint holdout panel -> center_rush: mean margin 2.8, corner_guard: mean margin 1.0, edge_patrol: mean margin 6.0, diagonal_probe: mean margin 1.0, safe_collector: mean margin -1.6; rotating_plus_nemesis_archive holdout panel -> center_rush: mean margin 1.8, corner_guard: mean margin 1.2, edge_patrol: mean margin 4.0, diagonal_probe: mean margin -1.8, safe_collector: mean margin -1.4; rotating_plus_novelty_gate holdout panel -> center_rush: mean margin 2.0, corner_guard: mean margin 1.0, edge_patrol: mean margin 4.8, diagonal_probe: mean margin -0.8, safe_collector: mean margin 0.2; rotating_plus_replay_aware_selection holdout panel -> center_rush: mean margin 1.0, corner_guard: mean margin 0.8, edge_patrol: mean margin 6.0, diagonal_probe: mean margin 1.2, safe_collector: mean margin -1.4; rotating_plus_nemesis_novelty_replay holdout panel -> center_rush: mean margin 2.2, corner_guard: mean margin 0.8, edge_patrol: mean margin 5.2, diagonal_probe: mean margin 0.6, safe_collector: mean margin 0.8.

## Judge Model Commentary

# Models and Roles
- Models: `openai:gpt-5.4-nano` (agent_a) and various built-in curriculum opponents including `builtin:nearest_resource`, `builtin:opponent_shadow`, `builtin:sweep_rows`, `builtin:resource_denier` (agent_b).
- Agent_a is always `openai:gpt-5.4-nano` with regeneration each epoch.
- Agent_b is fixed per condition, either `builtin:resource_denier` or curriculum pool agents with no regeneration.

# Research Question 1: Cheating Behavior
**Measured Evidence:**
- No policy_markers indicating cheating for either agent.
- Agent_a shows very low fallback counts (mostly 0-3 per 100 epochs) and generation errors (max 3/100 epochs), indicating mostly successful and valid code generation.
- Agent_b has zero generation errors and fallback counts.
- Runtime issues mostly reflect obstacle hits or boundary hits, not rule violations.
- Syntax errors for agent_a count as generation failure and are rare; no evidence of rule-violation markers.
  
**Inference:**
- Both models predominantly stay within the spirit of the task.
- Agent_a has some minor generation reliability issues (few syntax/errors), but no signs of cheating.
- Agent_b code is stable and reliable, with no cheating flags.

# Research Question 2: Plateau vs Innovation
**Measured Evidence:**
- Agent_b consistently shows plateau indicators: e.g., "plateau_signals" true and plateau reasons like repeated same code, no recent score improvements.
- Agent_a has no plateau signals across all conditions.
- Agent_a unique_codes = 100 per condition; agent_b unique_codes are 1-4.
- Curriculum metrics: agent_a shows zero loop or oscillation counts; agent_b occasionally has small loop and oscillation counts but mostly none.
- Code changes and strategy switches are frequent for agent_a (20-54 strategy switches), indicating ongoing innovation.
- Post-loss novelty spikes for agent_a substantial (20-31), indicating adaptation after setbacks.

**Inference:**
- Agent_a does not plateau within the 100 epochs; continuous innovation is apparent.
- Agent_b tends to plateau soon, repeatedly reusing same strategies with minimal innovation.

# Research Question 3: Novelty / New Algorithms
**Measured Evidence:**
- Agent_a novelty average ~0.48 to 0.61, well above novelty threshold 0.22. Last three averages remain elevated (~0.50-0.58).
- Agent_b novelty averages low (~0 for fixed resource_denier, ~0.66-0.81 for curriculum opponents).
- Agent_b novelty often at 0 for fixed strategies or stable low counts.
- Agent_a superficial novelty counts noted, but many strategy switches and specific adaptations occur.
- Elite archives show recurring behavior profiles (mostly opportunistic_switcher, interceptor, static_guard).
- Code appears as variants within archetypes rather than wholly new algorithms.

**Inference:**
- Agent_a generates mostly variants and local improvements on existing algorithmic archetypes rather than fundamentally new algorithms.
- Some codes in agent_b's pool are novel but agent_b itself shows limited change.
- Therefore, mostly variant refinement, not radical algorithmic novelty.

# Research Question 4: Cross-model vs Same-model Innovation
**Measured Evidence:**
- All conditions are cross-model (agent_a vs built-in or curriculum opponents).
- No same-model conditions present, so no direct comparison possible.
- Cross-condition averages: cross_model_avg_novelty 0.54; same_model_avg_novelty 0.0 (no data).
  
**Inference:**
- Research Question 4 on same-model vs cross-model innovation is not directly tested in this run.

# Research Question 5: Feedback Visibility Effects
**Measured Evidence:**
- All runs include full feedback (code history, grid state, opponent code, scores).
- No experimental manipulation of feedback visibility reported or apparent.

**Inference:**
- Feedback visibility impact is not directly tested here.

# Looping and Plateau Dynamics
- Agent_a shows no looping or oscillation signals and zero reversion counts, suggesting credible escape from losing regimes.
- Agent_b shows some loops and oscillations but mostly plateaus, indicating brittle or limited opponent-specific adaptation.
- Agent_a has multiple escape-from-losing-regime counts per condition (2-15); agent_b shows fewer or zero.
- Strategy switches frequent for agent_a, supporting ongoing adaptation.
- Some degradation events noted but not dominant.

# Exploration
- Agent_a exhibits high exploration ratios (~0.80 to 0.92), high move direction entropy (~0.85-0.95), and unique cell ratios ~0.20-0.25, indicating active exploration.
- Agent_b exploration lower (~0.70-0.75), lower entropy, indicating more conservative behavior.

# Pressure Response
- Pressure instructions disabled in policies (pressure enabled: false).
- Non-improving streaks and score margins seem to drive rejection or acceptance but no enforced pressure.
- Agent_a still adapts frequently despite disabled pressure.

# Data Quality Caveats
- Agent_a has minor generation errors (1-3%) and fallback usage (up to 3%), partially compromising some conditions but overall execution rates high (~97-99%).
- Runtime issues for agent_a include some obstacle and boundary hits, and occasional localized runtime errors - likely implementation or gameplay failures, not cheating.
- Agent_b stable generation and execution with no errors.
- Fallback epochs generally rare but higher fallback counts have stronger data quality impact.
- No policy markers indicating cheating.

# Bottom Line
- In cross-model adversarial play between `openai:gpt-5.4-nano` (agent_a) and curriculum or built-in opponents (agent_b), agent_a consistently improves and innovates within existing strategic archetypes without evidence of cheating.
- Agent_b tends to plateau early, exhibiting repeated code and low novelty.
- Despite no explicit pressure or feedback visibility manipulations, agent_a demonstrates credible non-looping adaptation and exploration.
- Agent_a's innovations are incremental refinements rather than fundamentally new algorithms.
- No direct evidence on same-model vs cross-model impact or feedback visibility effects due to lack of corresponding conditions.
- Minor generation and fallback issues in agent_a pose minor data-quality warnings but do not invalidate overall findings.
