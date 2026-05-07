from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re

from llm_grid_battle.config import SuiteConfig


TRANSFER_OUTPUT_ROOT = "runs/transfer_suite"
TRANSFER_CONFIG_DIR = Path("configs/transfer_suite")


def _deep_copy(value):
    return copy.deepcopy(value)


def _training_pool(mode: str, labels: list[str]) -> list[dict[str, str]]:
    if mode == "fixed_predator":
        return [{"library_key": labels[0]}]
    return [{"library_key": label} for label in labels]


def _slugify_recipe_name(recipe_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", recipe_name.lower()).strip("_")
    return slug or "transfer_recipe"


def _environment_templates(mode: str) -> list[dict]:
    return [
        {
            "name": "transfer_resource_collection_denial",
            "seed": 801,
            "environment": {"name": "resource_collection"},
            "map": {"width": 8, "height": 8, "resource_count": 12, "obstacle_count": 2, "resample_each_epoch": True},
            "game": {"epochs": 100, "max_turns": 80, "move_timeout_seconds": 0.35, "tie_break": "split"},
            "curriculum": {
                "opponent_pool": _training_pool(mode, ["nearest_resource", "opponent_shadow", "sweep_rows", "resource_denier"]),
                "evaluation": {
                    "enabled": True,
                    "games_per_opponent": 5,
                    "holdout_opponents": [
                        {"library_key": "center_rush"},
                        {"library_key": "corner_guard"},
                        {"library_key": "edge_patrol"},
                        {"library_key": "diagonal_probe"},
                        {"library_key": "safe_collector"},
                    ],
                },
            },
            "metadata": {"transfer_environment": "resource_collection"},
        },
        {
            "name": "transfer_pursuit_evasion",
            "seed": 802,
            "environment": {
                "name": "pursuit_evasion",
                "role_assignments": {"agent_a": "pursuer", "agent_b": "evader"},
                "capture_radius": 0,
                "capture_points": 10.0,
                "survival_points_per_turn": 0.15,
                "capture_ends_game": True,
            },
            "map": {"width": 8, "height": 8, "resource_count": 0, "obstacle_count": 2, "resample_each_epoch": True},
            "game": {"epochs": 100, "max_turns": 60, "move_timeout_seconds": 0.35, "tie_break": "split"},
            "curriculum": {
                "opponent_pool": _training_pool(mode, ["evasion_corner", "evasion_wall_runner", "evasion_zigzag", "pursuit_direct"]),
                "evaluation": {
                    "enabled": True,
                    "games_per_opponent": 5,
                    "holdout_opponents": [
                        {"library_key": "evasion_center_weave"},
                        {"library_key": "evasion_axis_flip"},
                        {"library_key": "evasion_midline_dodge"},
                    ],
                },
            },
            "metadata": {"transfer_environment": "pursuit_evasion"},
        },
        {
            "name": "transfer_territory_control",
            "seed": 803,
            "environment": {
                "name": "territory_control",
                "territory_flip_on_entry": True,
                "territory_control_bonus_interval": 10,
                "territory_control_bonus": 0.5,
            },
            "map": {"width": 8, "height": 8, "resource_count": 0, "obstacle_count": 2, "resample_each_epoch": True},
            "game": {"epochs": 100, "max_turns": 70, "move_timeout_seconds": 0.35, "tie_break": "split"},
            "curriculum": {
                "opponent_pool": _training_pool(mode, ["territory_sweeper", "territory_center_claim", "territory_counterclaim", "territory_edge_claim"]),
                "evaluation": {
                    "enabled": True,
                    "games_per_opponent": 5,
                    "holdout_opponents": [
                        {"library_key": "territory_diagonal_claim"},
                        {"library_key": "territory_quadrant_claim"},
                        {"library_key": "territory_far_corner_claim"},
                    ],
                },
            },
            "metadata": {"transfer_environment": "territory_control"},
        },
    ]


def build_transfer_suite(
    *,
    factorial_config: Path,
    recipe_name: str,
    output_path: Path | None = None,
    output_root: str | None = None,
) -> Path:
    suite = SuiteConfig.load(factorial_config)
    source = next((condition for condition in suite.conditions if condition.name == recipe_name), None)
    if source is None:
        raise ValueError(f"Recipe condition not found: {recipe_name}")
    recipe_slug = _slugify_recipe_name(recipe_name)
    resolved_output_path = output_path or (TRANSFER_CONFIG_DIR / f"{recipe_slug}.json")
    resolved_output_root = output_root or f"{TRANSFER_OUTPUT_ROOT}/{resolved_output_path.stem}"
    source_dict = source.to_dict()
    base_curriculum = _deep_copy(source_dict["curriculum"])
    base_curriculum.setdefault("selection", {})
    base_curriculum["selection"]["holdout_opponent_count"] = 0
    base_curriculum["selection"]["holdout_games_per_opponent"] = 0
    base_curriculum["selection"]["holdout_score_tolerance"] = 0.75

    defaults = {
        "seed": int(source.seed),
        "output_root": resolved_output_root,
        "agents": _deep_copy(source_dict["agents"]),
        "feedback": _deep_copy(source_dict["feedback"]),
        "observation": _deep_copy(source_dict["observation"]),
        "judge": _deep_copy(source_dict["judge"]),
        "generation": _deep_copy(source_dict["generation"]),
        "curriculum": base_curriculum,
        "metadata": {
            **_deep_copy(source_dict.get("metadata", {})),
            "suite_family": "transfer_suite",
            "study_phase": "phase_3",
            "primary_endpoint": "holdout_win_rate",
            "recipe_source_condition": recipe_name,
            "environment_family": "multi_environment_transfer",
        },
    }

    mode = str(base_curriculum.get("mode", "rotating_opponents"))
    conditions = []
    for template in _environment_templates(mode):
        condition = {
            "name": template["name"],
            "seed": template["seed"],
            "map": template["map"],
            "game": template["game"],
            "environment": template["environment"],
            "curriculum": template["curriculum"],
            "metadata": {
                **defaults["metadata"],
                **template["metadata"],
            },
        }
        conditions.append(condition)

    output = {"defaults": defaults, "conditions": conditions}
    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return resolved_output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a cross-environment transfer suite from a winning factorial recipe.")
    parser.add_argument("--factorial-config", default="configs/factorial_holdout_suite/01_factorial_holdout.json")
    parser.add_argument("--recipe", required=True, help="Condition name from the factorial suite to treat as the best curriculum recipe.")
    parser.add_argument("--output", help="Optional output config path. Defaults to configs/transfer_suite/<recipe>.json.")
    parser.add_argument("--output-root", help="Optional runs root. Defaults to runs/transfer_suite/<config-stem>.")
    args = parser.parse_args()

    output_path = build_transfer_suite(
        factorial_config=Path(args.factorial_config),
        recipe_name=args.recipe,
        output_path=Path(args.output) if args.output else None,
        output_root=args.output_root,
    )
    print(output_path)


if __name__ == "__main__":
    main()
