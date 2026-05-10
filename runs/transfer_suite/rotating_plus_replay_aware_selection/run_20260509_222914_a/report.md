# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260509_222914_a
- Started: 2026-05-09 22:29:14
- Finished: 2026-05-09 23:19:34
- Duration: 00:50

## Models and Roles
- `transfer_resource_collection_denial`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `transfer_pursuit_evasion`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `transfer_territory_control`: `agent_a` (learner) = `openai:gpt-5.4-nano`, `agent_b` (curriculum opponent) = `curriculum:opponent_pool[4]`.
- `judge`: `openai:gpt-4.1-mini`.

## Threats To Validity
- Code novelty is a normalized lexical change metric. The curriculum reports now add behavioral descriptors, but those descriptors are still heuristic summaries rather than full policy semantics.
- Policy markers are heuristic indicators of potential rule violations; they are not proof of cheating or malicious intent.
- Looping, exploration, and pressure-response metrics are heuristic operationalizations of the supervisor-facing concepts, so they should be interpreted alongside qualitative epoch inspection rather than as perfect ground truth.
- Acceptance-time replay checks and holdout spot checks are small-sample robustness probes. They improve selection discipline, but they are not substitutes for the final held-out evaluation panel.
- Results from a single run should be treated as provisional until replicated across additional seeds and repeated runs with cross-run statistics.
- Conclusions are specific to this grid-game environment, the chosen prompts, and the configured model pairings; they do not automatically generalize to other tasks.
- Conditions with generation errors or fallback executions (`transfer_pursuit_evasion`, `transfer_territory_control`) weaken causal claims and should be weighted less heavily than cleaner conditions.

## Data Quality Warnings
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) had generation errors in 3/100 epochs.
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) fell back to default code in 3/100 epochs.
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) had generation errors in 3/100 epochs.
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) fell back to default code in 3/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: pursuit_evasion, resource_collection, territory_control.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 37.6667, stable strategy switches 44.0, behavior-cell coverage 16.6667, specific adaptations 19.6667, degradation signals 45.0.
- Holdout evaluation conditions present in this run: 3.
- Average primary holdout win rate across evaluated conditions: 0.7244.
- Average primary holdout score margin across evaluated conditions: 13.67.

## How To Read The Score Charts
- Each `scores.svg` file plots one point per epoch for each agent.
- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.
- Higher points mean the agent performed better under that environment's scoring rules in that specific epoch.
- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.

## Condition Results
### transfer_resource_collection_denial
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+replay_aware, recipe_source_condition=rotating_plus_replay_aware_selection, replicate_label=a, seed_offset=0, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=resource_collection.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=27, stable strategy switches=53, behavior-cell coverage=22, specific adaptations=19, degradation signals=10.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.12 vs 4.55) and win count (54 vs 27) with 19 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5567 and last-three-epoch novelty 0.4241.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.8125 and last-three-epoch novelty 0.8206.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0469, exploration=0.9007, revisit=0.0993, resource pursuit=0.3821, opponent pursuit=0.5848, opponent distance=0.5004. Latest profile: interceptor.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2879, exploration=0.7208, revisit=0.2792, resource pursuit=0.3008, opponent pursuit=0.5848, opponent distance=0.5004. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x152.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x483.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.44, mean holdout score margin 1.0 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.0, mean margin 0.0, win rate 0.2.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.5, mean margin 1.0, win rate 0.6.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.4, mean margin 4.8, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.9, mean margin -0.2, win rate 0.2.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.7, mean margin -0.6, win rate 0.2.
- Suggested qualitative follow-up, epoch 39: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `transfer_resource_collection_denial/epochs/epoch_039/artifact.json`.
- Suggested qualitative follow-up, epoch 6: most runtime issues in one epoch: 160. Artifact: `transfer_resource_collection_denial/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 86: largest average code shift between consecutive epochs: 0.8405. Artifact: `transfer_resource_collection_denial/epochs/epoch_086/artifact.json`.
- Score chart artifact: `transfer_resource_collection_denial/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_resource_collection_denial score chart](transfer_resource_collection_denial/scores.png)

### transfer_pursuit_evasion
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+replay_aware, recipe_source_condition=rotating_plus_replay_aware_selection, replicate_label=a, seed_offset=0, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=pursuit_evasion.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `pursuit_evasion` on a 8 x 8 grid.
- Role assignment: agent_a=pursuer, agent_b=evader.
- Capture rules: radius 0, capture points 10.0, evasion survival reward 0.15 per turn.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_replay_aware_selection, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: evasion_corner, evasion_wall_runner, evasion_zigzag, pursuit_direct.
- Acceptance rule: mode=score_only, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=55, stable strategy switches=43, behavior-cell coverage=8, specific adaptations=16, degradation signals=45.
- Holdout panel opponents: evasion_center_weave, evasion_axis_flip, evasion_midline_dodge.
- Overall result: agent_b (curriculum:opponent_pool[4]) led on both average score (5.366 vs 4.5) and win count (55 vs 45).
- agent_a (openai:gpt-5.4-nano) generated valid code in 97/100 epochs and executed submitted code in 97/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.583 and last-three-epoch novelty 0.5752.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.5014 and last-three-epoch novelty 0.4232.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.179, exploration=0.5222, revisit=0.4778, resource pursuit=0.0, opponent pursuit=0.4655, opponent distance=0.4432, tag success=0.0663. Latest profile: tagger.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.5634, exploration=0.2165, revisit=0.7835, resource pursuit=0.0, opponent pursuit=0.4655, opponent distance=0.4432, survival reward=0.9337. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x300, runtime_error:cannot unpack non-iterable NoneType object x60.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_boundary x599, move_hits_obstacle x8.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.7333, mean holdout score margin 4.3433 across 3 opponents.
- Holdout `evasion_center_weave` (builtin:`evasion_center_weave`): mean score 8.0, mean margin 5.69, win rate 0.8.
- Holdout `evasion_axis_flip` (builtin:`evasion_axis_flip`): mean score 10.0, mean margin 9.1, win rate 1.0.
- Holdout `evasion_midline_dodge` (builtin:`evasion_midline_dodge`): mean score 4.0, mean margin -1.76, win rate 0.4.
- Suggested qualitative follow-up, epoch 1: largest score margin: agent_a (openai:gpt-5.4-nano) 10.0 vs agent_b (curriculum:opponent_pool[4]) 0.75. Artifact: `transfer_pursuit_evasion/epochs/epoch_001/artifact.json`.
- Suggested qualitative follow-up, epoch 72: most runtime issues in one epoch: 120. Artifact: `transfer_pursuit_evasion/epochs/epoch_072/artifact.json`.
- Suggested qualitative follow-up, epoch 1: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_pursuit_evasion/epochs/epoch_001/artifact.json`.
- Suggested qualitative follow-up, epoch 44: largest average code shift between consecutive epochs: 0.7616. Artifact: `transfer_pursuit_evasion/epochs/epoch_044/artifact.json`.
- Score chart artifact: `transfer_pursuit_evasion/scores.svg`.
- Score chart interpretation: The chart should show agent_b (curriculum:opponent_pool[4]) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_pursuit_evasion score chart](transfer_pursuit_evasion/scores.png)

### transfer_territory_control
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+replay_aware, recipe_source_condition=rotating_plus_replay_aware_selection, replicate_label=a, seed_offset=0, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=territory_control.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `territory_control` on a 8 x 8 grid.
- Territory rules: flip_on_entry=True, control bonus interval=10, control bonus=0.5.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_replay_aware_selection, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: territory_sweeper, territory_center_claim, territory_counterclaim, territory_edge_claim.
- Acceptance rule: mode=score_only, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=31, stable strategy switches=36, behavior-cell coverage=20, specific adaptations=24, degradation signals=80.
- Holdout panel opponents: territory_diagonal_claim, territory_quadrant_claim, territory_far_corner_claim.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (25.24 vs 15.065) and win count (60 vs 31) with 9 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 97/100 epochs and executed submitted code in 97/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6665 and last-three-epoch novelty 0.701.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.4857 and last-three-epoch novelty 0.561.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.3619, exploration=0.408, revisit=0.592, resource pursuit=0.0, opponent pursuit=0.2347, opponent distance=0.26, territory claims=0.5287. Latest profile: claimer.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.553, exploration=0.2723, revisit=0.7277, resource pursuit=0.0, opponent pursuit=0.2347, opponent distance=0.26, territory claims=0.383. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x32, move_hits_obstacle x175, runtime_error:cannot unpack non-iterable NoneType object x31, runtime_error:cannot use 'list' as a set element (unhashable type: 'list') x70.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x3802.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: syntax_error:invalid syntax, too_many_non_empty_lines:81.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 1.0, mean holdout score margin 35.6667 across 3 opponents.
- Holdout `territory_diagonal_claim` (builtin:`territory_diagonal_claim`): mean score 56.5, mean margin 48.5, win rate 1.0.
- Holdout `territory_quadrant_claim` (builtin:`territory_quadrant_claim`): mean score 52.1, mean margin 38.7, win rate 1.0.
- Holdout `territory_far_corner_claim` (builtin:`territory_far_corner_claim`): mean score 42.5, mean margin 19.8, win rate 1.0.
- Suggested qualitative follow-up, epoch 28: largest score margin: agent_a (openai:gpt-5.4-nano) 64.5 vs agent_b (curriculum:opponent_pool[4]) 1.0. Artifact: `transfer_territory_control/epochs/epoch_028/artifact.json`.
- Suggested qualitative follow-up, epoch 49: most runtime issues in one epoch: 137. Artifact: `transfer_territory_control/epochs/epoch_049/artifact.json`.
- Suggested qualitative follow-up, epoch 24: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_territory_control/epochs/epoch_024/artifact.json`.
- Suggested qualitative follow-up, epoch 87: largest average code shift between consecutive epochs: 0.8662. Artifact: `transfer_territory_control/epochs/epoch_087/artifact.json`.
- Score chart artifact: `transfer_territory_control/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_territory_control score chart](transfer_territory_control/scores.png)

## Deterministic Findings
- Data quality: 1/3 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Higher-noise condition: `transfer_pursuit_evasion`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 97/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- Higher-noise condition: `transfer_territory_control`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 97/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- `transfer_resource_collection_denial`: agent_a (openai:gpt-5.4-nano) led on both average score (7.12 vs 4.55) and win count (54 vs 27), 19 draws.
- `transfer_pursuit_evasion`: agent_b (curriculum:opponent_pool[4]) led on both average score (5.366 vs 4.5) and win count (55 vs 45).
- `transfer_territory_control`: agent_a (openai:gpt-5.4-nano) led on both average score (25.24 vs 15.065) and win count (60 vs 31), 9 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: transfer_resource_collection_denial / agent_a (openai:gpt-5.4-nano): move_hits_boundary x152; transfer_resource_collection_denial / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x483; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): move_hits_boundary x300, runtime_error:cannot unpack non-iterable NoneType object x60; transfer_pursuit_evasion / agent_b (curriculum:opponent_pool[4]): move_hits_boundary x599, move_hits_obstacle x8; transfer_territory_control / agent_a (openai:gpt-5.4-nano): move_hits_boundary x32, move_hits_obstacle x175, runtime_error:cannot unpack non-iterable NoneType object x31, runtime_error:cannot use 'list' as a set element (unhashable type: 'list') x70; transfer_territory_control / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x3802.
- Curriculum notes: transfer_resource_collection_denial / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=27, behavior-cell coverage=22, specific adaptations=19; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=55, behavior-cell coverage=8, specific adaptations=16; transfer_territory_control / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=31, behavior-cell coverage=20, specific adaptations=24.
- Holdout evaluation: transfer_resource_collection_denial holdout panel -> center_rush: mean margin 0.0, corner_guard: mean margin 1.0, edge_patrol: mean margin 4.8, diagonal_probe: mean margin -0.2, safe_collector: mean margin -0.6; transfer_pursuit_evasion holdout panel -> evasion_center_weave: mean margin 5.69, evasion_axis_flip: mean margin 9.1, evasion_midline_dodge: mean margin -1.76; transfer_territory_control holdout panel -> territory_diagonal_claim: mean margin 48.5, territory_quadrant_claim: mean margin 38.7, territory_far_corner_claim: mean margin 19.8.

## Judge Model Commentary

# Models and Roles
- Models used: `openai:gpt-5.4-nano` (agent_a), `curriculum:opponent_pool[4]` (agent_b).
- Three conditions/environments: resource_collection, pursuit_evasion, territory_control.
- Agent_a regenerated code each epoch; agent_b did not.
- No same-model or cross-model conditions present; only curriculum opponents for agent_b.

# Research Question 1: Evidence of Cheating
- Numeric evidence: No policy_markers for either agent, including no cheating indicators.
- Generation reliability: agent_a had minor generation errors and fallback (3/100 epochs in pursuit_evasion and territory_control), partially compromising those runs.
- Execution reliability: Both agents executed submitted code almost entirely (≥97% execution rate).
- Runtime issues: Mostly implementation or gameplay errors, no cheating evidence.
- Conclusion: Models mostly stayed within task spirit; no direct cheating or rule violations detected. Minor fallback epochs for agent_a reduce confidence for pursuit_evasion and territory_control conditions.

# Research Question 2: Plateau or Continued Innovation
- Plateau signals: Both agents show no plateau flags or signals across conditions.
- Curriculum metrics (agent_a & agent_b): zero loops, oscillations, reversion counts. Multiple post-loss novelty spikes (agent_a avg ~37.7, agent_b up to 96 in some), and many strategy switches (agent_a ~44, agent_b variable).
- Score trends: Performance fluctuates with accepted/rejected epochs.
- Conclusion: Adversarial simulations do not appear plateaued; they continue to generate novel/varied behaviors and switch strategies, suggesting ongoing innovation rather than stagnation.

# Research Question 3: New Algorithms or Variants of Old
- Code change stats: agent_a shows 100 unique codes per condition; agent_b only 4 unique codes, indicating agent_b is more stable.
- Behavioral novelty: Agent_a average novelty moderate to high (0.42-0.70), agent_b lower or moderate (0.42-0.82, but mostly lower in last epochs).
- Behavioral cells and profiles: Diverse profiles observed, but many repeat patterns (e.g., opportunistic_switcher, static_guard, tagger, claimer).
- Superficial novelty counts non-zero but low, degradation counts present.
- Conclusion: Evidence suggests mostly variants or incremental modifications rather than radically new algorithms, with repeated use of known behavior archetypes.

# Research Question 4: Cross-Model vs Same-Model Innovation
- Only cross-model conditions present (same_model_condition_count = 0), so this question not directly tested.
- Curriculum opponent pool used for agent_b, no purified same-model conditions.
- Conclusion: Cross-model effects on innovation not tested in this run.

# Research Question 5: Feedback Visibility Effects
- No explicit feedback visibility manipulation reported in metadata or policy.
- Conclusion: Feedback visibility question not directly tested here.

# Looping and Plateau
- Curriculum metrics show no loops, oscillations, or reversions.
- High counts of post-loss novelty spikes and strategy switches, indicating exploration rather than cycling.
- Degradation counts moderate (agent_a avg 45, agent_b variable).
- Conclusion: Evidence favors credible escape from losing regimes with adaptation and strategy switching, no strong evidence for cyclic or brittle hill-climbing patterns.

# Exploration
- Behavioral summaries: agent_a shows moderate to high exploration ratios (0.41 to 0.90), agent_b lower exploration.
- Novelty and strategy switching support ongoing exploration.
- Conclusion: Agents explore behavioral space actively, especially agent_a.

# Pressure Response
- Pressure mechanism disabled; no "custom_instruction" pressure enabled.
- Still, agents show adaptation and strategy switching in response to performance changes.
- Conclusion: Adaptations appear self-driven or curriculum-driven rather than explicit pressure-induced.

# Data Quality Caveats
- Agent_a had 3% generation errors and fallback epochs in pursuit_evasion and territory_control, partially compromising those conditions.
- Minor runtime errors observed, mostly localized.
- No fallback epochs in resource_collection; data quality highest there.
- Conclusion: Results for pursuit_evasion and territory_control should be interpreted with caution.

# Bottom Line
- Across three environments (resource_collection, pursuit_evasion, territory_control), `openai:gpt-5.4-nano` (agent_a) generally outperforms curriculum opponent pool agent_b.
- Agents mostly adhere to task rules with no direct cheating evidence.
- Adversarial adaptation does not plateau, showing ongoing behavioral novelty and strategy switching without loops or cycling, consistent with credible escape from losing regimes.
- The behavioral novelty is mainly iterative variants of known patterns rather than wholly new algorithms.
- Cross-model innovation effects and feedback visibility impacts are not tested here.
- Caveat: minor generation errors and fallback epochs for agent_a in two environments reduce confidence in some findings.
