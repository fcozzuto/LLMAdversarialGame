from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from llm_grid_battle.llm import _generate_text, judge_text, load_env_files

from .code_validation import validate_code
from .heuristic_engine import builtin_heuristic_code, default_heuristic_code


@dataclass
class GenerationResult:
    raw_text: str
    code: str
    submitted_code: str = ""
    error: str | None = None
    validation_issues: list[str] = field(default_factory=list)
    repair_attempted: bool = False
    used_fallback: bool = False


def extract_code(text: str) -> str:
    source = (text or "").strip()
    marker = "def build_heuristic"
    start = source.find(marker)
    if start != -1:
        return source[start:].strip().strip("`")
    return source.strip().strip("`")


def generate_code(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    repair_invalid_submissions: bool = True,
    timeout: float = 60.0,
) -> GenerationResult:
    if provider == "builtin":
        code = builtin_heuristic_code(model)
        return GenerationResult(raw_text=code, code=code, submitted_code=code)

    text, error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    if error:
        return GenerationResult(
            raw_text="",
            code=default_heuristic_code(),
            submitted_code="",
            error=error,
            used_fallback=True,
        )

    code = extract_code(text)
    issues = validate_code(code)
    if not issues:
        return GenerationResult(raw_text=text, code=code, submitted_code=code)
    if not repair_invalid_submissions:
        return GenerationResult(
            raw_text=text,
            code=default_heuristic_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)})",
            validation_issues=issues,
            used_fallback=True,
        )

    repair_prompt = _build_repair_prompt(code, issues)
    repaired_text, repair_error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=repair_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    combined_raw = f"{text}\n\n--- REPAIR ATTEMPT ---\n\n{repaired_text}" if repaired_text else text
    if repair_error:
        return GenerationResult(
            raw_text=combined_raw,
            code=default_heuristic_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)}); repair call failed: {repair_error}",
            validation_issues=issues,
            repair_attempted=True,
            used_fallback=True,
        )

    repaired_code = extract_code(repaired_text)
    repaired_issues = validate_code(repaired_code)
    if repaired_issues:
        return GenerationResult(
            raw_text=combined_raw,
            code=default_heuristic_code(),
            submitted_code=repaired_code,
            error=(
                f"Initial submission invalid ({', '.join(issues)}); "
                f"repair submission invalid ({', '.join(repaired_issues)})"
            ),
            validation_issues=repaired_issues,
            repair_attempted=True,
            used_fallback=True,
        )
    return GenerationResult(
        raw_text=combined_raw,
        code=repaired_code,
        submitted_code=repaired_code,
        repair_attempted=True,
    )


def _build_repair_prompt(code: str, issues: list[str]) -> str:
    return "\n".join(
        [
            "Repair the Python heuristic specification generator below.",
            "Return only raw Python source code.",
            "The first line must be exactly: def build_heuristic():",
            "Do not use markdown fences.",
            "Do not use import statements of any kind.",
            "Return a deterministic dictionary describing a constrained CVRP heuristic scaffold.",
            "",
            "Validator feedback:",
            *[f"- {issue}" for issue in issues],
            "",
            "Previous invalid submission:",
            code,
        ]
    )
