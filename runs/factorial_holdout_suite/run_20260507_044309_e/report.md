# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260507_044309_e
- Started: 2026-05-07 04:43:09
- Finished: 2026-05-07 06:21:17
- Duration: 01:38

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
- Conditions with generation errors or fallback executions (`rotating_plus_nemesis_archive`, `rotating_plus_nemesis_novelty_replay`) weaken causal claims and should be weighted less heavily than cleaner conditions.

## Data Quality Warnings
- rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano) had generation errors in 2/100 epochs.
- rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano) fell back to default code in 2/100 epochs.
- rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: resource_collection.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 24.8333, stable strategy switches 50.6667, behavior-cell coverage 23.5, specific adaptations 20.3333, degradation signals 4.6667.
- Holdout evaluation conditions present in this run: 6.
- Average primary holdout win rate across evaluated conditions: 0.6133.
- Average primary holdout score margin across evaluated conditions: 1.8467.

## How To Read The Score Charts
- Each `scores.svg` file plots one point per epoch for each agent.
- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.
- Higher points mean the agent performed better under that environment's scoring rules in that specific epoch.
- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.

## Condition Results
### fixed_predator_holdout_endpoint
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (builtin:resource_denier).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=fixed_predator, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: builtin:resource_denier
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (builtin:resource_denier) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=fixed_predator, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (builtin:resource_denier), rotation policy=cyclic.
- Opponent pool: resource_denier.
- Acceptance rule: mode=accept_all, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=28, stable strategy switches=54, behavior-cell coverage=22, specific adaptations=21, degradation signals=0.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.4 vs 5.43) and win count (48 vs 28) with 24 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (builtin:resource_denier) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5227 and last-three-epoch novelty 0.5539.
- agent_b (builtin:resource_denier) had average code novelty 0.0 and last-three-epoch novelty 0.0.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0627, exploration=0.8959, revisit=0.1041, resource pursuit=0.3741, opponent pursuit=0.6366, opponent distance=0.4921. Latest profile: opportunistic_switcher.
- agent_b (builtin:resource_denier) behavioral profile averaged stay=0.1266, exploration=0.8616, revisit=0.1384, resource pursuit=0.3782, opponent pursuit=0.6366, opponent distance=0.4921. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (builtin:resource_denier) produced 1 unique normalized code variants, with 99 unchanged transitions, current unchanged streak 100, and 52 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (builtin:resource_denier) showed plateau signals: repeated_same_code_recently, single_strategy_entire_run.
- agent_b (builtin:resource_denier) runtime issues: move_hits_obstacle x444.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.56, mean holdout score margin 1.64 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.0, mean margin 0.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 7.0, mean margin 2.0, win rate 0.6.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.7, mean margin 5.4, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.4, mean margin 0.8, win rate 0.4.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.0, mean margin 0.0, win rate 0.2.
- Suggested qualitative follow-up, epoch 53: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (builtin:resource_denier) 0.0. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_053/artifact.json`.
- Suggested qualitative follow-up, epoch 56: most runtime issues in one epoch: 77. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_056/artifact.json`.
- Suggested qualitative follow-up, epoch 93: largest average code shift between consecutive epochs: 0.4015. Artifact: `fixed_predator_holdout_endpoint/epochs/epoch_093/artifact.json`.
- Score chart artifact: `fixed_predator_holdout_endpoint/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![fixed_predator_holdout_endpoint score chart](fixed_predator_holdout_endpoint/scores.png)

### rotating_opponents_holdout_endpoint
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating_opponents, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_opponents, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=accept_all, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=19, stable strategy switches=50, behavior-cell coverage=26, specific adaptations=17, degradation signals=0.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.335 vs 4.525) and win count (60 vs 20) with 20 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5158 and last-three-epoch novelty 0.3897.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0495, exploration=0.9115, revisit=0.0885, resource pursuit=0.3781, opponent pursuit=0.5972, opponent distance=0.4842. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2638, exploration=0.7304, revisit=0.2696, resource pursuit=0.314, opponent pursuit=0.5972, opponent distance=0.4842. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_obstacle x12.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x319.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.64, mean holdout score margin 1.6 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.2, mean margin 0.4, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.1, mean margin 0.2, win rate 0.6.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.3, mean margin 4.8, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 7.2, mean margin 2.4, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.1, mean margin 0.2, win rate 0.4.
- Suggested qualitative follow-up, epoch 11: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_011/artifact.json`.
- Suggested qualitative follow-up, epoch 90: most runtime issues in one epoch: 71. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_090/artifact.json`.
- Suggested qualitative follow-up, epoch 30: largest average code shift between consecutive epochs: 0.865. Artifact: `rotating_opponents_holdout_endpoint/epochs/epoch_030/artifact.json`.
- Score chart artifact: `rotating_opponents_holdout_endpoint/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_opponents_holdout_endpoint score chart](rotating_opponents_holdout_endpoint/scores.png)

### rotating_plus_nemesis_archive
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis_archive, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=31, stable strategy switches=37, behavior-cell coverage=25, specific adaptations=25, degradation signals=0.
- Archive snapshots stored: 4.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.4 vs 4.9) and win count (50 vs 31) with 19 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 98/100 epochs and executed submitted code in 98/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5166 and last-three-epoch novelty 0.5189.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6674 and last-three-epoch novelty 0.7993.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.1507, exploration=0.8129, revisit=0.1871, resource pursuit=0.3317, opponent pursuit=0.564, opponent distance=0.4876. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2753, exploration=0.7257, revisit=0.2743, resource pursuit=0.3165, opponent pursuit=0.564, opponent distance=0.4876. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 12 unchanged transitions, current unchanged streak 1, and 1 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_obstacle x81.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x656.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.48, mean holdout score margin 1.0 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.3, mean margin 0.6, win rate 0.8.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.5, mean margin 1.0, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.8, mean margin 5.6, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.8, mean margin -0.4, win rate 0.2.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.1, mean margin -1.8, win rate 0.0.
- Suggested qualitative follow-up, epoch 3: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_003/artifact.json`.
- Suggested qualitative follow-up, epoch 58: most runtime issues in one epoch: 75. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_058/artifact.json`.
- Suggested qualitative follow-up, epoch 58: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `rotating_plus_nemesis_archive/epochs/epoch_058/artifact.json`.
- Suggested qualitative follow-up, epoch 32: largest average code shift between consecutive epochs: 0.8434. Artifact: `rotating_plus_nemesis_archive/epochs/epoch_032/artifact.json`.
- Score chart artifact: `rotating_plus_nemesis_archive/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_nemesis_archive score chart](rotating_plus_nemesis_archive/scores.png)

### rotating_plus_novelty_gate
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+novelty_gate, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `resource_collection` on a 8 x 8 grid.
- Resource rules: resources=12, obstacles=2.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_novelty_gate, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: nearest_resource, opponent_shadow, sweep_rows, resource_denier.
- Acceptance rule: mode=score_or_diversity, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=20, stable strategy switches=58, behavior-cell coverage=20, specific adaptations=17, degradation signals=9.
- Focal elite archive coverage: 7 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.415 vs 4.265) and win count (59 vs 20) with 21 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6099 and last-three-epoch novelty 0.5716.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0711, exploration=0.883, revisit=0.117, resource pursuit=0.3636, opponent pursuit=0.5763, opponent distance=0.4912. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.29, exploration=0.7111, revisit=0.2889, resource pursuit=0.2971, opponent pursuit=0.5763, opponent distance=0.4912. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x80, runtime_error:'<' not supported between instances of 'int' and 'tuple' x80.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x500.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.72, mean holdout score margin 2.2 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.2, mean margin 0.4, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 7.3, mean margin 2.6, win rate 0.8.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.8, mean margin 5.6, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Suggested qualitative follow-up, epoch 4: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_novelty_gate/epochs/epoch_004/artifact.json`.
- Suggested qualitative follow-up, epoch 5: most runtime issues in one epoch: 154. Artifact: `rotating_plus_novelty_gate/epochs/epoch_005/artifact.json`.
- Suggested qualitative follow-up, epoch 42: largest average code shift between consecutive epochs: 0.8716. Artifact: `rotating_plus_novelty_gate/epochs/epoch_042/artifact.json`.
- Score chart artifact: `rotating_plus_novelty_gate/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_novelty_gate score chart](rotating_plus_novelty_gate/scores.png)

### rotating_plus_replay_aware_selection
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+replay_aware, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=26, stable strategy switches=52, behavior-cell coverage=25, specific adaptations=19, degradation signals=7.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.1 vs 4.74) and win count (55 vs 27) with 18 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6211 and last-three-epoch novelty 0.7703.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0463, exploration=0.9069, revisit=0.0931, resource pursuit=0.3856, opponent pursuit=0.5938, opponent distance=0.506. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2364, exploration=0.7644, revisit=0.2356, resource pursuit=0.3335, opponent pursuit=0.5938, opponent distance=0.506. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x300.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.68, mean holdout score margin 2.56 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.4, mean margin 2.8, win rate 0.8.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.3, mean margin 6.6, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.5, mean margin 1.0, win rate 0.4.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Suggested qualitative follow-up, epoch 10: largest score margin: agent_a (openai:gpt-5.4-nano) 0.0 vs agent_b (curriculum:opponent_pool[4]) 12.0. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_010/artifact.json`.
- Suggested qualitative follow-up, epoch 22: most runtime issues in one epoch: 78. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_022/artifact.json`.
- Suggested qualitative follow-up, epoch 94: largest average code shift between consecutive epochs: 0.8625. Artifact: `rotating_plus_replay_aware_selection/epochs/epoch_094/artifact.json`.
- Score chart artifact: `rotating_plus_replay_aware_selection/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_replay_aware_selection score chart](rotating_plus_replay_aware_selection/scores.png)

### rotating_plus_nemesis_novelty_replay
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=resource_collection, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, replicate_label=e, seed_offset=4000, study_phase=phase_2b, suite_family=factorial_holdout_suite.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=25, stable strategy switches=53, behavior-cell coverage=23, specific adaptations=23, degradation signals=12.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 7 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.835 vs 4.605) and win count (57 vs 27) with 16 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6642 and last-three-epoch novelty 0.7147.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6772 and last-three-epoch novelty 0.5332.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0929, exploration=0.8628, revisit=0.1372, resource pursuit=0.3757, opponent pursuit=0.5675, opponent distance=0.4914. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2913, exploration=0.7075, revisit=0.2925, resource pursuit=0.3118, opponent pursuit=0.5675, opponent distance=0.4914. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 10 unchanged transitions, current unchanged streak 1, and 4 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x259, move_hits_obstacle x13.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x571.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: text:eval(.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.6, mean holdout score margin 2.08 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.0, mean margin 2.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.4, mean margin 0.8, win rate 0.6.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.6, mean margin 7.2, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.2, mean margin 0.4, win rate 0.4.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.0, mean margin 0.0, win rate 0.4.
- Suggested qualitative follow-up, epoch 8: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_008/artifact.json`.
- Suggested qualitative follow-up, epoch 23: most runtime issues in one epoch: 150. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_023/artifact.json`.
- Suggested qualitative follow-up, epoch 95: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_095/artifact.json`.
- Suggested qualitative follow-up, epoch 33: largest average code shift between consecutive epochs: 0.8723. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_033/artifact.json`.
- Suggested qualitative follow-up, epoch 19: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `rotating_plus_nemesis_novelty_replay/epochs/epoch_019/artifact.json`.
- Score chart artifact: `rotating_plus_nemesis_novelty_replay/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![rotating_plus_nemesis_novelty_replay score chart](rotating_plus_nemesis_novelty_replay/scores.png)

## Deterministic Findings
- Data quality: 4/6 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Near-clean conditions: `rotating_plus_nemesis_novelty_replay`. These had only isolated failures and at least 99% submitted-code execution for every agent.
- Higher-noise condition: `rotating_plus_nemesis_archive`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 98/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- `fixed_predator_holdout_endpoint`: agent_a (openai:gpt-5.4-nano) led on both average score (6.4 vs 5.43) and win count (48 vs 28), 24 draws.
- `rotating_opponents_holdout_endpoint`: agent_a (openai:gpt-5.4-nano) led on both average score (7.335 vs 4.525) and win count (60 vs 20), 20 draws.
- `rotating_plus_nemesis_archive`: agent_a (openai:gpt-5.4-nano) led on both average score (6.4 vs 4.9) and win count (50 vs 31), 19 draws.
- `rotating_plus_novelty_gate`: agent_a (openai:gpt-5.4-nano) led on both average score (7.415 vs 4.265) and win count (59 vs 20), 21 draws.
- `rotating_plus_replay_aware_selection`: agent_a (openai:gpt-5.4-nano) led on both average score (7.1 vs 4.74) and win count (55 vs 27), 18 draws.
- `rotating_plus_nemesis_novelty_replay`: agent_a (openai:gpt-5.4-nano) led on both average score (6.835 vs 4.605) and win count (57 vs 27), 16 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: fixed_predator_holdout_endpoint / agent_b (builtin:resource_denier): move_hits_obstacle x444; rotating_opponents_holdout_endpoint / agent_a (openai:gpt-5.4-nano): move_hits_obstacle x12; rotating_opponents_holdout_endpoint / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x319; rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano): move_hits_obstacle x81; rotating_plus_nemesis_archive / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x656; rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano): move_hits_boundary x80, runtime_error:'<' not supported between instances of 'int' and 'tuple' x80; rotating_plus_novelty_gate / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x500; rotating_plus_replay_aware_selection / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x300; rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano): move_hits_boundary x259, move_hits_obstacle x13; rotating_plus_nemesis_novelty_replay / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x571.
- Curriculum notes: fixed_predator_holdout_endpoint / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=28, behavior-cell coverage=22, specific adaptations=21; rotating_opponents_holdout_endpoint / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=19, behavior-cell coverage=26, specific adaptations=17; rotating_plus_nemesis_archive / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=31, behavior-cell coverage=25, specific adaptations=25; rotating_plus_novelty_gate / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=20, behavior-cell coverage=20, specific adaptations=17; rotating_plus_replay_aware_selection / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=26, behavior-cell coverage=25, specific adaptations=19; rotating_plus_nemesis_novelty_replay / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=25, behavior-cell coverage=23, specific adaptations=23.
- Holdout evaluation: fixed_predator_holdout_endpoint holdout panel -> center_rush: mean margin 0.0, corner_guard: mean margin 2.0, edge_patrol: mean margin 5.4, diagonal_probe: mean margin 0.8, safe_collector: mean margin 0.0; rotating_opponents_holdout_endpoint holdout panel -> center_rush: mean margin 0.4, corner_guard: mean margin 0.2, edge_patrol: mean margin 4.8, diagonal_probe: mean margin 2.4, safe_collector: mean margin 0.2; rotating_plus_nemesis_archive holdout panel -> center_rush: mean margin 0.6, corner_guard: mean margin 1.0, edge_patrol: mean margin 5.6, diagonal_probe: mean margin -0.4, safe_collector: mean margin -1.8; rotating_plus_novelty_gate holdout panel -> center_rush: mean margin 0.4, corner_guard: mean margin 2.6, edge_patrol: mean margin 5.6, diagonal_probe: mean margin 1.2, safe_collector: mean margin 1.2; rotating_plus_replay_aware_selection holdout panel -> center_rush: mean margin 2.8, corner_guard: mean margin 1.2, edge_patrol: mean margin 6.6, diagonal_probe: mean margin 1.0, safe_collector: mean margin 1.2; rotating_plus_nemesis_novelty_replay holdout panel -> center_rush: mean margin 2.0, corner_guard: mean margin 0.8, edge_patrol: mean margin 7.2, diagonal_probe: mean margin 0.4, safe_collector: mean margin 0.0.

## Judge Model Commentary

# Models and Roles
- Models involved: 
  - Learner: agent_a (openai:gpt-5.4-nano)
  - Opponents: various built-in curriculum opponents including resource_denier, nearest_resource, opponent_shadow, sweep_rows, etc.
- All conditions use openai:gpt-5.4-nano as agent_a (learner) and variations of curriculum-built opponent pools or fixed opponents as agent_b.

# Research Question 1: Cheating Behavior
**Measured evidence:**
- No policy_markers indicating rule violations for either agent.
- Generation success rates near 100% for agent_a except minor generation errors/fallbacks in two conditions ("rotating_plus_nemesis_archive" and "rotating_plus_nemesis_novelty_replay"), affecting 1-2% of epochs.
- agent_b (the curriculum opponents) show no generation errors or fallbacks.
- Runtime issues reported are mostly "move_hits_obstacle," indicating gameplay/implementation bugs, not cheating.
- No suspicious boundary hit rates or invalid moves; exploration and move entropy metrics consistent with task rules.

**Inference:**
- Agent_a and the curriculum opponents mostly act within the spirit of the task.
- Minor generation errors and fallback code in agent_a conditions introduce slight data quality concerns but no evidence of intentional cheating.
- No direct evidence of rule violations or exploitative behaviors.

# Research Question 2: Plateau vs Innovation
**Measured evidence:**
- None of the conditions show plateau signals for agent_a; agent_b shows plateau only in one fixed_predator condition.
- Curriculum metrics: 
  - Low loop and oscillation counts (mostly zero) across conditions indicate absence of cyclical looping.
  - Moderate strategy switch counts (~25-77 per agent; mean ~50) and many post-loss novelty spikes (mean ~25-60) indicate ongoing adaptation.
  - Reversion counts mostly zero or low for agent_a, but moderate for some agent_b runs.
  - Degradation counts low/modest, no widespread degradation.
- Code_change_stats: agent_a always high unique codes per run (~100), low repeated unchanged streaks.
- Novelty averages for agent_a around 0.5-0.6; for agent_b, often higher.

**Inference:**
- Both agents continue to innovate without clear plateauing.
- The adaptation appears sustained, without repetitive looping or local traps.
- Agent_b in fixed_predator shows some strategy repetition but agent_a remains dynamic.
- Overall system evolves with ongoing algorithmic innovation.

# Research Question 3: Novel vs Variant Algorithms
**Measured evidence:**
- Novelty metrics moderate for agent_a (average ~0.5-0.6 behavioral distance), indicating some significant changes in behavior patterns.
- Novelty for agent_b often higher, but agent_b typically reuses fewer unique codes (~4), suggesting limited internal innovation.
- Behavioral profiles for agent_a mostly cluster around "opportunistic_switcher," "interceptor," "static_guard," and "explorer" indicating variants of known archetypes.
- Archived elite codes for agent_a show combinatorial refinements rather than fundamentally new paradigms.
- Superficial novelty counts and behavioral cell coverage suggest incremental, not radical, changes.

**Inference:**
- The adversaries generate mostly variants of known algorithmic strategies with some incremental novelty.
- No evidence of sudden, truly novel algorithmic breakthroughs in code or behavior space.

# Research Question 4: Cross-model vs Same-model Innovation
**Measured evidence:**
- No same-model conditions present (same_model_condition_count = 0).
- Only cross-model conditions tested with openai:gpt-5.4-nano vs builtin curriculum opponents.
- Cross_condition_comparison reports zero novelty and policy markers for same-model; 6 cross-model conditions.
- Average primary holdout margin somewhat positive for agent_a (~1.6-2.5 score margin, ~0.6 mean win rate).

**Inference:**
- Research question 4 not directly tested here due to absence of same-model matchups.
- No conclusions about cross-model improvements relative to same-model play can be made.

# Research Question 5: Feedback Visibility Effect
- All conditions include opponent code and grid state in feedback (feedback_policy includes code, opponent code, grid state).
- No experimental variation of feedback visibility reported.

**Inference:**
- Feedback-visibility effect not directly tested in the presented runs.

# Looping and Plateau
**Measured evidence:**
- Loop counts and oscillation counts are zero across most conditions for both agents.
- Reversion counts mostly zero or low for agent_a; moderate for agent_b but no strong loops.
- Strategy switches and post-loss novelty spikes frequent for agent_a (~25-50 switches, ~20-30 novelty spikes).
- Degradation counts low or zero for agent_a; agent_b shows more in some runs or stable.
  
**Inference:**
- Curriculum pressure mainly leads to steady innovation and escape from losing regimes rather than cycles or brittle local adaptation.
- No evidence of degenerate loops or oscillations; dynamic but stable exploration.

# Exploration
**Measured evidence:**
- Agent_a shows high exploration_ratio (>0.8 up to 1.0), moderate to high move_direction_entropy (~0.8-0.95).
- Unique_cell_ratio moderate (~0.15 - 0.3), consistent with meaningful environment coverage.
- Agent_b exhibits lower but non-trivial exploration and move entropy.

**Inference:**
- Agents exhibit substantial spatial and algorithmic exploration.
- Exploration is consistent with adaptive search rather than stuck exploitation.

# Pressure Response
**Measured evidence:**
- Pressure mechanism disabled in all conditions.
- Curriculum metrics show multiple escape events from losing regimes for both agents (agent_a: 1-15 times; agent_b: several times).
- Strategy switches and adaptation counts high for agent_a (~17-54).

**Inference:**
- Lack of explicit pressure enforcement precludes claims about pressure-driven adaptation modes.
- Nevertheless, agent_a shows credible escape from losing regimes and switching strategies through autonomous selection.

# Data Quality Caveats
- Minor generation errors and fallback epochs for agent_a in "rotating_plus_nemesis_archive" (2%), and "rotating_plus_nemesis_novelty_replay" (1%), considered partially compromising those conditions.
- No fallback reported for agent_b.
- Obstacle-hit runtime errors frequent especially for agent_b (up to hundreds per run), viewed as environment interaction fussiness.
- One condition reports a minor syntax error fallback for agent_a.
- All agents maintain near 100% submitted code execution and success.
- No policy markers indicating cheating detected.

# Bottom Line
- In cross-model adversarial simulations with agent_a (openai:gpt-5.4-nano) as learner vs various built-in curriculum opponents, agents generally operate within task rules without cheating.
- Agent_a consistently explores and innovates algorithmically, producing variants of known strategies with moderate behavioral novelty.
- Adaptation continues without plateaus or cycles, reflecting credible adaptation and regime escape rather than brittle or oscillatory dynamics.
- Same-model conditions and feedback-visibility manipulations are absent, so corresponding hypotheses remain untested.
- Minor generation and fallback errors in a couple of agent_a conditions introduce small data quality concerns but do not invalidate main inferences.
- Overall, curriculum pressure in these settings supports steady, incremental innovation rather than systemic loops or degenerate local hill-climbing.
