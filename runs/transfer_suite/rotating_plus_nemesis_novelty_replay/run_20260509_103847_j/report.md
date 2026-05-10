# Research Report: LLM Adversarial Agent Experiment

## Run Metadata
- Run ID: run_20260509_103847_j
- Started: 2026-05-09 10:38:47
- Finished: 2026-05-09 11:35:10
- Duration: 00:56

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
- Conditions with generation errors or fallback executions (`transfer_territory_control`) weaken causal claims and should be weighted less heavily than cleaner conditions.

## Data Quality Warnings
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) had generation errors in 1/100 epochs.
- transfer_territory_control / agent_a (openai:gpt-5.4-nano) fell back to default code in 1/100 epochs.

## Cross-Condition Summary
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Environment types in this run: pursuit_evasion, resource_collection, territory_control.
- Learner-centric curriculum metrics across enabled conditions: average loops 0.0, oscillations 0.0, reversions 0.0, post-loss novelty spikes 34.3333, stable strategy switches 51.0, behavior-cell coverage 17.3333, specific adaptations 22.3333, degradation signals 50.0.
- Holdout evaluation conditions present in this run: 3.
- Average primary holdout win rate across evaluated conditions: 0.72.
- Average primary holdout score margin across evaluated conditions: 13.7367.

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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=29, stable strategy switches=69, behavior-cell coverage=28, specific adaptations=23, degradation signals=19.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 9 behavior cells.
- Holdout panel opponents: center_rush, corner_guard, edge_patrol, diagonal_probe, safe_collector.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (6.55 vs 4.9) and win count (52 vs 29) with 19 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.6695 and last-three-epoch novelty 0.7274.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.6758 and last-three-epoch novelty 0.7993.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.1446, exploration=0.8189, revisit=0.1811, resource pursuit=0.3436, opponent pursuit=0.5698, opponent distance=0.479. Latest profile: opportunistic_switcher.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.2641, exploration=0.7205, revisit=0.2795, resource pursuit=0.3152, opponent pursuit=0.5698, opponent distance=0.479. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 13 unchanged transitions, current unchanged streak 1, and 5 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x650.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.56, mean holdout score margin 2.24 across 5 opponents.
- Holdout `center_rush` (builtin:`center_rush`): mean score 8.5, mean margin 5.0, win rate 0.6.
- Holdout `corner_guard` (builtin:`corner_guard`): mean score 5.7, mean margin -0.6, win rate 0.2.
- Holdout `edge_patrol` (builtin:`edge_patrol`): mean score 8.8, mean margin 5.6, win rate 1.0.
- Holdout `diagonal_probe` (builtin:`diagonal_probe`): mean score 6.6, mean margin 1.2, win rate 0.6.
- Holdout `safe_collector` (builtin:`safe_collector`): mean score 6.0, mean margin 0.0, win rate 0.4.
- Suggested qualitative follow-up, epoch 8: largest score margin: agent_a (openai:gpt-5.4-nano) 12.0 vs agent_b (curriculum:opponent_pool[4]) 0.0. Artifact: `transfer_resource_collection_denial/epochs/epoch_008/artifact.json`.
- Suggested qualitative follow-up, epoch 33: most runtime issues in one epoch: 77. Artifact: `transfer_resource_collection_denial/epochs/epoch_033/artifact.json`.
- Suggested qualitative follow-up, epoch 82: largest average code shift between consecutive epochs: 0.9117. Artifact: `transfer_resource_collection_denial/epochs/epoch_082/artifact.json`.
- Suggested qualitative follow-up, epoch 10: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_resource_collection_denial/epochs/epoch_010/artifact.json`.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=46, stable strategy switches=46, behavior-cell coverage=6, specific adaptations=20, degradation signals=44.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 5 behavior cells.
- Holdout panel opponents: evasion_center_weave, evasion_axis_flip, evasion_midline_dodge.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (5.3 vs 4.731) and win count (53 vs 47).
- agent_a (openai:gpt-5.4-nano) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.5961 and last-three-epoch novelty 0.535.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.4681 and last-three-epoch novelty 0.5733.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.1707, exploration=0.5863, revisit=0.4137, resource pursuit=0.0, opponent pursuit=0.531, opponent distance=0.45, tag success=0.0753. Latest profile: static_guard.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.5979, exploration=0.2249, revisit=0.7751, resource pursuit=0.0, opponent pursuit=0.531, opponent distance=0.45, survival reward=0.9247. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 8 unchanged transitions, current unchanged streak 1, and 6 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_obstacle x60.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_boundary x539, move_hits_obstacle x89.
- No potential rule-violation indicators were recorded in this condition.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 0.6, mean holdout score margin 1.87 across 3 opponents.
- Holdout `evasion_center_weave` (builtin:`evasion_center_weave`): mean score 6.0, mean margin 1.95, win rate 0.6.
- Holdout `evasion_axis_flip` (builtin:`evasion_axis_flip`): mean score 10.0, mean margin 9.01, win rate 1.0.
- Holdout `evasion_midline_dodge` (builtin:`evasion_midline_dodge`): mean score 2.0, mean margin -5.35, win rate 0.2.
- Suggested qualitative follow-up, epoch 6: largest score margin: agent_a (openai:gpt-5.4-nano) 10.0 vs agent_b (curriculum:opponent_pool[4]) 0.75. Artifact: `transfer_pursuit_evasion/epochs/epoch_006/artifact.json`.
- Suggested qualitative follow-up, epoch 9: most runtime issues in one epoch: 60. Artifact: `transfer_pursuit_evasion/epochs/epoch_009/artifact.json`.
- Suggested qualitative follow-up, epoch 26: largest average code shift between consecutive epochs: 0.7729. Artifact: `transfer_pursuit_evasion/epochs/epoch_026/artifact.json`.
- Suggested qualitative follow-up, epoch 4: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_pursuit_evasion/epochs/epoch_004/artifact.json`.
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
- Learner curriculum metrics: loops=0, oscillations=0, reversions=0, post-loss novelty spikes=28, stable strategy switches=38, behavior-cell coverage=18, specific adaptations=24, degradation signals=87.
- Archive snapshots stored: 4.
- Focal elite archive coverage: 9 behavior cells.
- Holdout panel opponents: territory_diagonal_claim, territory_quadrant_claim, territory_far_corner_claim.
- Overall result: agent_a (openai:gpt-5.4-nano) led on both average score (26.055 vs 14.38) and win count (63 vs 29) with 8 draws.
- agent_a (openai:gpt-5.4-nano) generated valid code in 99/100 epochs and executed submitted code in 99/100 epochs.
- agent_b (curriculum:opponent_pool[4]) generated valid code in 100/100 epochs and executed submitted code in 100/100 epochs.
- agent_a (openai:gpt-5.4-nano) had average code novelty 0.661 and last-three-epoch novelty 0.7521.
- agent_b (curriculum:opponent_pool[4]) had average code novelty 0.5005 and last-three-epoch novelty 0.4074.
- agent_a (openai:gpt-5.4-nano) behavioral profile averaged stay=0.3679, exploration=0.4197, revisit=0.5803, resource pursuit=0.0, opponent pursuit=0.2321, opponent distance=0.2584, territory claims=0.5366. Latest profile: static_guard.
- agent_b (curriculum:opponent_pool[4]) behavioral profile averaged stay=0.5287, exploration=0.2877, revisit=0.7123, resource pursuit=0.0, opponent pursuit=0.2321, opponent distance=0.2584, territory claims=0.3934. Latest profile: static_guard.
- agent_a (openai:gpt-5.4-nano) produced 100 unique normalized code variants, with 0 unchanged transitions, current unchanged streak 1, and 0 repeats after non-improving epochs.
- agent_b (curriculum:opponent_pool[4]) produced 4 unique normalized code variants, with 7 unchanged transitions, current unchanged streak 2, and 3 repeats after non-improving epochs.
- agent_a (openai:gpt-5.4-nano) showed no plateau signal under the current heuristics.
- agent_b (curriculum:opponent_pool[4]) showed no plateau signal under the current heuristics.
- agent_a (openai:gpt-5.4-nano) runtime issues: move_hits_boundary x29, move_hits_obstacle x90, runtime_error:tuple index out of range x65.
- agent_b (curriculum:opponent_pool[4]) runtime issues: move_hits_obstacle x3493.
- agent_a (openai:gpt-5.4-nano) potential rule-violation indicators: syntax_error:closing parenthesis ']' does not match opening parenthesis '('.
- Held-out evaluation: 5 games per opponent for learner `agent_a`.
- Primary endpoint summary: mean holdout win rate 1.0, mean holdout score margin 37.1 across 3 opponents.
- Holdout `territory_diagonal_claim` (builtin:`territory_diagonal_claim`): mean score 57.7, mean margin 49.9, win rate 1.0.
- Holdout `territory_quadrant_claim` (builtin:`territory_quadrant_claim`): mean score 56.7, mean margin 47.9, win rate 1.0.
- Holdout `territory_far_corner_claim` (builtin:`territory_far_corner_claim`): mean score 39.5, mean margin 13.5, win rate 1.0.
- Suggested qualitative follow-up, epoch 20: largest score margin: agent_a (openai:gpt-5.4-nano) 64.5 vs agent_b (curriculum:opponent_pool[4]) 1.0. Artifact: `transfer_territory_control/epochs/epoch_020/artifact.json`.
- Suggested qualitative follow-up, epoch 89: most runtime issues in one epoch: 105. Artifact: `transfer_territory_control/epochs/epoch_089/artifact.json`.
- Suggested qualitative follow-up, epoch 57: first fallback/default-code epoch for agent_a (openai:gpt-5.4-nano). Artifact: `transfer_territory_control/epochs/epoch_057/artifact.json`.
- Suggested qualitative follow-up, epoch 38: largest average code shift between consecutive epochs: 0.8491. Artifact: `transfer_territory_control/epochs/epoch_038/artifact.json`.
- Suggested qualitative follow-up, epoch 10: first curriculum rejection by robustness checks: rejected_by_replay_checks. Artifact: `transfer_territory_control/epochs/epoch_010/artifact.json`.
- Score chart artifact: `transfer_territory_control/scores.svg`.
- Score chart interpretation: The chart should show agent_a (openai:gpt-5.4-nano) finishing above the opponent more often than not. Runtime failures in this condition likely correspond to the most lopsided or irregular epochs.
![transfer_territory_control score chart](transfer_territory_control/scores.png)

## Deterministic Findings
- Data quality: 2/3 conditions were fully clean under the strict zero-generation-error and zero-fallback rule.
- Near-clean conditions: `transfer_territory_control`. These had only isolated failures and at least 99% submitted-code execution for every agent.
- `transfer_resource_collection_denial`: agent_a (openai:gpt-5.4-nano) led on both average score (6.55 vs 4.9) and win count (52 vs 29), 19 draws.
- `transfer_pursuit_evasion`: agent_a (openai:gpt-5.4-nano) led on both average score (5.3 vs 4.731) and win count (53 vs 47).
- `transfer_territory_control`: agent_a (openai:gpt-5.4-nano) led on both average score (26.055 vs 14.38) and win count (63 vs 29), 8 draws.
- This run is organized around curriculum-style learner-versus-opponent-pool conditions, so same-model versus cross-model comparisons are not the main interpretation axis.
- Runtime notes: transfer_resource_collection_denial / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x650; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): move_hits_obstacle x60; transfer_pursuit_evasion / agent_b (curriculum:opponent_pool[4]): move_hits_boundary x539, move_hits_obstacle x89; transfer_territory_control / agent_a (openai:gpt-5.4-nano): move_hits_boundary x29, move_hits_obstacle x90, runtime_error:tuple index out of range x65; transfer_territory_control / agent_b (curriculum:opponent_pool[4]): move_hits_obstacle x3493.
- Curriculum notes: transfer_resource_collection_denial / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=29, behavior-cell coverage=28, specific adaptations=23; transfer_pursuit_evasion / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=46, behavior-cell coverage=6, specific adaptations=20; transfer_territory_control / agent_a (openai:gpt-5.4-nano): loops=0, oscillations=0, reversions=0, post-loss spikes=28, behavior-cell coverage=18, specific adaptations=24.
- Holdout evaluation: transfer_resource_collection_denial holdout panel -> center_rush: mean margin 5.0, corner_guard: mean margin -0.6, edge_patrol: mean margin 5.6, diagonal_probe: mean margin 1.2, safe_collector: mean margin 0.0; transfer_pursuit_evasion holdout panel -> evasion_center_weave: mean margin 1.95, evasion_axis_flip: mean margin 9.01, evasion_midline_dodge: mean margin -5.35; transfer_territory_control holdout panel -> territory_diagonal_claim: mean margin 49.9, territory_quadrant_claim: mean margin 47.9, territory_far_corner_claim: mean margin 13.5.

## Judge Model Commentary

# Models and Roles
- Models used: openai:gpt-5.4-nano (learner agent_a), curriculum:opponent_pool[4] (agent_b)
- Three conditions/environments tested: resource_collection, pursuit_evasion, territory_control
- No same-model matchups; all runs are cross-model (agent_a vs curriculum opponent pool)

# Research Question 1: Task Compliance / Cheating
## Evidence
- Both agents have zero policy_markers indicating rule violations or cheating in all conditions.
- Generation errors and syntax errors only appear for agent_a in territory_control (1/100 epochs) with fallback episodes (fallback_count=1).
- Runtime issues (e.g. move_hits_obstacle) exist but treated as gameplay or implementation issues, not cheating.
- Execution rates near 1.0 for both agents across conditions, indicating valid code runs almost always.
- Behavioral summaries show plausible exploratory and pursuit ratios, no extreme boundary hits or invalid moves.
## Inference
- Both openai:gpt-5.4-nano and curriculum pool opponents mostly adhere to the spirit of the tasks without overt cheating.
- Minor generation errors and a single fallback for agent_a in territory_control suggest slight data quality issues but no evidence of systematic cheating.

# Research Question 2: Plateau vs Innovation
## Evidence
- No plateau signals or plateau reasons reported for any agent in any condition.
- Curriculum metrics show non-zero behavior_cell_count (6 to 28 per agent) and hundreds of strategy switches (e.g., 38 to 84).
- Post-loss novelty spike counts range approx 28 to 58; specific adaptations and strategy switches are substantial.
- Score margins fluctuate, sometimes with rejections and degradation observed.
- Usage of rotating nemesis novelty replay curriculum encourages exploration and adaptation.
## Inference
- Adversarial simulations do not appear to plateau but continue to innovate with multiple behavior cells and strategy switches.
- Absence of plateau indicators supports ongoing innovation during the 100 epochs.

# Research Question 3: New Algorithms vs Variants
## Evidence
- Behavioral descriptors and behavioral cell counts indicate diversity of distinct strategy cells, but many share archetypes (e.g., "opportunistic_switcher", "static_guard", "claimer", "tagger").
- Archive and curriculum selection use behavioral distance as novelty metric, but many accepted codes show modest novelty distances (<0.2 typical) indicating variants rather than large shifts.
- Large code shifts at some epochs indicate occasional substantial updates, but many reversion and strategy switch counts signal iterative refinement.
- Superficial novelty counts are low, suggesting novelty is not mostly trivial.
## Inference
- Both agents produce mostly variants and refinements of known archetypal behavior patterns rather than fundamentally new algorithms.
- The repertoire shows credible adaptation but within a constrained algorithmic design space.

# Research Question 4: Cross-model vs Same-model Innovation
## Evidence
- No same_model conditions present (same_model_condition_count=0).
- cross_model_condition_count = 0 as well per cross_condition_comparison - dataset reports no direct same-model comparison.
## Inference
- Research Question 4 is **not directly tested** in this run.
- No conclusions about relative innovation from cross-model vs same-model play can be drawn here.

# Research Question 5: Feedback Visibility Effects
## Evidence
- No variation in feedback visibility indicated in configuration or metadata.
- Feedback policy is consistent across conditions; no direct manipulation or control condition described.
## Inference
- Feedback visibility effects are **not directly tested** in this run.

# Looping and Plateau Patterns
## Evidence
- Agent_a: loop_count=0, oscillation_count=0, reversion_count=0 across all conditions.
- Agent_b: some non-zero loop and oscillation counts only in pursuit_evasion (loop=8, oscillation=11), but zero in other conditions.
- Degradation counts non-zero for agents: agent_a ~44-87, agent_b ~19-44.
- Escape from losing regimes present (agent_a ~5-17, agent_b ~12-14).
- Strategy switches range from ~38 to 84.
## Inference
- Curriculum pressure mostly produces **local hill-climbing and credible escape from losing regimes**, not persistent looping or oscillation (except limited loops/oscillations for agent_b in pursuit_evasion).
- High reversion counts suggest retries rather than brittle opponent-specific adaptation.
- No strong evidence of persistent loops or plateaus.

# Exploration
## Evidence
- Behavioral summaries: exploration_ratio varies (~0.2 to >0.9) depending on agent and environment.
- Unique_cell_ratio relatively moderate (e.g., agent_a 0.13-0.36; agent_b 0.05-0.31).
- Novelty averages: agent_a ~0.6-0.67; agent_b ~0.45-0.68, with slight increases in recent epochs.
- Substantial strategy switching and adaptation counts.
## Inference
- Agents explore behavior space moderately to extensively, with continuing discovery of novel strategies.
- Exploration is present but tends to be incremental.

# Pressure Response
## Evidence
- Pressure mechanism is disabled (pressure.enabled=false).
- Loss streaks and non-improving streaks accumulate (up to 67 epochs).
- Curriculum enables selection rejection on robustness; multiple rejections recorded.
## Inference
- Since pressure is off, model responses stem from natural curriculum selection and evaluation.
- Models respond to challenge by adaptation and switching strategies rather than forced pressure-induced novelty.

# Data Quality Caveats
- Agent_a in territory_control had 1% generation error rate and 1 fallback epoch; this partially compromises that condition's data quality.
- Runtime issues concentrated mostly on agent_b (move_hits_obstacle high counts), indicating localized gameplay issues, not cheating.
- Policy marker absence suggests no detected cheating or rule violation but code generation errors indicate system should be interpreted conservatively.

# Bottom Line
- The experiments involve cross-model adversarial matches between openai:gpt-5.4-nano (agent_a) and a curriculum opponent pool (agent_b) across three distinct environments.
- Both agents maintain task compliance with no evidence of cheating.
- Adversarial training produces ongoing innovation with no plateau signals, manifesting mainly as variants of archetypal strategies rather than fundamentally new algorithms.
- Cross-model vs same-model innovation and feedback visibility effects are not directly tested.
- Curriculum pressure leads primarily to local adaptation and credible escape from losing states, not persistent loops or brittle overfitting.
- Minor data quality issues for agent_a in territory_control call for cautious interpretation of results in that condition.
- Overall, agent_a tends to outperform agent_b on average scores and win counts.
