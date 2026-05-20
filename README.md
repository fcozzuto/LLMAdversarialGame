# LLM Adversarial Agent Games

This project runs adversarial experiments in a family of small 2D games. The original benchmark is resource collection / denial on a grid, and the same harness now supports pursuit / evasion and territory-control variants for transfer studies. Each epoch is a full game. After every epoch, the framework saves the code, prompts, scores, paths, environment events, and sandbox/runtime signals, then feeds a configurable subset of that information back to the models so they can propose improved deterministic code for the next epoch.

The repository now also includes routing-benchmark follow-on phases. Those phases keep the replay-aware curriculum logic, replay archives, novelty/complexity tracking, and held-out transfer evaluation, but move from the toy grid environments to benchmark-driven routing studies:

- phase 5: symmetric TSPLIB95 Euclidean TSP, TSPLIB95 ATSP, and CVRPLIB CVRP
- phase 6: a TSP-only replay-mechanism study that asks why `random_replay` beat `failure_replay`
- phase 7: a modular operator-discovery track that evolves one reusable TSP heuristic operator at a time instead of a whole solver
- phase 8: an adaptive heuristic portfolio track that evolves an interpretable controller over a frozen library of known TSP heuristics

The design stays intentionally small:

- One package, one runner, one JSON suite config.
- Minimal third-party dependencies for report/chart artifacts: `Pillow` and `reportlab`.
- Artifacts are written as JSON, Markdown, SVG, PNG, and PDF so you can inspect them without extra tooling.
- The same runner supports same-model vs cross-model experiments, feedback ablations, obstacles, fixed vs resampled maps, and a final low-cost report pass.

## Layout

- `run_suite.py`: entrypoint for running one or more conditions.
- `aggregate_runs.py`: aggregate repeated runs into one cross-run markdown/PDF report.
- `configs/default_suite.json`: default suite with same-model, cross-model, and limited-feedback conditions.
- `configs/smoke_suite.json`: offline builtin smoke test.
- `configs/live_smoke_suite.json`: one-condition live API smoke test.
- `configs/research_ablations_suite.json`: targeted ablations for feedback and generation scaffolding.
- `configs/research_controls_suite.json`: baseline and frozen-control conditions for research runs.
- `configs/research_cheating_opportunity_suite.json`: optional undocumented-field opportunity tests for rule-boundary studies.
- `configs/full_suite/`: full multi-run research campaign bundle plus ordered runbook.
- `configs/curriculum_suite/`: phase-2 adversarial-curriculum suite bundle plus ordered runbook.
- `configs/factorial_holdout_suite/`: holdout-first factorial ablation bundle for recipe comparison.
- `configs/transfer_suite/`: cross-environment transfer runbook plus the generated transfer suite.
- `configs/tsp_suite/`: phase-5 symmetric TSP replay-transfer suite.
- `configs/tsp_phase6_suite/`: phase-6 TSP replay-mechanism suite.
- `configs/tsp_phase7_suite/`: phase-7 modular operator-discovery suite.
- `configs/tsp_phase8_suite/`: phase-8 adaptive heuristic portfolio suite.
- `configs/atsp_suite/`: phase-5B ATSP replay-transfer suite.
- `configs/cvrp_suite/`: phase-5C CVRP replay-transfer suite.
- `build_transfer_suite.py`: generate a transfer suite from the winning factorial recipe.
- `analyze_causal_transfer.py`: paired-seed transfer comparison plus failure-mode and behavior-versus-novelty analysis for phase 4.
- `review_novelty_spikes.py`: build a manual novelty-validation packet from completed runs.
- `prepare_tsp_benchmarks.py`: download the phase-5 TSPLIB95 subset, compute best-known costs from official tours, and write the benchmark manifest.
- `run_tsp_suite.py`: run the constrained replay-aware TSP benchmark suite.
- `aggregate_tsp_runs.py`: aggregate repeated TSP-suite runs into one cross-run report.
- `aggregate_tsp_phase6_runs.py`: aggregate repeated phase-6 TSP replay-mechanism runs into one cross-run report.
- `run_tsp_operator_suite.py`: run the phase-7 modular operator-discovery suite.
- `aggregate_tsp_operator_runs.py`: aggregate repeated phase-7 operator-discovery runs into one cross-run report.
- `run_tsp_phase8_suite.py`: run the phase-8 adaptive heuristic portfolio suite.
- `aggregate_tsp_phase8_runs.py`: aggregate repeated phase-8 adaptive-portfolio runs into one cross-run report.
- `prepare_atsp_benchmarks.py`: download the phase-5B TSPLIB95 ATSP subset and write the benchmark manifest with official best-known costs.
- `run_atsp_suite.py`: run the constrained replay-aware ATSP benchmark suite.
- `aggregate_atsp_runs.py`: aggregate repeated ATSP-suite runs into one cross-run report.
- `prepare_cvrp_benchmarks.py`: download the phase-5C CVRPLIB subset, verify official solution files, and write the benchmark manifest.
- `run_cvrp_suite.py`: run the constrained replay-aware CVRP benchmark suite.
- `aggregate_cvrp_runs.py`: aggregate repeated CVRP-suite runs into one cross-run report.
- `llm_grid_battle/`: game engine, sandbox, prompt builder, analysis, and SVG output.
- `llm_tsp/`: TSP benchmark loader, heuristic scaffold, replay archive logic, reporting, and runner support.
- `llm_tsp_operator/`: modular operator schema, scaffold engine, validation pipeline, reporting, and runner support for phase 7.
- `llm_tsp_portfolio/`: frozen heuristic portfolio, controller schema, prompt builder, reporting, and runner support for phase 8.
- `llm_atsp/`: ATSP benchmark loader, constrained asymmetric heuristic scaffold, replay archive logic, reporting, and runner support.
- `llm_cvrp/`: CVRP benchmark loader, constrained routing heuristic scaffold, replay archive logic, reporting, and runner support.
- `benchmarks/tsp/`: prepared TSPLIB95 symmetric benchmark subset plus synthetic geometric manifests.
- `benchmarks/atsp/`: prepared TSPLIB95 asymmetric benchmark subset plus synthetic asymmetric manifests.
- `benchmarks/cvrp/`: prepared CVRPLIB subset plus synthetic routing manifests.
- `runs/`: generated artifacts.
- `RESEARCH_CHECKLIST.md`: fixed research protocol and minimum publishable checklist.
- `docs/CURRICULUM_V2_PROTOCOL.md`: phase-2 protocol for looping, plateauing, exploration, pressure response, curriculum, and holdout evaluation.
- `docs/FACTORIAL_AND_TRANSFER_PROTOCOL.md`: holdout-first factorial and cross-environment transfer protocol.
- `docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md`: phase-4 protocol for paired transfer replication, opponent failure modes, and functional-adaptation analysis.
- `docs/TSP_PHASE_5_PROTOCOL.md`: phase-5A protocol for the initial symmetric-TSPLIB transfer step.
- `docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md`: phase-6 protocol for the focused TSP replay-mechanism study.
- `docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md`: phase-7 protocol for modular TSP operator discovery and validation.
- `docs/PHASE_8_ADAPTIVE_HEURISTIC_PORTFOLIO_PROTOCOL.md`: phase-8 protocol for adaptive heuristic portfolio control over a frozen TSP library.
- `docs/PHASE_7_TSP_OPERATOR_DISCOVERY_RESULTS_2026-05-20.md`: official phase-7 operator-discovery result note.
- `docs/ROUTING_PHASE_5B_5C_PROTOCOL.md`: phase-5B/5C protocol for the ATSP and CVRP extensions.
- `docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md`: first replicated routing-benchmark results note across TSP, ATSP, and CVRP.
- `docs/VALIDITY_AND_GENERALIZATION_BACKLOG.md`: deferred checklist for metric validation, stronger evaluation, replication discipline, and broader generalization claims.

## Agent Interface

Each model must return Python that defines:

```python
def choose_move(observation):
    return [dx, dy]
```

The engine calls that function every turn. `dx` and `dy` must each be `-1`, `0`, or `1`. Invalid moves are rejected by keeping the agent in place and logging the violation.

## Sandbox Model

The generated code is executed in a separate Python process with:

- no imports
- restricted builtins
- per-turn timeouts
- fallback execution when static validation fails

That is not a formally secure Python sandbox, but it is enough for controlled experimentation and for detecting obvious cheating attempts such as imports, file access, introspection, or repeated invalid actions.

## Running

Use any Python 3.11+ interpreter:

```powershell
python -m pip install -r requirements.txt
python run_suite.py --config configs/default_suite.json
```

For replicated campaigns, you can offset all condition seeds without copying config files:

```powershell
python run_suite.py --config configs/curriculum_suite/02_rotating_opponents.json --seed-offset 1000 --replicate-label b
```

The runner loads environment variables from either:

- `.env`
- `DO NOT COMMIT/.env`

Expected keys:

- `OPENAI_API_KEY`
- `GROQ_API_KEY`

## Research Workflow

- Use [RESEARCH_CHECKLIST.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/RESEARCH_CHECKLIST.md) as the fixed protocol before making strong claims.
- Use [docs/CURRICULUM_V2_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/CURRICULUM_V2_PROTOCOL.md) when you are working on the adversarial-curriculum phase.
- Use [docs/FACTORIAL_AND_TRANSFER_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/FACTORIAL_AND_TRANSFER_PROTOCOL.md) when you are working on the holdout-first factorial study or the cross-environment transfer study.
- Use [docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md) when you are working on the next causal-interpretation phase after the initial transfer result.
- Use [docs/TSP_PHASE_5_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/TSP_PHASE_5_PROTOCOL.md) when you are moving the replay-aware machinery onto symmetric TSPLIB95 and the constrained TSP heuristic scaffold.
- Use [docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_6_TSP_REPLAY_MECHANISM_PROTOCOL.md) when you are running the focused mechanism study on why `random_replay` beat `failure_replay` on symmetric TSP.
- The official phase-6 evidence readout is versioned on branch `replay-mechanism` in `docs/PHASE_6_TSP_REPLAY_MECHANISM_RESULTS_2026-05-20.md`.
- Use [docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_7_TSP_OPERATOR_DISCOVERY_PROTOCOL.md) when you are running the modular operator-discovery track and its transplant/ablation pipeline.
- Use [docs/PHASE_7_TSP_OPERATOR_DISCOVERY_RESULTS_2026-05-20.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_7_TSP_OPERATOR_DISCOVERY_RESULTS_2026-05-20.md) when you need the current evidence readout for the completed phase-7 operator-discovery campaign.
- Use [docs/PHASE_8_ADAPTIVE_HEURISTIC_PORTFOLIO_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_8_ADAPTIVE_HEURISTIC_PORTFOLIO_PROTOCOL.md) when you are running the adaptive heuristic portfolio phase and comparing fixed, random, oracle, supervised, static-LLM, adaptive-LLM, replay-aware, and full-solver conditions.
- Use [docs/ROUTING_PHASE_5B_5C_PROTOCOL.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/ROUTING_PHASE_5B_5C_PROTOCOL.md) when you are extending the benchmark-transfer study to TSPLIB95 ATSP or CVRPLIB.
- Use [docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/docs/PHASE_5_ROUTING_RESULTS_2026-05-14.md) when you need the current evidence readout for the completed 20-offset routing campaign.
- Use `configs/research_ablations_suite.json` when you want causal comparisons on feedback visibility or the generation scaffold.
- Use `configs/research_controls_suite.json` when you want builtin baselines or frozen-agent controls.
- Use `configs/research_cheating_opportunity_suite.json` when you want to test whether agents exploit undocumented observation fields that are present at runtime but omitted from the documented schema.
- Use [configs/full_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/full_suite/RUNBOOK.md) when you want the full stricter campaign, including repeated core runs, repeated ablations, controls, cheating-opportunity checks, and aggregate report generation in a fixed order.
- Use [configs/curriculum_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/curriculum_suite/RUNBOOK.md) when you want the updated curriculum campaign with three replicated runs per family, replay-aware novelty gating, elite-archive selection, stronger holdout evaluation, and loss-triggered mutation as a controlled auxiliary ablation.
- Use [configs/factorial_holdout_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/factorial_holdout_suite/RUNBOOK.md) when you want the six-condition holdout-first recipe comparison with five replicated seed offsets.
- Use [configs/transfer_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/RUNBOOK.md) after the factorial study, once you have selected the winning recipe and generated the transfer suite.
- Use [configs/transfer_suite/PHASE_4_RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/PHASE_4_RUNBOOK.md) when you want the paired phase-4 transfer replication and the causal-transfer analysis pass.
- Use [configs/tsp_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/tsp_suite/RUNBOOK.md) when you want the replay-aware TSP benchmark suite, its replication workflow, and the phase-5 aggregation commands.
- Use [configs/tsp_phase6_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/tsp_phase6_suite/RUNBOOK.md) when you want the TSP replay-mechanism suite, its 20-offset workflow, and the mechanism-study aggregation commands.
- Use [configs/tsp_phase7_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/tsp_phase7_suite/RUNBOOK.md) when you want the modular operator-discovery suite and its validation-heavy replication workflow.
- Use [configs/tsp_phase8_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/tsp_phase8_suite/RUNBOOK.md) when you want the adaptive heuristic portfolio suite and its paired-offset replication workflow.
- Use [configs/atsp_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/atsp_suite/RUNBOOK.md) when you want the replay-aware ATSP benchmark suite and its replication workflow.
- Use [configs/cvrp_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/cvrp_suite/RUNBOOK.md) when you want the replay-aware CVRP benchmark suite and its replication workflow.
- After collecting repeated runs, aggregate them with:

```powershell
python aggregate_runs.py --runs-root runs
```

- That writes `aggregate_summary.json`, `aggregate_report.md`, and `aggregate_report.pdf` into a new `runs/aggregate_*` directory.
- For the TSP benchmark phase, prepare the benchmark pack and then run:

```powershell
conda activate Python3_14
python prepare_tsp_benchmarks.py
python run_tsp_suite.py --config configs/tsp_suite/01_replay_transfer.json
```

The ATSP and CVRP extensions follow the same pattern with `prepare_atsp_benchmarks.py` / `run_atsp_suite.py` and `prepare_cvrp_benchmarks.py` / `run_cvrp_suite.py`.

## Outputs

For each condition and epoch, the project writes:

- prompt text
- model response text
- extracted code
- full epoch artifact JSON
- path/grid SVG

For the full suite, it writes:

- `suite_summary.json`
- `run_metadata.json`
- `report.md`
- `report.pdf`
- one `scores.svg` per condition
- one `scores.png` per condition for report embedding
- curriculum trace fields, behavioral descriptors, and code fingerprints inside each epoch artifact when curriculum is enabled
- holdout evaluation summaries inside `condition_summary.json` and the report when evaluation is enabled

For the phase-5 and phase-6 TSP suites, it writes:

- `condition_summary.json` with per-epoch training, replay-probe, held-out probe, adversarial probe, and transfer-probe gaps
- `training_gap.svg/png` and `transfer_gap.svg/png`
- `suite_summary.json`, `run_metadata.json`, `report.md`, and `report.pdf`
- replay-archive snapshots for worst cases, catastrophic failures, and adversarial layouts
- benchmark-manifest-backed held-out TSPLIB and synthetic evaluation summaries
- phase-6 archive descriptor-diversity, hardness, size-bias, and residual-failure summaries

For the ATSP and CVRP suites, it writes the same artifact structure with family-appropriate held-out benchmark summaries and replay-archive traces.

For the phase-7 modular operator suite, it writes:

- `condition_summary.json` with per-epoch training, replay-probe, held-out probe, and transfer-probe summaries
- `operator_report.json` and `operator_report.md` for each modular condition
- `training_gap.svg/png` and `transfer_gap.svg/png`
- `suite_summary.json`, `run_metadata.json`, `report.md`, and `report.pdf`
- final operator validation summaries covering transplant, family, Pareto, and ablation checks

For the phase-8 adaptive heuristic portfolio suite, it writes:

- `condition_summary.json` for every baseline and controller condition
- `training_gap.svg/png` and `transfer_gap.svg/png` for the adaptive-controller conditions
- `suite_summary.json`, `run_metadata.json`, `report.md`, and `report.pdf`
- selector-regret, runtime-adjusted-gap, runtime-inflation, and Pareto-efficiency summaries
- held-out TSPLIB and synthetic-validation-family summaries using a common final evaluation path across fixed, oracle, supervised, controller, and full-solver conditions

## Notes

- The OpenAI backend uses the Responses API with low verbosity and a reasoning-effort fallback that retries with supported values when a model rejects the initial setting. It also retries transient upstream failures such as HTTP 502/503/504 with exponential backoff, which reduces the chance that a single provider glitch contaminates a run.
- The default judge model is `gpt-4.1-mini`. It is a stable low-cost fallback for summary-style analysis that does not depend on GPT-5-family organization verification.
- If you want offline smoke tests first, change providers in the config to `builtin` and use models like `nearest_resource`, `sweep_rows`, or `opponent_shadow`.
- The phase-5 TSP smoke suite writes to `DO NOT COMMIT/tsp_suite/smoke`; official TSP study runs remain under `runs/tsp_suite/...`.
- The phase-6 TSP smoke suite writes to `DO NOT COMMIT/tsp_phase6_suite/smoke`; official mechanism-study runs remain under `runs/tsp_phase6_suite/...`.
- The phase-7 TSP smoke suite writes to `DO NOT COMMIT/tsp_phase7_suite/smoke`; official operator-discovery runs remain under `runs/tsp_phase7_suite/...`.
- The phase-8 TSP smoke suite writes to `DO NOT COMMIT/tsp_phase8_suite/smoke`; official adaptive-portfolio runs remain under `runs/tsp_phase8_suite/...`.
- The official phase-6 artifact archive is tagged as `phase-6-replay-mechanism` on branch `replay-mechanism`; the `operator-discovery` branch starts from the phase-6 implementation state rather than the archived phase-6 run tree.
- The phase-5 ATSP smoke suite writes to `DO NOT COMMIT/atsp_suite/smoke`; official ATSP study runs remain under `runs/atsp_suite/...`.
- The phase-5 CVRP smoke suite writes to `DO NOT COMMIT/cvrp_suite/smoke`; official CVRP study runs remain under `runs/cvrp_suite/...`.
- The transfer workflow assumes the factorial study identifies a winning recipe first; use `build_transfer_suite.py` to stamp that recipe into the cross-environment suite before running official transfer experiments.
- `build_transfer_suite.py` now accepts `--study-phase`, which is useful when you want phase-specific metadata and separate run roots for follow-on replication campaigns such as phase 4.
- The TSP benchmark pack uses the official TSPLIB95 catalog as the benchmark definition source and computes best-known costs from the corresponding published optimal-tour files when those are available in the selected subset.
- The ATSP benchmark pack uses the official TSPLIB95 ATSP catalog plus the published ATSP best-known-values page.
- The CVRP benchmark pack uses the official CVRPLIB catalog and verifies the downloaded official solution files against recomputed route costs before admitting an instance into the curated subset.
