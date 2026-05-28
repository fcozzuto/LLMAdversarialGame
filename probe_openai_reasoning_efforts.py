from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from llm_grid_battle.llm import _openai_responses_text, _post_json, load_env_files
from model_strength_factorial_common import load_jsonish_config


def _model_specs(config_path: Path) -> list[dict[str, Any]]:
    config = load_jsonish_config(config_path)
    return [
        spec
        for spec in config.get("model_tiers", [])
        if str(spec.get("provider", "")).lower() == "openai"
    ]


def _probe_one(
    *,
    model: str,
    effort: str,
    max_output_tokens: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "accepted": False,
            "error_type": "missing_api_key",
            "error": "OPENAI_API_KEY is missing.",
            "output_text": "",
            "elapsed_seconds": 0.0,
        }

    payload = {
        "model": model,
        "instructions": "Reply with exactly OK.",
        "input": "OK",
        "reasoning": {"effort": effort},
        "text": {"verbosity": "low"},
        "max_output_tokens": max_output_tokens,
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "llm-adversarial-game-reasoning-preflight/0.1",
    }

    started = perf_counter()
    try:
        response = _post_json(
            "https://api.openai.com/v1/responses",
            headers,
            payload,
            timeout_seconds,
        )
        output_text = _openai_responses_text(response)
        return {
            "accepted": True,
            "error_type": "",
            "error": "",
            "output_text": output_text[:200],
            "elapsed_seconds": round(perf_counter() - started, 3),
        }
    except Exception as exc:
        error = str(exc)
        error_type = "unsupported_reasoning_effort" if "reasoning.effort" in error.lower() else "api_error"
        if "model" in error.lower() and ("not found" in error.lower() or "does not exist" in error.lower()):
            error_type = "model_unavailable"
        if "rate_limit" in error.lower() or "http 429" in error.lower():
            error_type = "rate_limit"
        if "insufficient_quota" in error.lower() or "quota" in error.lower():
            error_type = "quota"
        return {
            "accepted": False,
            "error_type": error_type,
            "error": error[:1000],
            "output_text": "",
            "elapsed_seconds": round(perf_counter() - started, 3),
        }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "model_tier",
        "model_name",
        "reasoning_effort",
        "accepted",
        "error_type",
        "elapsed_seconds",
        "output_text",
        "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe OpenAI reasoning-effort support for configured pinned models.")
    parser.add_argument("--config", default="configs/model_strength_continuum_factorial.yaml")
    parser.add_argument("--efforts", default="low,medium,high")
    parser.add_argument("--max-output-tokens", type=int, default=16)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--timestamp", default="")
    parser.add_argument("--output-root", default="DO NOT COMMIT/openai_reasoning_effort_preflight")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    load_env_files(project_root)
    efforts = [item.strip().lower() for item in args.efforts.split(",") if item.strip()]
    specs = _model_specs(Path(args.config))
    if not specs:
        raise SystemExit(f"No OpenAI model_tiers found in {args.config}.")

    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_root) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for spec in specs:
        model_tier = str(spec["model_tier"])
        model_name = str(spec["model_name"])
        for effort in efforts:
            print(f"Probing {model_name} effort={effort}")
            result = _probe_one(
                model=model_name,
                effort=effort,
                max_output_tokens=int(args.max_output_tokens),
                timeout_seconds=float(args.timeout_seconds),
            )
            rows.append(
                {
                    "model_tier": model_tier,
                    "model_name": model_name,
                    "reasoning_effort": effort,
                    **result,
                }
            )

    common_supported = [
        effort
        for effort in efforts
        if all(row["accepted"] for row in rows if row["reasoning_effort"] == effort)
    ]
    summary = {
        "config": args.config,
        "efforts": efforts,
        "max_output_tokens": int(args.max_output_tokens),
        "model_count": len(specs),
        "probe_count": len(rows),
        "accepted_count": sum(1 for row in rows if row["accepted"]),
        "common_supported_efforts": common_supported,
        "recommended_effort": common_supported[0] if common_supported else "",
        "output_dir": str(output_dir),
    }

    _write_csv(output_dir / "reasoning_effort_preflight.csv", rows)
    (output_dir / "reasoning_effort_preflight.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"reasoning_effort_preflight.csv: {output_dir / 'reasoning_effort_preflight.csv'}")
    print(f"common_supported_efforts: {common_supported if common_supported else 'none'}")


if __name__ == "__main__":
    main()
