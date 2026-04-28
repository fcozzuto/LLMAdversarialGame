# LLM Adversarial Grid Battle

This project runs a simple adversarial experiment in which two LLM-generated agents compete on a 2D grid to collect fixed resources. Each epoch is a full game. After every epoch, the framework saves the code, prompts, scores, paths, and sandbox/runtime events, then feeds a configurable subset of that information back to the models so they can propose improved deterministic code for the next epoch.

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
- `llm_grid_battle/`: game engine, sandbox, prompt builder, analysis, and SVG output.
- `runs/`: generated artifacts.
- `RESEARCH_CHECKLIST.md`: fixed research protocol and minimum publishable checklist.

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

The runner loads environment variables from either:

- `.env`
- `DO NOT COMMIT/.env`

Expected keys:

- `OPENAI_API_KEY`
- `GROQ_API_KEY`

## Research Workflow

- Use [RESEARCH_CHECKLIST.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/RESEARCH_CHECKLIST.md) as the fixed protocol before making strong claims.
- Use `configs/research_ablations_suite.json` when you want causal comparisons on feedback visibility or the generation scaffold.
- Use `configs/research_controls_suite.json` when you want builtin baselines or frozen-agent controls.
- Use `configs/research_cheating_opportunity_suite.json` when you want to test whether agents exploit undocumented observation fields that are present at runtime but omitted from the documented schema.
- Use [configs/full_suite/RUNBOOK.md](C:/Users/kaaro/Documents/GitHub/LLMAdversarialGame/configs/full_suite/RUNBOOK.md) when you want the full stricter campaign, including repeated core runs, repeated ablations, controls, cheating-opportunity checks, and aggregate report generation in a fixed order.
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

## Notes

- The OpenAI backend uses the Responses API with low verbosity and a reasoning-effort fallback that retries with supported values when a model rejects the initial setting. That keeps mixed-model suites from silently failing onto default code.
- The default judge model is `gpt-5-mini`. That is deliberate: it is a low-cost GPT-5 family option that is still adequate for summary-style analysis.
- If you want offline smoke tests first, change providers in the config to `builtin` and use models like `nearest_resource`, `sweep_rows`, or `opponent_shadow`.
