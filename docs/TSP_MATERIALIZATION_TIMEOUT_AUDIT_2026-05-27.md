# TSP Materialization Timeout Audit (2026-05-27)

This note audits the TSP materialization-timeout rows in the archived mixed-ladder model-strength factorial run:

`runs/cross_family_model_x_evolution_factorial/20260524_172130`

## Summary

- Timeout-marked TSP candidate materializations: `10`.
- All 10 timeout-marked candidates occurred in `medium_model`.
- By technique:
  - `failure_replay`: `8`
  - `budget_matched_no_replay`: `1`
  - `random_replay`: `1`
- Accepted timeout-marked candidates: `2`.
- Rejected timeout-marked candidates: `8`.

The broader scan found more TSP fallback-like rows if generation fallback and non-timeout materialization fallback are counted together, but the supervisor-mentioned `10` rows correspond to explicit `materialization_timeout` issues.

## Timeout Rows

| model_tier | technique | seed | candidate | accepted |
| --- | --- | ---: | ---: | --- |
| `medium_model` | `budget_matched_no_replay` | 21013 | 4 | false |
| `medium_model` | `failure_replay` | 21017 | 1 | true |
| `medium_model` | `failure_replay` | 21017 | 2 | false |
| `medium_model` | `failure_replay` | 21017 | 3 | false |
| `medium_model` | `failure_replay` | 21017 | 4 | false |
| `medium_model` | `failure_replay` | 21017 | 5 | false |
| `medium_model` | `failure_replay` | 21017 | 6 | false |
| `medium_model` | `failure_replay` | 21017 | 7 | false |
| `medium_model` | `failure_replay` | 21017 | 8 | false |
| `medium_model` | `random_replay` | 21006 | 1 | true |

## Consequence

These rows do not invalidate the archived mixed-ladder run because the run completed and logged fallback behavior, but they weaken any fine-grained TSP interpretation. The clean-continuum phase therefore adds explicit realized-budget accounting and writes `tsp_diagnostics/tsp_materialization_audit.csv` during aggregation.
