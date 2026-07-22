# Artifact Manifest

This file maps retained thesis evidence to the public repository artifacts.

Each retained phase is documented by a tagged code snapshot, a phase protocol,
an archived run directory, and an aggregate report. Tags and archived outputs
are the stable reference points for the reported claims.

## Evidence Map

### Phase 1: Baseline Simple-Game Evolution

Tag: `phase-1-baseline`

Artifacts: early simple-game run outputs under `runs/`, with supporting protocol notes under `docs/`.

### Phase 2: Adversarial Curriculum and Holdout Tests

Tags: `phase-2-adversarial-curriculum`, `phase-2b-factorial-holdout`

Artifacts: `configs/curriculum_suite/`, `configs/factorial_holdout_suite/`,
`runs/curriculum_suite/`, and related phase reports under `docs/`.

### Phase 3 and Phase 4: Transfer and Causal Transfer

Tags: `phase-3-transfer`, `phase-4-causal-transfer`

Artifacts: `configs/transfer_suite/`, `runs/transfer_suite/`,
`docs/FACTORIAL_AND_TRANSFER_PROTOCOL.md`, `docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md`,
and `docs/PHASE_4_NOVELTY_ADJUDICATION_2026-05-10.md`.

### Phase 5: Routing Archive Across TSP, ATSP, and CVRP

Tag: `phase-5-routing-archive`

Artifacts: `configs/tsp_suite/`, `configs/atsp_suite/`, `configs/cvrp_suite/`,
`runs/tsp_suite/`, `runs/atsp_suite/`, `runs/cvrp_suite/`,
`docs/TSP_PHASE_5_PROTOCOL.md`, `docs/ROUTING_PHASE_5B_5C_PROTOCOL.md`, and
`docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md`.

### Phase 6: Replay-Aware TSP Mechanism

Tag: `phase-6-replay-mechanism`

Artifacts: `configs/tsp_phase6_suite/`, `runs/tsp_phase6_suite/`,
`docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md`, and
`docs/PHASE_6_TSP_REPLAY_MECHANISM_RESULTS_2026-05-20.md`.

### Phase 7: Operator Rediscovery and Failure Modes

Tag: `phase-7-operator-discovery`

Artifacts: `configs/tsp_phase7_suite/`, `runs/tsp_phase7_suite/`,
`docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md`, and
`docs/PHASE_7_TSP_OPERATOR_DISCOVERY_RESULTS_2026-05-20.md`.

### Phase 8: Adaptive Portfolio Tests

Tag: `phase-8-adaptive-portfolio`

Artifacts: `configs/tsp_phase8_suite/`, `runs/tsp_phase8_suite/`,
`docs/PHASE_8_ADAPTIVE_HEURISTIC_PORTFOLIO_PROTOCOL.md`, and
`docs/PHASE_8_ADAPTIVE_HEURISTIC_PORTFOLIO_RESULTS_2026-05-21.md`.

### Phase 9: Real-World CVRP Solver Evolution

Tag: `phase-9-real-world-vrp`

Artifacts: `configs/cvrp_phase9_suite/`, `runs/cvrp_phase9_suite/`,
`docs/PHASE_9_REAL_WORLD_CVRP_SOLVER_EVOLUTION_PROTOCOL.md`, and
`docs/PHASE_9_REAL_WORLD_CVRP_SOLVER_EVOLUTION_RESULTS_2026-05-21.md`.

### Phase 9 Closeout: Budget-Control CVRP

Tag: `phase-9-closeout-budget-control`

Artifacts: `configs/cvrp_phase9_closeout/`, `runs/cvrp_phase9_closeout/`,
`docs/PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_PROTOCOL.md`, and
`docs/PHASE_9_CLOSEOUT_BUDGET_CONTROL_CVRP_RESULTS_2026-06-05.md`.

### Phase 10: Cross-Family Synthesis

Tag: `phase-10-cross-family-synthesis`

Artifacts: `configs/cross_family_synthesis/`,
`runs/cross_family_synthesis/meta_patterns_20260522_165500/`, and
`docs/CROSS_FAMILY_CODE_EVOLUTION_SYNTHESIS_2026-05-22.md`.

### Phase 11: Model-Strength Factorial

Tag: `phase-11-model-strength-factorial`

Artifacts: `configs/model_strength_factorial/`,
`runs/cross_family_model_x_evolution_factorial/20260524_172130/`,
`docs/MODEL_STRENGTH_FACTORIAL_PROTOCOL.md`, and
`docs/MODEL_STRENGTH_FACTORIAL_RESULTS_2026-05-27.md`.

### Phase 12: State-of-the-Art CVRP Calibration

Tag: `phase-12-sota-cvrp-hgs-baseline`

Artifacts: `run_cvrp_phase12_sota_hgs_baseline.py`,
`runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/`,
`docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_PROTOCOL.md`, and
`docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_RESULTS_2026-07-21.md`.

## Prompt, Candidate, and Generated-Code Records

Official run directories preserve experiment records emitted by the harness when
those records are part of the run provenance. These records include prompt text
sent to the model, model responses, extracted candidate JSON files, generated
policy or solver code, validation records, and fallback/error records.

Aggregate values are reported in the phase reports and run summaries. Prompt,
candidate, generated-code, and validation records establish provenance for the
evolved programs that produced those aggregate reports.

## Excluded Private Material

The public repository excludes:

- API keys, `.env` files, local credentials, or account identifiers.
- Private thesis drafts, presentation drafts, or committee-revision notes.
- Large transient worker outputs that are not referenced by a phase report.
- Local caches, virtual environments, compiled bytecode, and editor metadata.

The ignored `DO NOT COMMIT/` directory is reserved for private thesis,
presentation, and administrative material.

## Notes on Non-Retained Work

The `clean-model-strength-continuum` direction was not pursued as a thesis phase
and is recorded as future work rather than supporting evidence.

Historical exploratory artifacts may include checks outside the retained thesis
evidence. In particular, the direct-Codex CVRP check in the cross-family
synthesis artifacts is preserved for context but is not used as retained thesis
evidence because it was not a frozen replicated condition.
