# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260509_025707_j
- Started: 2026-05-09 02:57:07
- Finished: 2026-05-09 03:50:42
- Duration: 00:54

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
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) had generation errors in 8/100 epochs.
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) fell back to default code in 8/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: pursuit_evasion, resource_collection, territory_control.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 32.3333, stable strategy switches 46.0, behavior-cell coverage 16.3333, specific adaptations 19.0, degradation signals 47.3333.
- Holdout evaluation conditions present in this run: 3.
- Average primary holdout win rate across evaluated conditions: 0.7067.
- Average primary holdout score margin across evaluated conditions: 13.9122.

## How To Read The Score Charts
- Each `scores.svg` file plots one point per epoch for each agent.
- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.
- Higher points mean the agent performed better under that environment's scoring rules in that specific epoch.
- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.

## Condition Results
### transfer_resource_collection_denial
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=j, seed_offset=9000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=resource_collection.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=24, stable strategy switches=56, behavior-cell coverage=26, specific adaptations=18, degradation signals=11.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 8 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (7.055 vs 4.645) and win count (50 vs 24) with 26 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6179 and last-three-epoch novelty 0.5894.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6585 and last-three-epoch novelty 0.5332.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0679, exploration=0.8943, revisit=0.1057, resource pursuit=0.3608, opponent pursuit=0.604, opponent distance=0.4622. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2425, exploration=0.7467, revisit=0.2533, resource pursuit=0.3293, opponent pursuit=0.604, opponent distance=0.4622. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 15 unchanged transitions, current unchanged streak 1, and 5 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x466.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.52, mean holdout score margin 1.8 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 7.9, mean margin 4.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 5.8, mean margin -0.2, win rate 0.4.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 9.0, mean margin 6.0, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 5.6, mean margin -0.8, win rate 0.2.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.0, mean margin 0.0, win rate 0.4.
- Suggested qualitative follow-up, epoch 8: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `transfer_resource_collection_denial/epochs/epoch_008/artifact.json`.
- Suggested qualitative follow-up, epoch 68: most runtime issues in one epoch: 77. Artifact: `transfer_resource_collection_denial/epochs/epoch_068/artifact.json`.
- Suggested qualitative follow-up, epoch 62: largest average code shift between consecutive epochs: 0.8527. Artifact: `transfer_resource_collection_denial/epochs/epoch_062/artifact.json`.
- Suggested qualitative follow-up, epoch 8: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_resource_collection_denial/epochs/epoch_008/artifact.json`.
- Score chart artifact: `transfer_resource_collection_denial/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_resource_collection_denial score chart](transfer_resource_collection_denial/scores.png)

### transfer_pursuit_evasion
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=j, seed_offset=9000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=pursuit_evasion.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `pursuit_evasion` on a 8 x 8 grid.
- Role assignment: agent_a=pursuer, agent_b=evader.
- Capture rules: radius 0, capture points 10.0, evasion survival reward 0.15 per turn.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_nemesis_novelty_replay, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: evasion_corner, evasion_wall_runner, evasion_zigzag, pursuit_direct.
- Acceptance rule: mode=score_or_diversity, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Nemesis archive: reintroduce_every=5, min_score_margin=1.0, max_size=8.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=44, stable strategy switches=42, behavior-cell coverage=9, specific adaptations=17, degradation signals=42.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 4 behavior cells.
- Holdout panel opponents: evasion_center_weave, evasion_axis_flip, evasion_midline_dodge.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (5.6 vs 4.497) and win count (56 vs 44).
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5574 and last-three-epoch novelty 0.4305.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.4544 and last-three-epoch novelty 0.572.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.153, exploration=0.6135, revisit=0.3865, resource pursuit=0.0, opponent pursuit=0.5682, opponent distance=0.4345, tag success=0.0787. Latest profile: tagger.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.612, exploration=0.2418, revisit=0.7582, resource pursuit=0.0, opponent pursuit=0.5682, opponent distance=0.4345, survival reward=0.9213. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 11 unchanged transitions, current unchanged streak 1, and 11 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_boundary x507, move_hits_obstacle x186.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: text:open(.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.6, mean holdout score margin 1.87 across 3 opponents.
- Holdout `evasion_center_weave` (builtin:`evasion_center_weave`): mean score 6.0, mean margin 1.95, win rate 0.6.
- Holdout `evasion_axis_flip` (builtin:`evasion_axis_flip`): mean score 10.0, mean margin 9.01, win rate 1.0.
- Holdout `evasion_midline_dodge` (builtin:`evasion_midline_dodge`): mean score 2.0, mean margin -5.35, win rate 0.2.
- Suggested qualitative follow-up, epoch 6: largest score margin: agent_a (openai:gpt-5.4-nano) 10.0 vs agent_b (curriculum:opponent_pool[4]) 0.75. Artifact: `transfer_pursuit_evasion/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 4: most runtime issues in one epoch: 60. Artifact: `transfer_pursuit_evasion/epochs/epoch_004/artifact.json`.
- Suggested qualitative follow-up, epoch 9: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_pursuit_evasion/epochs/epoch_009/artifact.json`.
- Suggested qualitative follow-up, epoch 4: largest average code shift between consecutive epochs: 0.8209. Artifact: `transfer_pursuit_evasion/epochs/epoch_004/artifact.json`.
- Suggested qualitative follow-up, epoch 9: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_pursuit_evasion/epochs/epoch_009/artifact.json`.
- Score chart artifact: `transfer_pursuit_evasion/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_pursuit_evasion score chart](transfer_pursuit_evasion/scores.png)

### transfer_territory_control
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=j, seed_offset=9000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=territory_control.
- agent_a: openai:gpt-5.4-nano
- agent_b: curriculum:opponent_pool[4]
- Environment: `territory_control` on a 8 x 8 grid.
- Territory rules: flip_on_entry=True, control bonus interval=10, control bonus=0.5.
- Generation scaffold: pre-execution validation was enabled, and repair retries were enabled.
- Adaptation control: agent_b (curriculum:opponent_pool[4]) reused prior code after epoch 1 instead of regenerating each epoch.
- Curriculum design: mode=rotating_nemesis_novelty_replay, learner=agent_a (openai:gpt-5.4-nano), opponent role=agent_b (curriculum:opponent_pool[4]), rotation policy=cyclic.
- Opponent pool: territory_sweeper, territory_center_claim, territory_counterclaim, territory_edge_claim.
- Acceptance rule: mode=score_or_diversity, novelty threshold=0.22, elite-distance threshold=0.18, score tolerance=0.5.
- Replay-aware selection: candidate policies were rechecked against up to 2 archived opponents before acceptance.
- Nemesis archive: reintroduce_every=5, min_score_margin=1.0, max_size=8.
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=29, stable strategy switches=40, behavior-cell coverage=14, specific adaptations=22, degradation signals=89.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 6 behavior cells.
- Holdout panel opponents: territory_diagonal_claim, territory_quadrant_claim, territory_far_corner_claim.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (17.53 vs 10.925) and win count (57 vs 30) with 13 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 92/100 epochs and executed submitted code in 92/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.7578 and last-three-epoch novelty 0.7903.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.5171 and last-three-epoch novelty 0.674.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.4403, exploration=0.2793, revisit=0.7207, resource pursuit=0.0, opponent pursuit=0.1737, opponent distance=0.2073, territory claims=0.4721. Latest profile: claimer.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.5069, exploration=0.2453, revisit=0.7547, resource pursuit=0.0, opponent pursuit=0.1737, opponent distance=0.2073, territory claims=0.4303. Latest profile: claimer.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 8 unchanged transitions, current unchanged streak 1, and 6 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x57, move_hits_obstacle x387, runtime_error:cannot unpack non-iterable int object x70.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x3464.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: entrypoint_may_fall_through.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 1.0, mean holdout score margin 38.0667 across 3 opponents.
- Holdout `territory_diagonal_claim` (builtin:`territory_diagonal_claim`): mean score 42.5, mean margin 35.3, win rate 1.0.
- Holdout `territory_quadrant_claim` (builtin:`territory_quadrant_claim`): mean score 49.1, mean margin 46.3, win rate 1.0.
- Holdout `territory_far_corner_claim` (builtin:`territory_far_corner_claim`): mean score 44.5, mean margin 32.6, win rate 1.0.
- Suggested qualitative follow-up, epoch 2: largest score margin: agent_a (openai:gpt-5.4-nano) 58.5 vs agent_b (curriculum:opponent_pool[4]) 1.0. Artifact: `transfer_territory_control/epochs/epoch_002/artifact.json`.
- Suggested qualitative follow-up, epoch 76: most runtime issues in one epoch: 130. Artifact: `transfer_territory_control/epochs/epoch_076/artifact.json`.
- Suggested qualitative follow-up, epoch 30: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_territory_control/epochs/epoch_030/artifact.json`.
- Suggested qualitative follow-up, epoch 53: largest average code shift between consecutive epochs: 0.8673. Artifact: `transfer_territory_control/epochs/epoch_053/artifact.json`.
- Suggested qualitative follow-up, epoch 5: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_territory_control/epochs/epoch_005/artifact.json`.
- Score chart artifact: `transfer_territory_control/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_territory_control score chart](transfer_territory_control/scores.png)

## Deterministic Findings
- Data quality: 1/3 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Near-clean conditions: `transfer_pursuit_evasion`. These had only isolated failures and at least 99% submitted-code execution for every agent.
- Higher-noise condition: `transfer_territory_control`. Submitted-code execution rates were agent_a (openai:gpt-5.4-nano) 92/100, agent_b (curriculum:opponent_pool[4]) 100/100.
- `transfer_resource_collection_denial`: agent_a (openai:gpt-5.4-nano) led on both average score (7.055 vs 4.645) and win count (50 vs 24), 26 draws.
- `transfer_pursuit_evasion`: agent_a (openai:gpt-5.4-nano) led on both average score (5.6 vs 4.497) and win count (56 vs 44).
- `transfer_territory_control`: agent_a (openai:gpt-5.4-nano) led on both average score (17.53 vs 10.925) and win count (57 vs 30), 13 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: transfer_resource_collection_denial / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x466; transfer_pursuit_evasion / agent_b (curriculum:opponent_pool[4]): move_hits_boundary x507, move_hits_obstacle x186; transfer_territory_control / agent_a (openai:gpt-5.4-nano): move_hits_boundary x57, move_hits_obstacle x387, runtime_error:cannot unpack non-iterable int object x70; transfer_territory_control / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x3464.
- Curriculum notes: transfer_resource_collection_denial / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=24, behavior-cell coverage=26, specific adaptations=18; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=44, behavior-cell coverage=9, specific adaptations=17; transfer_territory_control / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=29, behavior-cell coverage=14, specific adaptations=22.
- Holdout evaluation: transfer_resource_collection_denial holdout panel -> center_rush: mean margin 4.0, corner_guard: mean margin -0.2, edge_patrol: mean margin 6.0, diagonal_probe: mean margin -0.8, safe_collector: mean margin 0.0; transfer_pursuit_evasion holdout panel -> evasion_center_weave: mean margin 1.95, evasion_axis_flip: mean margin 9.01, evasion_midline_dodge: mean margin -5.35; transfer_territory_control holdout panel -> territory_diagonal_claim: mean margin 35.3, territory_quadrant_claim: mean margin 46.3, territory_far_corner_claim: mean margin 32.6.

## Judge Model Commentary

# Models and Roles
- Models: `openai:gpt-5.4-nano` (agent_a), `curriculum:opponent_pool[4]` (agent_b).
- Environments tested: resource_collection, pursuit_evasion, territory_control.
- No same-model matchups; all runs involve `openai:gpt-5.4-nano` as learner vs curriculum opponent pool.
- Agent_b consistently is curriculum opponent_pool with 4-8 classic strategies (builtin models).

# Research Question 1: Task compliance (cheating)
**Measured evidence:**
- No policy markers indicating cheating in any run.
- Generation errors occurred only with agent_a in pursuit_evasion (1%) and territory_control (8%) runs.
- Fallback counts for agent_a in those runs match error counts, indicating fallback to default code, weakening evidence during those epochs.
- No invalid moves or illegal boundary hits reported beyond moderate runtime "move_hits_obstacle".
- No rule violations reported from policy_markers other than generation warnings.

**Inference:**
- Both models mostly stay within the spirit of the task; occasional generation errors and fallback default code (agent_a) partially compromise some epochs but not systemic cheating.
- Agent_b shows no evidence of cheating or fallback.

# Research Question 2: Plateau vs innovation
**Measured evidence:**
- No plateau signals detected in any run for either agent.
- Significant code churn for agent_a (100 unique codes per run, low unchanged streak).
- Agent_b shows stable low unique codes (~4), more repeats.
- Curriculum metrics: no loops or oscillations on agent_a; agent_b shows minor oscillation/loop counts in some runs.
- Many strategy switches (~40-88 per run per agent), many post-loss novelty spikes (29-49 per run).

**Inference:**
- Agent_a exhibits ongoing innovation with frequent strategy switches and novelty spikes.
- Agent_b strategies more stable, fewer unique codes, some oscillations but less innovation.
- Overall no persistent plateau; adversarial simulations generally continue innovating.

# Research Question 3: Novelty nature (new algorithms or minor variants)
**Measured evidence:**
- Behavioral novelty averages moderate: agent_a (0.56-0.76 average), agent_b lower or variable.
- Superficial novelty count for agent_a not zero but less than strategy switches.
- Accepted codes usually low behavioral distance (~0.05 - 0.17) between consecutive elites, indicating incremental strategy variants.
- Many reversion counts near zero for agent_a, indicating persistent changes rather than random switches.
- Archive contains familiar archetypes (e.g., opportunistic_switcher, static_guard, claimer) with algorithmically interpretable code.
- Code provided corresponds to intuitive heuristic variants, no exotic or non-interpretable code snippets.

**Inference:**
- Innovations are mainly incremental variants/adaptations of known algorithmic motifs rather than entirely novel algorithms.
- New algorithms might emerge occasionally but limited evidence for major paradigm shifts.

# Research Question 4: Cross-model vs same-model innovation
- No same-model matchup or curriculum study (curriculum_condition_count equals condition_count = 3, but all vs curriculum opponent pools).
- Cross-model average novelty and policy markers data zero due to absence of these conditions.
- Feedback-visibility manipulation absent (only default feedback).
  
**Inference:**
- Research Question 4 not directly tested in this experiment suite. No evidence for comparative effect of cross-model vs same-model play.

# Research Question 5: Feedback visibility impact
- No real feedback-visibility manipulation across conditions (feedback_policy constant).
- No distinct conditions to compare feedback visibility effects.

**Inference:**
- Feedback visibility effects not directly tested here.

# Looping and Plateau Patterns under Curriculum Pressure
**Measured evidence:**
- Curriculum pressure disabled (pressure: enabled=false).
- Strategy switch counts moderate to high for agent_a (40-88), moderate for agent_b (~38).
- No loops detected for agent_a; agent_b shows loops (11 in pursuit_evasion, 8 in territory_control) and oscillations (8 and 12 respectively).
- Many post-loss novelty spikes indicate agent_a tries escaping losing regimes.
- Agent_b shows reversion counts high (up to 88 in territory_control), indicating brittle opponent-specific adaptation.
- No explicit long-term degradation events.

**Inference:**
- Curriculum pressure not active, but agent_a tends to escape losing regimes via novelty spikes and strategy switches without looping.
- Agent_b shows evidence of local hill-climbing, oscillation, and reversion behavior indicating brittle adaptation.

# Data Quality Caveats
- Agent_a had generation errors and fallback epochs partially compromising pursuit_evasion (1%) and territory_control (8%) runs.
- These epochs may bias innovation and performance metrics downward for agent_a.
- Runtime issues mostly "move_hits_obstacle" more frequent for agent_b but treated as game mechanic failures, not cheating.
- No fallback or errors for agent_b, indicating robust generation and execution on that side.

# Bottom Line
- Across three distinct environments, `openai:gpt-5.4-nano` (agent_a) played against curriculum opponent pools (`curriculum:opponent_pool[4]`) without evidence of cheating or rule violations.
- Agent_a exhibited steady innovation and improvement with frequent strategy switches and post-loss novelty spikes, suggesting continued search rather than plateau.
- Innovations appear to be incremental variants of known behavioral archetypes rather than radically new algorithm classes.
- Agent_b generally more stable with fewer unique codes, some local instability (loops, oscillations) and frequent reversion indicating brittle incremental adaptation.
- No same-model or cross-model direct comparisons; feedback visibility effects untested.
- Curriculum pressure was disabled, so no forced switching; behavior suggests agent_a avoids losing regimes credibly, agent_b sometimes exhibits local cyclic behavior.
- Generation errors and fallbacks for `openai:gpt-5.4-nano` partially compromise some epochs, so conclusions about agent_a's performance and innovation are slightly tentative but overall consistent.
