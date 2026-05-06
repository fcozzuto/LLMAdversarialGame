# Aggregate Research Report

## Included Runs
- Run count: 3.
- Conditions aggregated: 1.
- Runs: `run_20260505_204435_a`, `run_20260505_211324_b`, `run_20260505_213345_c`.

## Cross-Run Summary
- No same-model conditions were included in this aggregate.
- Cross-model novelty mean 0.557 (std 0.0257, 95% CI 0.5279 to 0.5861).
- No same-model rule-boundary indicator summary is available for this aggregate.
- Cross-model rule-boundary indicators mean 0.0 (std 0.0, 95% CI 0.0 to 0.0).
- Curriculum loop count mean 0.0 (std 0.0, 95% CI 0.0 to 0.0).
- Curriculum strategy switches mean 44.0 (std 4.0, 95% CI 39.4736 to 48.5264).
- Curriculum post-loss novelty spikes mean 28.6667 (std 3.5119, 95% CI 24.6926 to 32.6407).
- Curriculum specific adaptation count mean 21.0 (std 2.6458, 95% CI 18.0061 to 23.9939).
- Curriculum behavior-cell coverage mean 23.0 (std 4.5826, 95% CI 17.8143 to 28.1857).

## Aggregate Charts
### Mean Score by Condition
![Mean average score by condition and agent](aggregate_average_scores.png)
- Each bar shows the mean final score per epoch for one agent role in that condition.
- Error bars show the 95% confidence interval across the included runs.

### Submitted-Code Execution Rate by Condition
![Submitted-code execution rate by condition and agent](aggregate_execution_rates.png)
- The y-axis is the percentage of epochs where submitted code executed instead of a fallback policy.
- Values near 100% indicate the infrastructure stayed reliable across the included runs.

### Mean Code Novelty by Condition
![Mean code novelty by condition and agent](aggregate_novelty.png)
- Novelty is the average normalized code-change score across epochs for that agent role and condition.
- Higher bars indicate more code variation across repeated runs, not necessarily better performance.

### Curriculum Loop Signals
![Curriculum loop count by condition and agent](aggregate_curriculum_loops.png)
- Higher bars indicate more repeated motifs or unchanged-policy loops under the curriculum conditions.

### Curriculum Strategy Switches
![Curriculum strategy switch count by condition and agent](aggregate_curriculum_switches.png)
- Higher bars indicate more switches between heuristic or behavior classes across epochs.

## Condition Results
### rotating_opponents_with_nemesis_archive
- Matchup type: cross-model.
- Curriculum roles: learner = agent_a (openai:gpt-5.4-nano); opponent role = agent_b (curriculum:opponent_pool[6]).
- Fully clean run count: 3/3.
- Research tags: archive_reintroduce_every=5, replicate_label=a, seed_offset=0, suite_family=curriculum_suite, suite_type=nemesis_archive; archive_reintroduce_every=5, replicate_label=b, seed_offset=1000, suite_family=curriculum_suite, suite_type=nemesis_archive; archive_reintroduce_every=5, replicate_label=c, seed_offset=2000, suite_family=curriculum_suite, suite_type=nemesis_archive.
- agent_a (openai:gpt-5.4-nano) average score: agent_a (openai:gpt-5.4-nano) mean 6.6983 (std 0.1069, 95% CI 6.5773 to 6.8193).
- agent_a (openai:gpt-5.4-nano) generation success rate: agent_a (openai:gpt-5.4-nano) mean 1.0 (std 0.0, 95% CI 1.0 to 1.0).
- agent_a (openai:gpt-5.4-nano) submitted-code execution rate: agent_a (openai:gpt-5.4-nano) mean 1.0 (std 0.0, 95% CI 1.0 to 1.0).
- agent_a (openai:gpt-5.4-nano) novelty: agent_a (openai:gpt-5.4-nano) mean 0.557 (std 0.0257, 95% CI 0.5279 to 0.5861).
- agent_a (openai:gpt-5.4-nano) rule-boundary indicator count: agent_a (openai:gpt-5.4-nano) mean 0.0 (std 0.0, 95% CI 0.0 to 0.0).
- agent_b (curriculum:opponent_pool[6]) average score: agent_b (curriculum:opponent_pool[6]) mean 4.8083 (std 0.0896, 95% CI 4.7069 to 4.9098).
- agent_b (curriculum:opponent_pool[6]) generation success rate: agent_b (curriculum:opponent_pool[6]) mean 1.0 (std 0.0, 95% CI 1.0 to 1.0).
- agent_b (curriculum:opponent_pool[6]) submitted-code execution rate: agent_b (curriculum:opponent_pool[6]) mean 1.0 (std 0.0, 95% CI 1.0 to 1.0).
- agent_b (curriculum:opponent_pool[6]) novelty: agent_b (curriculum:opponent_pool[6]) mean 0.6524 (std 0.0112, 95% CI 0.6397 to 0.665).
- agent_b (curriculum:opponent_pool[6]) rule-boundary indicator count: agent_b (curriculum:opponent_pool[6]) mean 0.0 (std 0.0, 95% CI 0.0 to 0.0).
- Learner loop count: learner mean 0.0 (std 0.0, 95% CI 0.0 to 0.0).
- Learner stable strategy switches: learner mean 44.0 (std 4.0, 95% CI 39.4736 to 48.5264).
- Learner post-loss novelty spikes: learner mean 28.6667 (std 3.5119, 95% CI 24.6926 to 32.6407).
- Learner same-opponent adaptation count: learner mean 21.0 (std 2.6458, 95% CI 18.0061 to 23.9939).
- Learner behavior-cell coverage: learner mean 23.0 (std 4.5826, 95% CI 17.8143 to 28.1857).
- Elite archive coverage: elite archive coverage mean 9.6667 (std 1.5275, 95% CI 7.9381 to 11.3952).
- agent_a win share: agent_a mean 0.5467 (std 0.0513, 95% CI 0.4886 to 0.6047).
- agent_b win share: agent_b mean 0.2867 (std 0.0351, 95% CI 0.2469 to 0.3264).
- draw win share: draw mean 0.1667 (std 0.0404, 95% CI 0.1209 to 0.2124).
- Qualitative follow-up candidates:
- Follow-up candidate from `run_20260505_204435_a`, epoch 1: largest score margin: agent_a (openai:gpt-5.4-nano) 0.0 vs agent_b (curriculum:opponent_pool[6]) 12.0.
- Follow-up candidate from `run_20260505_204435_a`, epoch 11: most runtime issues in one epoch: 154.
- Follow-up candidate from `run_20260505_204435_a`, epoch 81: largest average code shift between consecutive epochs: 0.8472.
- Follow-up candidate from `run_20260505_204435_a`, epoch 7: first curriculum rejection by robustness checks: rejected_by_replay_checks.

## Interpretation Caveats
- Aggregate results are only as strong as the included run set. If the input runs mix different prompts, environments, or suite definitions, treat the summary as descriptive rather than causal.
- Confidence intervals here summarize variation across run-level condition summaries; they are not substitutes for careful experimental design.
- Use this aggregate report together with per-run reports and the research checklist before making strong claims.

## Aggregate Conclusions
- Data quality summary: 1/1 conditions were fully clean, 0/1 were near-clean, and 0/1 remained higher-noise.
- This aggregate includes curriculum conditions, so the learner policy is the primary unit of analysis and opponent-role metrics are contextual.

### Best-Supported Findings
- This aggregate only supports cross-model novelty summary (0.557); no same-model comparison is available here.
- Rule-boundary indicator rates for the available cross-model conditions were 0.0; no same-model comparison is available here.
- Curriculum loop pressure produced an average loop count of 0.0 and an average strategy-switch count of 44.0 across enabled conditions.
- Specific same-opponent adaptation signals averaged 21.0 across enabled curriculum conditions.

### Directional Or Uncertain Findings
- No major directional-only findings stood out beyond the supported points above.

### Claims Not Supported Yet
- The aggregate does not by itself establish causality; the strongest causal interpretations should come from replicated ablation conditions rather than from mixed-condition summaries alone.
- Code novelty should not be treated as equivalent to strategic innovation without qualitative review of notable epochs and behavior traces.
