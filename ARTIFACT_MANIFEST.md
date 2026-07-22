# Artifact Manifest for Thesis Evidence

This manifest identifies the public files that support the thesis claims. It is
intended as a navigation aid for examiners and future readers, not as a complete
file inventory.

The canonical evidence for each phase is the combination of the tagged code
snapshot, the phase protocol, the archived run directory, and the aggregate
report. Branch names are working labels; tags and archived outputs are the
stable reference points.

## Evidence Map

| Thesis evidence area | Main public artifacts | Reference tag |
| --- | --- | --- |
| Baseline simple-game evolution | `runs/`, `docs/`, early phase protocol notes | `phase-1-baseline` |
| Adversarial curriculum and holdout tests | `configs/curriculum_suite/`, `runs/curriculum_suite/`, phase reports in `docs/` | `phase-2-adversarial-curriculum`, `phase-2b-factorial-holdout` |
| Transfer and causal transfer analyses | `configs/transfer_suite/`, `runs/transfer_suite/`, `docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md`, `docs/PHASE_4_CAUSAL_TRANSFER_RESULTS.md` | `phase-3-transfer`, `phase-4-causal-transfer` |
| Routing archive across TSP, ATSP, and CVRP | `configs/tsp_suite/`, `configs/atsp_suite/`, `configs/cvrp_suite/`, `runs/tsp_suite/`, `runs/atsp_suite/`, `runs/cvrp_suite/`, `docs/TSP_PHASE_5_PROTOCOL.md`, `docs/ROUTING_PHASE_5B_5C_PROTOCOL.md`, `docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md` | `phase-5-routing-archive` |
| Replay-aware TSP mechanism | `configs/tsp_phase6_suite/`, `runs/tsp_phase6_suite/`, Phase 6 protocol and result notes in `docs/` | `phase-6-replay-mechanism` |
| Operator rediscovery and failure modes | `configs/tsp_phase7_suite/`, `runs/tsp_phase7_suite/`, Phase 7 protocol and result notes in `docs/` | `phase-7-operator-discovery` |
| Adaptive portfolio tests | `configs/tsp_phase8_suite/`, `runs/tsp_phase8_suite/`, Phase 8 protocol and result notes in `docs/` | `phase-8-adaptive-portfolio` |
| Real-world CVRP solver evolution | `configs/cvrp_phase9_suite/`, `runs/cvrp_phase9_suite/`, Phase 9 protocol and result notes in `docs/` | `phase-9-real-world-vrp` |
| Budget-control CVRP closeout | `configs/cvrp_phase9_closeout/`, `runs/cvrp_phase9_closeout/`, closeout protocol and aggregate notes in `docs/` | `phase-9-closeout-budget-control` |
| Cross-family synthesis and result atlas | cross-family analysis scripts, aggregate reports in `docs/`, archived run summaries in `runs/` | `phase-10-cross-family-synthesis` |
| Model-strength factorial | `configs/model_strength_factorial/`, `runs/cross_family_model_x_evolution_factorial/20260524_172130/`, model-strength reports in `docs/` | `phase-11-model-strength-factorial` |
| State-of-the-art CVRP calibration | `run_cvrp_phase12_sota_hgs_baseline.py`, `docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_PROTOCOL.md`, `docs/PHASE_12_SOTA_CVRP_HGS_BASELINE_RESULTS_2026-07-21.md`, `runs/cvrp_phase12_sota_hgs_baseline/pyvrp_hgs_20260721_heldout_30sx5/` | `phase-12-sota-cvrp-hgs-baseline` |

## Prompt and Candidate Artifacts

Some official run directories include prompt text, model responses, candidate
JSON files, generated solver or policy code, and error/fallback records. These
files are retained because they document the process by which the code-evolution
loop produced the archived aggregate results.

They are not required for ordinary inspection of the main empirical conclusions.
Readers who only want to verify reported aggregate values should begin with the
phase reports and run summaries. Readers auditing provenance can inspect the
corresponding prompt and candidate artifacts inside each official run directory.

## Excluded Private Material

The public repository should not include:

- API keys, `.env` files, local credentials, or account identifiers.
- Private thesis drafts, presentation drafts, or committee-revision notes.
- Large transient worker outputs that are not referenced by a phase report.
- Local caches, virtual environments, compiled bytecode, and editor metadata.

The ignored `DO NOT COMMIT/` directory is reserved for private thesis,
presentation, and administrative material.

## Notes on Non-Retained Work

The `clean-model-strength-continuum` direction was not pursued as a thesis phase
and should be treated as future work rather than as supporting evidence.

Historical exploratory artifacts may include checks that were not retained as
thesis claims. The thesis conclusions should be evaluated against the phase
protocols, aggregate reports, and tags listed above.
