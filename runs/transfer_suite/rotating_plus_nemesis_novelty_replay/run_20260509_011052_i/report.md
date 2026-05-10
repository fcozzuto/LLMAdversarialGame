# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260509_011052_i
- Started: 2026-05-09 01:10:52
- Finished: 2026-05-09 02:05:15
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
- Conditions with generation errors or fallback executions (`transfer_pursuit_evasion`) weaken causal claims and should be weighted less heavily than cleaner conditions.

## Data Quality Warnings
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: pursuit_evasion, resource_collection, territory_control.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 32.3333, stable strategy switches 47.0, behavior-cell coverage 13.0, specific adaptations 20.0, degradation signals 48.3333.
- Holdout evaluation conditions present in this run: 3.
- Average primary holdout win rate across evaluated conditions: 0.7556.
- Average primary holdout score margin across evaluated conditions: 13.0122.

## How To Read The Score Charts
- Each `scores.svg` file plots one point per epoch for each agent.
- The x-axis is epoch index. The y-axis is that agent's final score at the end of the epoch, not a cumulative running total across the whole experiment.
- Higher points mean the agent performed better under that environment's scoring rules in that specific epoch.
- A persistent gap between lines means one agent usually finished ahead. Frequent crossings mean the matchup stayed competitive from epoch to epoch.

## Condition Results
### transfer_resource_collection_denial
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=i, seed_offset=8000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=resource_collection.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=22, stable strategy switches=51, behavior-cell coverage=18, specific adaptations=19, degradation signals=4.
- Archive snapshots stored: 3.
- Focal elite archive coverage: 8 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.855 vs 4.815) and win count (51 vs 23) with 26 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.4812 and last-three-epoch novelty 0.4058.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.667 and last-three-epoch novelty 0.8076.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.0405, exploration=0.9191, revisit=0.0809, resource pursuit=0.3851, opponent pursuit=0.6102, opponent distance=0.4869. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.198, exploration=0.7918, revisit=0.2082, resource pursuit=0.3497, opponent pursuit=0.6102, opponent distance=0.4869. Latest profile: opportunistic_switcher.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 12 unchanged transitions, current unchanged streak 1, and 5 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x276.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.4, mean holdout score margin 0.12 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 6.0, mean margin 0.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 6.3, mean margin 0.6, win rate 0.2.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.0, mean margin 4.6, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 4.6, mean margin -2.8, win rate 0.2.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 5.1, mean margin -1.8, win rate 0.0.
- Suggested qualitative follow-up, epoch 52: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `transfer_resource_collection_denial/epochs/epoch_052/artifact.json`.
- Suggested qualitative follow-up, epoch 6: most runtime issues in one epoch: 78. Artifact: `transfer_resource_collection_denial/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 10: largest average code shift between consecutive epochs: 0.8282. Artifact: `transfer_resource_collection_denial/epochs/epoch_010/artifact.json`.
- Suggested qualitative follow-up, epoch 12: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_resource_collection_denial/epochs/epoch_012/artifact.json`.
- Score chart artifact: `transfer_resource_collection_denial/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_resource_collection_denial score chart](transfer_resource_collection_denial/scores.png)

### transfer_pursuit_evasion
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=i, seed_offset=8000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=pursuit_evasion.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=51, stable strategy switches=43, behavior-cell coverage=6, specific adaptations=23, degradation signals=51.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 3 behavior cells.
- Holdout panel opponents: evasion_center_weave, evasion_axis_flip, evasion_midline_dodge.
- Overall result: agent_b (curriculum:opponent_pool[4]) led on both average score (5.048 vs 4.9) and win count (51 vs 49).
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6681 and last-three-epoch novelty 0.7745.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.4604 and last-three-epoch novelty 0.5733.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.1977, exploration=0.5507, revisit=0.4493, resource pursuit=0.0, opponent pursuit=0.4886, opponent distance=0.4633, tag success=0.0702. Latest profile: tagger.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.6091, exploration=0.2236, revisit=0.7764, resource pursuit=0.0, opponent pursuit=0.4886, opponent distance=0.4633, survival reward=0.9298. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 9 unchanged transitions, current unchanged streak 1, and 8 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_obstacle x55, runtime_error:'>' not supported between instances of 'tuple' and 'NoneType' x60.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_boundary x548, move_hits_obstacle x126.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.8667, mean holdout score margin 6.6167 across 3 opponents.
- Holdout `evasion_center_weave` (builtin:`evasion_center_weave`): mean score 8.0, mean margin 5.66, win rate 0.8.
- Holdout `evasion_axis_flip` (builtin:`evasion_axis_flip`): mean score 10.0, mean margin 9.1, win rate 1.0.
- Holdout `evasion_midline_dodge` (builtin:`evasion_midline_dodge`): mean score 8.0, mean margin 5.09, win rate 0.8.
- Suggested qualitative follow-up, epoch 1: largest score margin: agent_a (openai:gpt-5.4-nano) 10.0 vs agent_b (curriculum:opponent_pool[4]) 0.75. Artifact: `transfer_pursuit_evasion/epochs/epoch_001/artifact.json`.
- Suggested qualitative follow-up, epoch 14: most runtime issues in one epoch: 120. Artifact: `transfer_pursuit_evasion/epochs/epoch_014/artifact.json`.
- Suggested qualitative follow-up, epoch 86: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_pursuit_evasion/epochs/epoch_086/artifact.json`.
- Suggested qualitative follow-up, epoch 99: largest average code shift between consecutive epochs: 0.8071. Artifact: `transfer_pursuit_evasion/epochs/epoch_099/artifact.json`.
- Suggested qualitative follow-up, epoch 20: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_pursuit_evasion/epochs/epoch_020/artifact.json`.
- Score chart artifact: `transfer_pursuit_evasion/scores.svg`.
- Score chart interpretation: The chart should show agent_b (curriculum:opponent_pool[4]) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_pursuit_evasion score chart](transfer_pursuit_evasion/scores.png)

### transfer_territory_control
- Curriculum setup: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[4]).
- Feedback visibility: scores, initial resources and obstacles, paths, runtime events, and both agents' code.
- Research tags: environment_family=multi_environment_transfer, factorial_goal=generalizable_adaptation, primary_endpoint=holdout_win_rate, recipe=rotating+nemesis+novelty+replay, recipe_source_condition=rotating_plus_nemesis_novelty_replay, replicate_label=i, seed_offset=8000, study_phase=phase_4, suite_family=transfer_suite, transfer_environment=territory_control.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=24, stable strategy switches=47, behavior-cell coverage=15, specific adaptations=18, degradation signals=90.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 6 behavior cells.
- Holdout panel opponents: territory_diagonal_claim, territory_quadrant_claim, territory_far_corner_claim.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (20.755 vs 10.945) and win count (60 vs 24) with 16 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.7124 and last-three-epoch novelty 0.7454.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.5048 and last-three-epoch novelty 0.4074.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.4137, exploration=0.3103, revisit=0.6897, resource pursuit=0.0, opponent pursuit=0.189, opponent distance=0.2379, territory claims=0.4696. Latest profile: static_guard.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.5007, exploration=0.2524, revisit=0.7476, resource pursuit=0.0, opponent pursuit=0.189, opponent distance=0.2379, territory claims=0.3979. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 8 unchanged transitions, current unchanged streak 2, and 1 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x58, runtime_error:name 'iter' is not defined x69.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x3416.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 1.0, mean holdout score margin 32.3 across 3 opponents.
- Holdout `territory_diagonal_claim` (builtin:`territory_diagonal_claim`): mean score 24.3, mean margin 22.3, win rate 1.0.
- Holdout `territory_quadrant_claim` (builtin:`territory_quadrant_claim`): mean score 36.5, mean margin 32.9, win rate 1.0.
- Holdout `territory_far_corner_claim` (builtin:`territory_far_corner_claim`): mean score 51.0, mean margin 41.7, win rate 1.0.
- Suggested qualitative follow-up, epoch 34: largest score margin: agent_a (openai:gpt-5.4-nano) 59.0 vs agent_b (curriculum:opponent_pool[4]) 1.0. Artifact: `transfer_territory_control/epochs/epoch_034/artifact.json`.
- Suggested qualitative follow-up, epoch 25: most runtime issues in one epoch: 134. Artifact: `transfer_territory_control/epochs/epoch_025/artifact.json`.
- Suggested qualitative follow-up, epoch 48: largest average code shift between consecutive epochs: 0.887. Artifact: `transfer_territory_control/epochs/epoch_048/artifact.json`.
- Suggested qualitative follow-up, epoch 5: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_territory_control/epochs/epoch_005/artifact.json`.
- Suggested qualitative follow-up, epoch 68: first acceptance driven by diversity logic: diversity_gain_within_score_tolerance. Artifact: `transfer_territory_control/epochs/epoch_068/artifact.json`.
- Score chart artifact: `transfer_territory_control/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_territory_control score chart](transfer_territory_control/scores.png)

## Deterministic Findings
- Data quality: 2/3 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Near-clean conditions: `transfer_pursuit_evasion`. These had only isolated failures and at least 99% submitted-code execution for every agent.
- `transfer_resource_collection_denial`: agent_a (openai:gpt-5.4-nano) led on both average score (6.855 vs 4.815) and win count (51 vs 23), 26 draws.
- `transfer_pursuit_evasion`: agent_b (curriculum:opponent_pool[4]) led on both average score (5.048 vs 4.9) and win count (51 vs 49).
- `transfer_territory_control`: agent_a (openai:gpt-5.4-nano) led on both average score (20.755 vs 10.945) and win count (60 vs 24), 16 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: transfer_resource_collection_denial / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x276; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): move_hits_obstacle x55, runtime_error:'>' not supported between instances of 'tuple' and 'NoneType' x60; transfer_pursuit_evasion / agent_b (curriculum:opponent_pool[4]): move_hits_boundary x548, move_hits_obstacle x126; transfer_territory_control / agent_a (openai:gpt-5.4-nano): move_hits_boundary x58, runtime_error:name 'iter' is not defined x69; transfer_territory_control / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x3416.
- Curriculum notes: transfer_resource_collection_denial / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=22, behavior-cell coverage=18, specific adaptations=19; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=51, behavior-cell coverage=6, specific adaptations=23; transfer_territory_control / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=24, behavior-cell coverage=15, specific adaptations=18.
- Holdout evaluation: transfer_resource_collection_denial holdout panel -> center_rush: mean margin 0.0, corner_guard: mean margin 0.6, edge_patrol: mean margin 4.6, diagonal_probe: mean margin -2.8, safe_collector: mean margin -1.8; transfer_pursuit_evasion holdout panel -> evasion_center_weave: mean margin 5.66, evasion_axis_flip: mean margin 9.1, evasion_midline_dodge: mean margin 5.09; transfer_territory_control holdout panel -> territory_diagonal_claim: mean margin 22.3, territory_quadrant_claim: mean margin 32.9, territory_far_corner_claim: mean margin 41.7.

## Judge Model Commentary

# Models and Roles
- Models used: `openai:gpt-5.4-nano` (agent_a), `curriculum:opponent_pool[4]` (agent_b)
- Environments: Three distinct types - `resource_collection`, `pursuit_evasion`, and `territory_control`.
- No same-model matchups; all adversarial play is cross-model (learner openai:gpt-5.4-nano vs curriculum opponent pool).
- agent_a is the learner; agent_b is the fixed opponent pool.
- agent_a regenerates code each epoch; agent_b does not.

# Research Question 1: Cheating Behavior
**Measured evidence:**
- No policy markers indicating rule violations or cheating for either agent.
- Zero invalid move rates across agents.
- Generation error count for agent_a in pursuit_evasion condition: 1/100 epochs (sample error present).
- Fallback count for agent_a in pursuit_evasion: 1/100 epochs - fallback implies code defaulting, a data-quality issue.
- Runtime issues (e.g., move_hits_obstacle) occur mainly for agent_b, interpreted as gameplay failures, not cheating.
  
**Inference:**
- Both models largely stay within task spirit with no evidence of cheating.
- Minor generation errors and a fallback code epoch for agent_a in pursuit_evasion partially compromise robustness but are insufficient to imply cheating.
  
# Research Question 2: Innovation vs Plateau
**Measured evidence:**
- Novelty averages for agent_a: 0.4812 (resource_collection), 0.6681 (pursuit_evasion), 0.7124 (territory_control).
- Novelty averages for agent_b: 0.667 (resource_collection), 0.4604 (pursuit_evasion), 0.5048 (territory_control).
- Curriculum metrics show no loops or oscillations in resource_collection and relatively low loops/oscillations in other conditions.
- Post-loss novelty spikes exist (averages ~32 for curriculum), indicating periodic innovation attempts.
- Strategy switches substantial (>40 avg), indicating ongoing search rather than stagnation.

**Inference:**
- Evidence indicates the adversarial process does not plateau prematurely.
- Models show ongoing innovation with novelty above thresholds and post-loss novelty spikes.
- Lack of sustained plateau signals, though some degradation and reversion occur.

# Research Question 3: New Algorithms or Variants
**Measured evidence:**
- Behavior profiles repeatedly return to a small set of archetypes (e.g., opportunistic_switcher, static_guard, tagger).
- Curriculum data shows many refreshed or replaced behavior cells but mostly within known archetype clusters.
- Superficial novelty counts moderate (e.g., 0 to 26), and no strong signals of truly novel archetypes.
- Code changes for agent_b are limited (few unique codes), agent_a codes diversify more.

**Inference:**
- Models mainly produce variants on existing algorithm archetypes rather than fully new algorithms.
- Innovations are incremental, focusing on tuning or parameter shifts rather than radically new methods.

# Research Question 4: Cross-model vs Same-model Innovation
**Measured evidence:**
- No same-model conditions present; cross-model conditions only.
- Cross-model average novelty and policy markers reported as zero since no same-model runs exist.
- Curriculum condition count equals total conditions (3), indicating curriculum study design rather than paired comparison.

**Inference:**
- Cross-model vs same-model innovation comparison is not directly tested in this run.
- No claims about cross-model play's effect on innovation can be made here.

# Research Question 5: Feedback Visibility Effects
**Measured evidence:**
- No explicit real feedback-visibility manipulation indicated in conditions or metadata.
- Feedback policy static with full inclusion of codes, grid states, opponent code, paths, runtime events, and scores.

**Inference:**
- Feedback visibility effects on outcomes are not directly tested in this experiment suite.

# Looping and Plateau
**Measured evidence:**
- Loop counts: 0 for resource_collection, 0 for pursuit_evasion, 8 for territory_control (moderate).
- Oscillation counts: 0 except for pursuit_evasion (~10) and territory_control (12), indicating some local oscillations.
- Reversion counts: 0 across runs, suggesting limited backward movement.
- Degradation counts are moderate (mean ~48), but escape from losing regime counts present, indicating some recovery.
- Strategy switches numerous (~47 on average).

**Inference:**
- Curriculum pressure yields mostly local hill-climbing and some oscillations but no pervasive loops.
- Some brittle, opponent-specific adaptations exist (many failed fix repetitions in pursuit_evasion agent_b).
- Evidence of credible escape from losing regimes, not persistent cycling.

# Exploration
- Exploration ratios moderate to high for agent_a in resource_collection (0.9191) and territory_control (0.3103), lower in pursuit_evasion (0.5507).
- agent_b generally less exploratory.
- Diversity of behavior cells (up to 18 for resource_collection, 6 in pursuit_evasion, 15 territory_control) supports varied exploration.

# Pressure Response
- No pressure enabled in curriculum policy (pressure.enabled=false).
- Score margins and non-improving streaks lead to selection or rejection without forced pressure.
- High counts of non-improving streaks and selection rejections suggest natural pressure from curriculum without explicit pressure mechanism.

# Data Quality Caveats
- agent_a in pursuit_evasion suffered 1% generation errors and 1 fallback epoch.
- Runtime errors mainly concentrated in certain epochs for both agents, interpreted as localized instability.
- agent_b has substantial move_hits_obstacle counts, mostly gameplay failures.
- All code executions (except fallback) succeed, so results mainly reliable.
- Fallback occurrence suggests minor partial compromise of pursuit_evasion condition.

# Bottom Line
- Across `openai:gpt-5.4-nano` (agent_a) vs curriculum pool (agent_b) in three distinct environments, models primarily adhere to task rules without cheating.
- Adversarial runs show ongoing incremental innovation with moderate novelty, substantial strategy switching, and credible recovery from failures.
- Innovations mostly refine or recombine known archetypes rather than generating entirely new algorithms.
- Cross-model vs same-model effect not tested; feedback visibility manipulation absent.
- Curriculum pressure leads to local hill-climbing with oscillations but no major looping.
- Minor generation and fallback errors in `pursuit_evasion` partially compromise that condition's reliability but do not negate overall trends.
