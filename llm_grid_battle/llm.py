from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Any
import urllib.error
import urllib.request


CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


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


def extract_code(text: str) -> str:
    match = CODE_BLOCK_RE.search(text or "")
    if match:
        return match.group(1).strip()
    return (text or "").strip()


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
    return default_agent_code()


@dataclass
class GenerationResult:
    raw_text: str
    code: str
    error: str | None = None


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
        payload = {
            "model": model,
            "instructions": system_prompt,
            "input": user_prompt,
            "reasoning": {"effort": "minimal"},
            "text": {"verbosity": "low"},
            "max_output_tokens": max_tokens,
        }
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
        response = _post_json(url, headers, payload, timeout)
        if provider == "openai":
            return _openai_responses_text(response), None
        return _content_to_text(response["choices"][0]["message"]["content"]), None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return "", f"HTTP {exc.code}: {body[:500]}"
    except Exception as exc:
        return "", str(exc)


def generate_code(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 60.0,
) -> GenerationResult:
    if provider == "builtin":
        code = builtin_strategy_code(model)
        return GenerationResult(raw_text=f"```python\n{code}\n```", code=code)

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
        return GenerationResult(raw_text="", code=default_agent_code(), error=error)
    code = extract_code(text)
    if "def choose_move" not in code:
        return GenerationResult(raw_text=text, code=default_agent_code(), error="Model did not return choose_move().")
    return GenerationResult(raw_text=text, code=code)


def judge_text(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    text, error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if error:
        return f"Judge model call failed: {error}"
    return text
