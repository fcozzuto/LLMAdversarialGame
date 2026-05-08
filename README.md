# LLM Adversarial Agent Games

This project runs adversarial experiments in a family of small 2D games. The original benchmark is resource collection / denial on a grid, and the same harness now supports pursuit / evasion and territory-control variants for transfer studies. Each epoch is a full game. After every epoch, the framework saves the code, prompts, scores, paths, environment events, and sandbox/runtime signals, then feeds a configurable subset of that information back to the models so they can propose improved deterministic code for the next epoch.

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
- `build_transfer_suite.py`: generate a transfer suite from the winning factorial recipe.
- `analyze_causal_transfer.py`: paired-seed transfer comparison plus failure-mode and behavior-versus-novelty analysis for phase 4.
- `review_novelty_spikes.py`: build a manual novelty-validation packet from completed runs.
- `llm_grid_battle/`: game engine, sandbox, prompt builder, analysis, and SVG output.
- `runs/`: generated artifacts.
- `RESEARCH_CHECKLIST.md`: fixed research protocol and minimum publishable checklist.
- `docs/CURRICULUM_V2_PROTOCOL.md`: phase-2 protocol for looping, plateauing, exploration, pressure response, curriculum, and holdout evaluation.
- `docs/FACTORIAL_AND_TRANSFER_PROTOCOL.md`: holdout-first factorial and cross-environment transfer protocol.
- `docs/PHASE_4_CAUSAL_TRANSFER_PROTOCOL.md`: phase-4 protocol for paired transfer replication, opponent failure modes, and functional-adaptation analysis.
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
- Use `configs/research_ablations_suite.json` when you want causal comparisons on feedback visibility or the generation scaffold.
- Use `configs/research_controls_suite.json` when you want builtin baselines or frozen-agent controls.
- Use `configs/research_cheating_opportunity_suite.json` when you want to test whether agents exploit undocumented observation fields that are present at runtime but omitted from the documented schema.
- Use [configs/full_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/full_suite/RUNBOOK.md) when you want the full stricter campaign, including repeated core runs, repeated ablations, controls, cheating-opportunity checks, and aggregate report generation in a fixed order.
- Use [configs/curriculum_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/curriculum_suite/RUNBOOK.md) when you want the updated curriculum campaign with three replicated runs per family, replay-aware novelty gating, elite-archive selection, stronger holdout evaluation, and loss-triggered mutation as a controlled auxiliary ablation.
- Use [configs/factorial_holdout_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/factorial_holdout_suite/RUNBOOK.md) when you want the six-condition holdout-first recipe comparison with five replicated seed offsets.
- Use [configs/transfer_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/RUNBOOK.md) after the factorial study, once you have selected the winning recipe and generated the transfer suite.
- Use [configs/transfer_suite/PHASE_4_RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/transfer_suite/PHASE_4_RUNBOOK.md) when you want the paired phase-4 transfer replication and the causal-transfer analysis pass.
- After collecting repeated runs, aggregate them with:

```powershell
python aggregate_runs.py --runs-root runs
```

- That writes `aggregate_summary.json`, `aggregate_report.md`, and `aggregate_report.pdf` into a new `runs/aggregate_*` directory.

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

## Notes

- The OpenAI backend uses the Responses API with low verbosity and a reasoning-effort fallback that retries with supported values when a model rejects the initial setting. It also retries transient upstream failures such as HTTP 502/503/504 with exponential backoff, which reduces the chance that a single provider glitch contaminates a run.
- The default judge model is `gpt-4.1-mini`. It is a stable low-cost fallback for summary-style analysis that does not depend on GPT-5-family organization verification.
- If you want offline smoke tests first, change providers in the config to `builtin` and use models like `nearest_resource`, `sweep_rows`, or `opponent_shadow`.
- The transfer workflow assumes the factorial study identifies a winning recipe first; use `build_transfer_suite.py` to stamp that recipe into the cross-environment suite before running official transfer experiments.
- `build_transfer_suite.py` now accepts `--study-phase`, which is useful when you want phase-specific metadata and separate run roots for follow-on replication campaigns such as phase 4.
