from __future__ import annotations

from typing import Any


def build_generation_prompt(*, context: dict[str, Any], max_non_empty_lines: int, max_characters: int) -> str:
    instance_summaries = context["train_instance_summaries"]
    baseline_summaries = context["baseline_summaries"]
    incumbent = context.get("incumbent_summary")
    worst_cases = context.get("worst_cases", [])
    prompt_lines = [
        "Design a deterministic CVRP solver in raw Python.",
        "Treat this as mutation-based solver evolution, not a fresh rewrite.",
        "Return only raw Python source code.",
        "The first line must be exactly: def solve_cvrp(instance):",
        "Do not use markdown fences.",
        "Do not use import statements of any kind.",
        "Do not access files, network, environment variables, or instance names.",
        f"- Stay within {max_non_empty_lines} non-empty lines when feasible.",
        f"- Stay within {max_characters} characters when feasible.",
        "- Oversized submissions are rejected; prefer a compact solver with only a few short helper functions.",
        "- Prefer 1 to 3 focused edits to the incumbent instead of a whole new design.",
        "- Preserve the incumbent structure, helper functions, and return path unless a specific change is necessary.",
        "- If you are unsure how to improve the solver safely, return the incumbent unchanged rather than emitting broken code.",
        "",
        "Your solver must return a full solution as a list of routes.",
        "Each route must be a Python list of zero-based customer node ids.",
        "Do not include the depot in any route.",
        "",
        "You are allowed to evolve:",
        "- constructive route-building logic",
        "- savings-style merges",
        "- insertion and repair logic",
        "- intra-route or inter-route local search",
        "- destroy/repair cycles",
        "- restart or multi-start logic",
        "- instance-conditioned control based on descriptors",
        "",
        "You are not allowed to use:",
        "- imports or external libraries",
        "- OR-Tools or any hidden solver",
        "- hard-coded instance-name rules",
        "- stochastic behavior or randomness",
        "",
        "Runtime input schema:",
        "- instance['customer_ids']: list[int]",
        "- instance['depot_index']: int",
        "- instance['demands']: list[int]",
        "- instance['capacity']: int",
        "- instance['vehicle_count_hint']: int",
        "- instance['coordinates']: list[[x, y]]",
        "- instance['distance_matrix']: list[list[int]]",
        "- instance['nearest_neighbors']: dict[str, list[int]]",
        "- instance['descriptors']: summary features",
        "",
        "Training instances:",
    ]
    for index, item in enumerate(instance_summaries, start=1):
        prompt_lines.append(
            "- train_case_{index}: {customer_count} customers, vehicle hint {vehicle_count_hint}, demand pressure {demand_pressure}, "
            "structure {structure_class}, corridor {corridor_score}, clusteredness {clusteredness_score}, trap {nearest_neighbor_trap_score}".format(
                index=index,
                **item
            )
        )
    prompt_lines.extend(["", "Reference baselines on the same training panel:"])
    for item in baseline_summaries:
        prompt_lines.append(
            "- {baseline_name}: feasibility {feasibility_rate}, penalized gap {mean_penalized_gap}, feasible gap {mean_feasible_gap}".format(
                **item
            )
        )
    if incumbent is not None:
        prompt_lines.extend(
            [
                "",
                "Current incumbent summary:",
                "- training feasibility {feasibility_rate}, penalized gap {mean_penalized_gap}, feasible gap {mean_feasible_gap}, runtime ms {mean_runtime_ms}".format(
                    **incumbent
                ),
                "- Make small, targeted changes that improve the worst training cases without destabilizing the rest of the solver.",
            ]
        )
    previous_code = str(context.get("incumbent_code", "")).strip()
    if previous_code:
        prompt_lines.extend(
            [
                "",
                "Current incumbent solver code:",
                previous_code,
            ]
        )
    if worst_cases:
        prompt_lines.extend(["", "Worst current training cases to fix:"])
        for index, item in enumerate(worst_cases[:5], start=1):
            prompt_lines.append(
                "- train_case_issue_{index}: family={family}, feasible={feasible}, penalized gap {penalized_gap}, errors={errors}".format(
                    index=index,
                    **item
                )
            )
    prompt_lines.extend(
        [
            "",
            "Target behavior:",
            "- maximize feasibility first",
            "- then reduce objective gap on the training instances",
            "- keep edits small enough that the code stays syntactically complete",
            "- keep the solver interpretable and deterministic",
            "",
            "Return only Python source code for solve_cvrp(instance).",
        ]
    )
    return "\n".join(prompt_lines)
