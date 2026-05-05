from __future__ import annotations

from typing import Any

from .config import AgentConfig, OpponentSpec


_LIBRARY: dict[str, dict[str, Any]] = {
    "nearest_resource": {
        "label": "nearest_resource",
        "provider": "builtin",
        "model": "nearest_resource",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "greedy_collector"},
    },
    "opponent_shadow": {
        "label": "opponent_shadow",
        "provider": "builtin",
        "model": "opponent_shadow",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "contester"},
    },
    "sweep_rows": {
        "label": "sweep_rows",
        "provider": "builtin",
        "model": "sweep_rows",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "coverage_sweeper"},
    },
    "center_rush": {
        "label": "center_rush",
        "provider": "builtin",
        "model": "center_rush",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "center_rush"},
    },
    "corner_guard": {
        "label": "corner_guard",
        "provider": "builtin",
        "model": "corner_guard",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "corner_guard"},
    },
    "resource_denier": {
        "label": "resource_denier",
        "provider": "builtin",
        "model": "resource_denier",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "resource_denier"},
    },
    "edge_patrol": {
        "label": "edge_patrol",
        "provider": "builtin",
        "model": "edge_patrol",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "edge_patrol"},
    },
    "diagonal_probe": {
        "label": "diagonal_probe",
        "provider": "builtin",
        "model": "diagonal_probe",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "diagonal_probe"},
    },
    "safe_collector": {
        "label": "safe_collector",
        "provider": "builtin",
        "model": "safe_collector",
        "temperature": 0.0,
        "max_tokens": 1,
        "regenerate_each_epoch": False,
        "metadata": {"archetype": "safe_collector"},
    },
}


def available_library_keys() -> list[str]:
    return sorted(_LIBRARY)


def resolve_opponent_spec(spec: OpponentSpec, *, slot_name: str) -> tuple[AgentConfig, str, dict[str, Any]]:
    merged: dict[str, Any] = {}
    if spec.library_key:
        if spec.library_key not in _LIBRARY:
            raise ValueError(f"Unknown opponent library key: {spec.library_key}")
        merged.update(_LIBRARY[spec.library_key])
    explicit = spec.__dict__.copy()
    metadata = dict(merged.get("metadata", {}))
    metadata.update(explicit.get("metadata", {}))
    for key, value in explicit.items():
        if key == "metadata":
            continue
        if value not in ("", None, []):
            merged[key] = value
    merged["metadata"] = metadata
    label = str(merged.get("label") or merged.get("library_key") or merged.get("model") or slot_name)
    agent = AgentConfig(
        name=slot_name,
        provider=str(merged.get("provider", "builtin")),
        model=str(merged.get("model", "nearest_resource")),
        system_prompt=str(merged.get("system_prompt", "You write deterministic Python for a grid-game agent.")),
        temperature=float(merged.get("temperature", 0.0)),
        max_tokens=int(merged.get("max_tokens", 1)),
        regenerate_each_epoch=bool(merged.get("regenerate_each_epoch", False)),
    )
    return agent, label, metadata
