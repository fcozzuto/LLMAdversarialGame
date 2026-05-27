def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic, interpretable TSP heuristic scaffold with solid transfer potential across held-out TSPLIB and synthetic instances.",
        "constraints": {
            "problem_type": "constrained_tsp",
            "valid_actions": ["select_next_city_by_distance", "respect_constraints", "build_partial_path"],
            "hard_constraints": [
                "do_not_revisit_cities",
                "respect_required_visits_if_specified",
                "honor_city_opening_and_closing_constraints_if_present",
            ],
            "soft_preferences": [
                "prefer_nearby_next_city_to reduce incremental cost",
                "prefer_city_with_minimal_additional_constraint_violation",
            ],
        },
        "heuristic_core": {
            "strategy": "greedy_with_constraint_checks",
            "scoring": {
                "base_score": 1.0,
                "distance_penalty_weight": 1.0,
                "constraint_violation_penalty": 100.0,
                "priority_bonus": 0.1,
            },
            "selection_rule": [
                "for candidate in candidate_cities_in_remaining: ",
                "    if not violates_constraints(candidate):",
                "        score = -distance(current, candidate) + soft_preferences(candidate)",
                "        if score > best_score:",
                "            best_candidate = candidate",
                "            best_score = score",
            ],
            "tie_breaker": "lowest_distance_then_least_constraints_violated",
            "rollback_on_failure": True,
        },
        "transitions": {
            "start": {
                "choose_seed_city": "deterministic_seed_city",
                "seed_assignment": "predefined_order",
            },
            "growth_step": "select_next_city_by_distance",
            "termination": {
                "condition": "all_required_visits_completed_or_no_feasible_extension",
                "fallback": "best_partial_path_so_far"
            },
        },
        "robustness_and_transfer": {
            "robustness_mechanisms": [
                "deterministic_seed_and_order",
                "explicit_constraint_handling",
                "fallback_to_partial_solution_if_no_feasible_extension",
            ],
            "transfer_support": {
                "tsplib_heldout_strategy": "evaluate_on_diverse_location_sets",
                "synthetic_transfer_focus": [
                    "varied_capacity_constraints",
                    "variable_visit_requirements",
                    "mixed_metric_distances"
                ],
            },
        },
        "interpretability": {
            "rationale_explanation": "path chosen via transparent greedy with explicit constraint checks and deterministic tie-breaking",
            "debugging_hooks": [
                "log_current_city",
                "log_candidate_scores",
                "log_constraint_violations",
            ],
        },
        "failure_replay_compression": {
            "archive": "none_yet",
            "replay_entries": [],
            "compression_strategy": "none",
        },
        "notes": [
            "This scaffold is intentionally simple and deterministic to ease analysis and transfer evaluation.",
            "It provides a clear path for extending with more sophisticated scoring or additional constraint types while preserving interpretability."
        ],
        "__meta__": {
            "authors": ["scaffold_author"],
            "last_review": "2026-05-27",
            "risk_factors": ["low complexity, moderate transferability, no learned components"],
        },
    }
