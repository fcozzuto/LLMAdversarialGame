# Cross-Family Code-Evolution Synthesis

Generated: 2026-05-22T17:06:56

## Purpose

This artifact answers the requested cross-family question: whether comparable LLM-driven code-evolution loops show recurring capability and limitation patterns across the simple-game, TSP, and real-world CVRP experiment families.

The analysis is intentionally conservative. It reuses completed official artifacts instead of creating a new paid campaign, normalizes only metrics that are present in the archived runs, and keeps train-time search dynamics separate from held-out endpoint evidence.

## Evidence Base

- Simple game transfer suite: 10 runs, 3 conditions, 3000 epochs.
- Symmetric TSP replay suite: 20 runs, 4 conditions, 640 epochs.
- Real-world CVRP phase-9 suite: 20 runs, 4 conditions, 160 solver-evolution epochs.
- Direct Codex experiment: one deterministic CVRP solver authored locally by Codex and evaluated through the phase-9 sandbox/validator.

## Family-Level Results

### Simple Game Transfer

| condition | primary_holdout_win_rate | primary_holdout_score_margin | mean_code_novelty | generation_success_rate |
| --- | --- | --- | --- | --- |
| transfer_pursuit_evasion | 0.7 | 3.702 | 0.5553 | 0.996 |
| transfer_resource_collection_denial | 0.484 | 1.348 | 0.59 | 0.992 |
| transfer_territory_control | 0.9467 | 34.17 | 0.6823 | 0.984 |

### TSP Replay

| condition | final_transfer_gap | final_tsplib_gap | mean_code_novelty | adaptation_efficiency |
| --- | --- | --- | --- | --- |
| tsplib_failure_replay | 0.130918 | 0.18132 | 0.806087 | -8.5e-05 |
| tsplib_failure_replay_compression | 0.124895 | 0.177578 | 0.286629 | 0.015348 |
| tsplib_no_replay | 0.132474 | 0.183325 | 0.742512 | -0.01061 |
| tsplib_random_replay | 0.104243 | 0.152211 | 0.736465 | 0.025089 |

### Real-World CVRP

| condition | heldout_feasibility_rate | heldout_penalized_gap | heldout_runtime_ms | mean_code_novelty |
| --- | --- | --- | --- | --- |
| phase9_baseline_clarke_wright_savings | 1 | 0.073766 | 79.5711 | 0 |
| phase9_baseline_nearest_neighbor_constructive | 1 | 0.273435 | 43.0211 | 0 |
| phase9_baseline_regret_insertion_local_search | 1 | 0.466391 | 1473.49 | 0 |
| phase9_solver_evolution | 1 | 0.182231 | 821.706 | 0.471587 |

## Direct Codex Experiment

Codex produced a single deterministic Clarke-Wright-style CVRP solver with bounded local route improvement. This is not an API-generated candidate and not an evolved loop. It is a direct single-shot coding baseline evaluated on the same phase-9 train and held-out split.

| Panel | Feasibility | Mean penalized gap | Mean feasible gap | Mean runtime ms |
| --- | --- | --- | --- | --- |
| train | 1 | 0.064271 | 0.064271 | 243.964 |
| holdout | 1 | 0.06778 | 0.06778 | 687.264 |

Interpretation: the direct Codex solver is useful as a sanity baseline for what a single interactive Codex pass can author, but it should not be treated as a replicated stochastic condition. The fair comparison remains descriptive unless it is rerun under a frozen direct-Codex protocol.

## Meta-Patterns

### Syntactic novelty is common, but not sufficient.

Evidence: Mean novelty was high in the game family (0.6092), TSP (0.687611), and CVRP candidate stream (0.771482), yet final wins were domain-dependent.

Interpretation: The loop is good at producing variants; selection and validation determine whether those variants become useful.

### Improvement depends on available benchmark headroom.

Evidence: TSP random replay improved over no replay on final transfer and TSPLIB gaps, while phase 9 improved over weak CVRP baselines but not Clarke-Wright.

Interpretation: When a strong classical baseline already captures most structure, LLM evolution often produces bounded refinement rather than a dominant new method.

### Failure modes shift with domain constraints.

Evidence: The game loop mainly exposed action/runtime behavior issues, TSP exposed replay-policy sensitivity, and CVRP exposed feasibility/scoring pressure plus low acceptance rates.

Interpretation: A unified framework should classify failure by domain-specific validator pressure rather than only by code novelty or final score.

### The strongest defensible story is capability-bounded adaptation.

Evidence: Codex direct CVRP held-out gap was 0.06778; phase-9 evolved mean held-out gap was 0.182231; Clarke-Wright was 0.073766.

Interpretation: The current data support a framework of capabilities and limits, not a claim that LLM evolution beats mature optimization heuristics.

## Framework Summary

The current project is best summarized as a capability-and-limits framework for LLM-driven code evolution.

- Capability: the loop reliably generates executable, diverse code variants under a structured interface.
- Capability: when validators and baselines leave reachable heuristic headroom, selection can preserve useful refinements.
- Limitation: lexical/code novelty does not reliably imply behavioral novelty or held-out improvement.
- Limitation: strong classical heuristics and low portfolio/benchmark headroom cap apparent wins.
- Limitation: each domain has a different dominant failure mode, so a single aggregate score hides important mechanisms.

## Claim Wording

A defensible dissertation-level claim is: across three increasingly realistic problem families, LLM-guided code evolution can produce diverse, executable heuristic programs and sometimes preserve useful adaptations, but its current success is constrained by validator pressure, baseline strength, and benchmark headroom. The contribution is therefore a measurement framework for when the loop adapts versus when it churns, not a claim of beating mature optimization solvers.

## Sources

- [Henderson et al. 2018, Deep Reinforcement Learning That Matters](https://arxiv.org/abs/1709.06560): motivates replicated runs, careful reporting, and avoiding best-run-only claims.
- [Agarwal et al. 2021, Deep RL at the Edge of the Statistical Precipice](https://arxiv.org/abs/2108.13264): motivates uncertainty-aware aggregate reporting in few-run adaptive systems.
- [Rice 1976, The Algorithm Selection Problem](https://doi.org/10.1016/S0065-2458(08)60520-3): frames portfolio/selector phases as feature-to-algorithm mapping problems.
- [CVRPLIB Uchoa X benchmark family](https://galgos.inf.puc-rio.br/cvrplib/en/instances): defines the real-world CVRP benchmark source used by phase 9.
