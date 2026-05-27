def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP with a single-shot approach.
    # This scaffold favors readability and robustness across held-out TSPLIB-like instances
    # and synthetic transfer scenarios without relying on external data or imports.
    heuristic = {
        # Basic problem definition scaffold
        "problem": {
            "name": "constrained_tsp_single_shot",
            "version": 1,
            "description": "Deterministic single-shot heuristic for constrained TSP with interpretable steps.",
            "constraints": [
                "visit_each_city_once",
                "precedence_or_limit_constraints_if_any",
                "subtour_elimination",
            ],
        },
        # Step-wise construction strategy; deterministic seed for reproducibility
        "seed": 1,
        "construction": {
            "method": "nearest_neighbor_with_constraints",
            "strategy": [
                "start_at_fixed_city_0",
                "always_pick_next_city_with_minimum_distance_that_satisfies_all_constraints",
                "if_no_feasible_move, terminate_with_subtour_check",
            ],
            "tie_breaker": "lower_index",
            "max_steps": 1000,  # safe bound for typical TSPLIB sizes
        },
        # Constraint handling
        "constraints": {
            "type": "hard_and_soft",
            "hard": [
                "each_city_visited_at_m_must_be_in_tour_once",
                "no_subtours_of_incomplete_set",
            ],
            "soft": [
                "minimize_total_distance",
                "respect_precedence_constraints_if_present",
            ],
        },
        # Validation and repair
        "validation": {
            "subtour_elimination": "implemented_during_construction_via_local_checks",
            "feasibility_check": "tour_covers_all_cities_and_returns_to_start",
            "distance_objective": "total_distance_calculated_on_complete_tour",
        },
        # Output form
        "output": {
            "tour": "list_of_city_indices_in_order",
            "distance": "float_total_distance_of_tour",
            "feasible": "bool_indicating_if_tour_is_feasible",
            "summary": "string_description_of_the_result",
        },
        # Robustness considerations
        "robustness": {
            "generalization_focus": [
                "use deterministic rules so performance is predictable across synthetic and TSPLIB-like instances",
                "avoid instance-specific heuristics",
            ],
            "transfer_ready": {
                "synthetic_scaling": "works with varying city counts",
                "held_out_tsplib": "defaults to standard metrics and deterministic path",
            },
        },
        # Complexity and interpretability
        "interpretability": {
            "explanation": "each_step_is_explicit_and_deterministic",
            "parameters": ["seed", "method", "constraints"],
        },
        # Determinism
        "determinism": {
            "reproducibility": True,
            "random_components": False,
        },
    }
    return heuristic
