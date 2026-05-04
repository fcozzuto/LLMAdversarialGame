from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import json
import os
from pathlib import Path
import re
from typing import Any
import urllib.error
import urllib.request

from .code_validation import (
    MAX_CHARACTERS,
    MAX_NON_EMPTY_LINES,
    TARGET_CHARACTERS,
    TARGET_NON_EMPTY_LINES,
    validate_code,
)
from .sandbox import close_agent, collect_move, launch_agent, request_move


CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
FENCE_LINE_RE = re.compile(r"^\s*```(?:python)?\s*$", re.IGNORECASE)


def load_env_files(project_root: Path) -> None:
    candidates = [project_root / ".env", project_root / "DO NOT COMMIT" / ".env"]
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _strip_fence_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not FENCE_LINE_RE.match(line))


def _slice_from_entrypoint(text: str) -> str:
    candidate = _strip_fence_lines(text).strip()
    marker = "def choose_move"
    start = candidate.find(marker)
    if start != -1:
        candidate = candidate[start:]
    return candidate.strip()


def extract_code(text: str) -> str:
    source = text or ""
    blocks = [match.group(1) for match in CODE_BLOCK_RE.finditer(source)]
    for block in blocks:
        if "def choose_move" in block:
            return _slice_from_entrypoint(block)
    if "def choose_move" in source:
        return _slice_from_entrypoint(source)
    stripped = _strip_fence_lines(source).strip()
    return stripped


def default_agent_code() -> str:
    return """
def choose_move(observation):
    sx, sy = observation["self_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]
""".strip()


def builtin_strategy_code(name: str) -> str:
    normalized = name.lower()
    if normalized in {"nearest_resource", "default", "greedy_nearest"}:
        return default_agent_code()
    if normalized == "sweep_rows":
        return """
def choose_move(observation):
    x, y = observation["self_position"]
    width = observation["grid_width"]
    height = observation["grid_height"]
    target_y = y
    target_x = width - 1 if y % 2 == 0 else 0
    if x != target_x:
        return [1 if target_x > x else -1, 0]
    if y < height - 1:
        return [0, 1]
    return [0, 0]
""".strip()
    if normalized == "opponent_shadow":
        return """
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    def score(cell):
        self_d = abs(cell[0] - sx) + abs(cell[1] - sy)
        opp_d = abs(cell[0] - ox) + abs(cell[1] - oy)
        return (self_d - opp_d, self_d)
    target = min(resources, key=score)
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]
""".strip()
    if normalized == "center_rush":
        return """
def choose_move(observation):
    sx, sy = observation["self_position"]
    cx = observation["grid_width"] // 2
    cy = observation["grid_height"] // 2
    resources = observation.get("resources", [])
    target = [cx, cy]
    if resources:
        target = min(resources, key=lambda item: (abs(item[0] - cx) + abs(item[1] - cy), abs(item[0] - sx) + abs(item[1] - sy)))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]
""".strip()
    if normalized == "corner_guard":
        return """
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    near_self = [cell for cell in resources if abs(cell[0] - sx) + abs(cell[1] - sy) <= abs(cell[0] - ox) + abs(cell[1] - oy)]
    target = min((near_self or resources), key=lambda item: (abs(item[0] - sx) + abs(item[1] - sy), abs(item[0] - ox) + abs(item[1] - oy)))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]
""".strip()
    if normalized == "resource_denier":
        return """
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    def score(cell):
        self_d = abs(cell[0] - sx) + abs(cell[1] - sy)
        opp_d = abs(cell[0] - ox) + abs(cell[1] - oy)
        return (opp_d - self_d, self_d)
    target = max(resources, key=score)
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]
""".strip()
    return default_agent_code()


@dataclass
class GenerationResult:
    raw_text: str
    code: str
    submitted_code: str = ""
    error: str | None = None
    validation_issues: list[str] = field(default_factory=list)
    repair_attempted: bool = False
    used_fallback: bool = False


def _truncate(text: str, limit: int = 1400) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif item.get("type") == "text" and isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join(part for part in parts if part)
    return str(content)


def _openai_responses_text(response: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                parts.append(content["text"])
    return "\n".join(part for part in parts if part)


def _is_unsupported_openai_reasoning_error(body: str) -> bool:
    lowered = body.lower()
    return "reasoning.effort" in lowered and ("unsupported" in lowered or "not supported" in lowered)


def _is_unsupported_openai_text_verbosity_error(body: str) -> bool:
    lowered = body.lower()
    return "text.verbosity" in lowered and ("unsupported" in lowered or "not supported" in lowered)


def _generate_text(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 60.0,
) -> tuple[str, str | None]:
    if provider == "builtin":
        return builtin_strategy_code(model), None

    common_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "llm-grid-battle/0.1",
    }

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "", "OPENAI_API_KEY is missing."
        url = "https://api.openai.com/v1/responses"
        headers = {"Authorization": f"Bearer {api_key}", **common_headers}
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "", "GROQ_API_KEY is missing."
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", **common_headers}
    else:
        return "", f"Unsupported provider: {provider}"

    try:
        if provider == "openai":
            last_error: str | None = None
            payloads: list[dict[str, Any]] = [
                {
                    "model": model,
                    "instructions": system_prompt,
                    "input": user_prompt,
                    "reasoning": {"effort": reasoning_effort},
                    "text": {"verbosity": "low"},
                    "max_output_tokens": max_tokens,
                }
                for reasoning_effort in ("minimal", "low", "none")
            ]
            payloads.append(
                {
                    "model": model,
                    "instructions": system_prompt,
                    "input": user_prompt,
                    "text": {"verbosity": "low"},
                    "max_output_tokens": max_tokens,
                }
            )
            payloads.append(
                {
                    "model": model,
                    "instructions": system_prompt,
                    "input": user_prompt,
                    "text": {"verbosity": "medium"},
                    "max_output_tokens": max_tokens,
                }
            )
            payloads.append(
                {
                    "model": model,
                    "instructions": system_prompt,
                    "input": user_prompt,
                    "max_output_tokens": max_tokens,
                }
            )
            for payload in payloads:
                try:
                    response = _post_json(url, headers, payload, timeout)
                    return _openai_responses_text(response), None
                except urllib.error.HTTPError as exc:
                    body = exc.read().decode("utf-8", errors="replace")
                    last_error = f"HTTP {exc.code}: {body[:500]}"
                    has_reasoning = "reasoning" in payload
                    verbosity = payload.get("text", {}).get("verbosity") if isinstance(payload.get("text"), dict) else None
                    if exc.code == 400 and _is_unsupported_openai_reasoning_error(body) and has_reasoning:
                        continue
                    if exc.code == 400 and _is_unsupported_openai_text_verbosity_error(body) and verbosity != "medium":
                        continue
                    return "", last_error
            return "", last_error or "OpenAI request failed."

        response = _post_json(url, headers, payload, timeout)
        return _content_to_text(response["choices"][0]["message"]["content"]), None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return "", f"HTTP {exc.code}: {body[:500]}"
    except Exception as exc:
        return "", str(exc)


def _describe_issue(issue: str) -> str:
    if issue == "imports_not_allowed":
        return "Do not use import statements."
    if issue in {"dunder_attribute_not_allowed", "dunder_name_not_allowed"}:
        return "Do not use names or attributes that begin with __."
    if issue == "missing_choose_move":
        return "Define exactly one top-level function named choose_move."
    if issue == "entrypoint_may_fall_through":
        return "choose_move can reach the end without returning [dx, dy] on every path."
    if issue.startswith("syntax_error:"):
        return f"Fix the Python syntax error: {issue.split(':', 1)[1]}."
    if issue.startswith("too_many_non_empty_lines:"):
        count = issue.split(":", 1)[1]
        return f"The function is too long at {count} non-empty lines. Keep it to at most {MAX_NON_EMPTY_LINES} lines and target {TARGET_NON_EMPTY_LINES}."
    if issue.startswith("too_many_characters:"):
        count = issue.split(":", 1)[1]
        return f"The function is too long at {count} characters. Keep it under {MAX_CHARACTERS} characters and target {TARGET_CHARACTERS}."
    if issue.startswith("disallowed_call:"):
        name = issue.split(":", 1)[1]
        return f"Do not call {name}."
    if issue.startswith("preflight_runtime_error:"):
        return f"Your function raised a runtime error during validation: {issue.split(':', 1)[1]}."
    if issue.startswith("preflight_invalid_return"):
        return "Your function returned something other than [dx, dy] with integer values in {-1, 0, 1} during validation."
    if issue.startswith("preflight_timeout"):
        return "Your function timed out during validation. Use a simpler strategy."
    if issue.startswith("preflight_non_deterministic"):
        return "Your function produced different outputs for the same observation. It must be deterministic."
    if issue.startswith("preflight_used_fallback"):
        return "Your function could not be executed safely during validation."
    if issue.startswith("preflight_init_error:"):
        return f"Your function failed during initialization: {issue.split(':', 1)[1]}."
    return f"Fix this validator issue: {issue}."


def _build_repair_prompt(*, invalid_code: str, issues: list[str]) -> str:
    lines = [
        "Your previous choose_move submission was invalid and cannot be executed.",
        "Rewrite it as a shorter, simpler, fully valid solution.",
        "",
        "Return only raw Python source code.",
        "The first line must be exactly: def choose_move(observation):",
        "Do not use markdown fences.",
        "Do not add explanation before or after the function.",
        "Do not use import statements of any kind.",
        "Do not use names beginning with __.",
        "Every control path must end by returning [dx, dy] with integer dx and dy in {-1, 0, 1}.",
        "Do not leave placeholder logic, unfinished branches, or helper code without a final return path.",
        "Prefer concise deterministic heuristics over large helper stacks or full-grid search if brevity is at risk.",
        f"Use at most {TARGET_NON_EMPTY_LINES} non-empty lines.",
        f"Keep the function under {TARGET_CHARACTERS} characters.",
        f"The validator rejects code over {MAX_NON_EMPTY_LINES} non-empty lines or over {MAX_CHARACTERS} characters.",
        "If needed, simplify the strategy rather than writing more code.",
        "",
        "Observation fields you may use:",
        "- grid_width, grid_height",
        "- self_position, opponent_position",
        "- resources, obstacles",
        "- remaining_resource_count",
        "- scores",
        "- self_path, opponent_path",
        "",
        "Goal: maximize your score against the opponent while staying deterministic and valid.",
        "",
        "Validator feedback:",
        *[f"- {_describe_issue(issue)}" for issue in issues],
    ]
    if invalid_code.strip():
        lines.extend(
            [
                "",
                "Previous invalid submission excerpt:",
                _truncate(invalid_code),
            ]
        )
    return "\n".join(lines)


def _validation_observations() -> list[dict[str, Any]]:
    base_scores = {"agent_a": 0.0, "agent_b": 0.0}
    return [
        {
            "turn_index": 0,
            "grid_width": 8,
            "grid_height": 8,
            "self_name": "agent_a",
            "opponent_name": "agent_b",
            "self_position": [0, 0],
            "opponent_position": [7, 7],
            "resources": [],
            "obstacles": [],
            "remaining_resource_count": 0,
            "scores": base_scores,
            "self_path": [[0, 0]],
            "opponent_path": [[7, 7]],
        },
        {
            "turn_index": 5,
            "grid_width": 8,
            "grid_height": 8,
            "self_name": "agent_a",
            "opponent_name": "agent_b",
            "self_position": [2, 2],
            "opponent_position": [5, 5],
            "resources": [[1, 1], [2, 6], [6, 2], [4, 4]],
            "obstacles": [[3, 3], [3, 4]],
            "remaining_resource_count": 4,
            "scores": {"agent_a": 3.0, "agent_b": 4.0},
            "self_path": [[0, 0], [1, 1], [2, 2]],
            "opponent_path": [[7, 7], [6, 6], [5, 5]],
        },
        {
            "turn_index": 11,
            "grid_width": 8,
            "grid_height": 8,
            "self_name": "agent_a",
            "opponent_name": "agent_b",
            "self_position": [6, 1],
            "opponent_position": [4, 2],
            "resources": [[0, 7], [5, 1], [6, 3], [7, 0]],
            "obstacles": [[5, 2], [6, 2], [7, 2]],
            "remaining_resource_count": 4,
            "scores": {"agent_a": 7.0, "agent_b": 6.0},
            "self_path": [[7, 0], [6, 1]],
            "opponent_path": [[3, 3], [4, 2]],
        },
    ]


def _behavioral_issues(code: str) -> list[str]:
    runtime = launch_agent(code)
    issues: list[str] = []
    if runtime.issues:
        issues.extend(runtime.issues)
    if runtime.init_error:
        issues.append(f"preflight_init_error:{runtime.init_error}")
    if runtime.used_fallback:
        issues.append("preflight_used_fallback")
    if issues:
        close_agent(runtime)
        return sorted(set(issues))

    try:
        for case_index, observation in enumerate(_validation_observations(), start=1):
            request_move(runtime, observation)
            move, runtime_issue = collect_move(runtime, timeout_seconds=0.5)
            if runtime_issue:
                issues.append(f"preflight_{runtime_issue}:case_{case_index}")
                continue
            request_move(runtime, observation)
            repeated_move, repeated_runtime_issue = collect_move(runtime, timeout_seconds=0.5)
            if repeated_runtime_issue:
                issues.append(f"preflight_{repeated_runtime_issue}:case_{case_index}_repeat")
                continue
            if repeated_move != move:
                issues.append(f"preflight_non_deterministic:case_{case_index}")
    finally:
        close_agent(runtime)
    return sorted(set(issues))


def _validate_submission(
    text: str,
    *,
    pre_execution_validation: bool,
) -> tuple[str, list[str]]:
    code = extract_code(text)
    if not pre_execution_validation:
        return code, []
    issues = validate_code(code)
    if issues:
        return code, issues
    return code, _behavioral_issues(code)


def generate_code(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    pre_execution_validation: bool = True,
    repair_invalid_submissions: bool = True,
    timeout: float = 60.0,
) -> GenerationResult:
    if provider == "builtin":
        code = builtin_strategy_code(model)
        return GenerationResult(raw_text=f"```python\n{code}\n```", code=code, submitted_code=code)

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
            code=default_agent_code(),
            submitted_code="",
            error=error,
            used_fallback=True,
        )

    code, issues = _validate_submission(
        text,
        pre_execution_validation=pre_execution_validation,
    )
    if not issues:
        return GenerationResult(raw_text=text, code=code, submitted_code=code)

    if not repair_invalid_submissions:
        return GenerationResult(
            raw_text=text,
            code=default_agent_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)})",
            validation_issues=issues,
            used_fallback=True,
        )

    repair_prompt = _build_repair_prompt(
        invalid_code=code,
        issues=issues,
    )
    repaired_text, repair_error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=repair_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    combined_raw_text = text
    if repaired_text:
        combined_raw_text = (
            f"{text}\n\n--- REPAIR ATTEMPT ---\n\n{repaired_text}"
            if text
            else repaired_text
        )
    if repair_error:
        return GenerationResult(
            raw_text=combined_raw_text,
            code=default_agent_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)}); repair call failed: {repair_error}",
            validation_issues=issues,
            repair_attempted=True,
            used_fallback=True,
        )

    repaired_code, repaired_issues = _validate_submission(
        repaired_text,
        pre_execution_validation=pre_execution_validation,
    )
    if repaired_issues:
        return GenerationResult(
            raw_text=combined_raw_text,
            code=default_agent_code(),
            submitted_code=repaired_code,
            error=f"Initial submission invalid ({', '.join(issues)}); repair submission invalid ({', '.join(repaired_issues)})",
            validation_issues=repaired_issues,
            repair_attempted=True,
            used_fallback=True,
        )

    return GenerationResult(
        raw_text=combined_raw_text,
        code=repaired_code,
        submitted_code=repaired_code,
        repair_attempted=True,
    )


def judge_text(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 300.0
) -> str:
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
        return f"Judge model call failed: {error}"
    return text
