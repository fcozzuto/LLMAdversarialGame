def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic.
    # Designed to be robust on held-out TSPLIB-like instances and synthetic transfers,
    # while remaining interpretable and not overly complex.
    heuristic = {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": "1.0",
        "description": (
            "Deterministic heuristic scaffold implementing a simple, interpretable "
            "construction with feasibility checks for constrained TSP problems."
        ),
        "technique": "failure_replay_compression",
        "comments": [
            "No replay archive entries currently available for failure_replay_compression.",
            "Deterministic seed-less behavior is achieved via fixed tie-breaking rules.",
            "Focus on robustness across TSPLIB-like and synthetic transfer instances.",
        ],
        "parameters": {
            "seed": 0,
            "greedy_tie_breaker": "lexicographic",  # options: lexicographic, degree, nearest
            "max_iterations": 5,
            "feasibility_checks": True,
            "city_ordering": "degree_asc_then_index_desc",
        },
        "instance_handling": {
            "supported_types": ["tsplib_like", "synthetic_transfer"],
            "constrains": {
                "capacity": None,  # placeholder for constrained capacity; None means unconstrained
                "precedence": False,
                "subtour_elimination": "simple_marekos",
            },
            "robustness": {
                "recovery_on_infeasibility": True,
                "fallback_to_penalty_if_infeasible": False,
            },
        },
        "construction_routine": {
            "step_sequence": [
                "initialize_route_with_start_city",
                "build_feasible_partial_paths",
                "apply_feasibility_checks_and_fix",
                "complete_route_with_least_cost_extension",
                "validate_and_finalize_route",
            ],
            "step_details": {
                "initialize_route_with_start_city": {
                    "description": "Choose a deterministic start city (index 0).",
                    "action": "route = [0]"
                },
                "build_feasible_partial_paths": {
                    "description": "Extend the route by repeatedly selecting the next feasible city.",
                    "action": (
                        "For candidate cities not yet visited, evaluate feasibility under constraints; "
                        "choose the best according to the fixed tie-breaker."
                    ),
                },
                "apply_feasibility_checks_and_fix": {
                    "description": "If a move violates constraints, skip or apply minimal fix.",
                    "action": "If no feasible candidate, backtrack to last feasible prefix."
                },
                "complete_route_with_least_cost_extension": {
                    "description": "Finish the tour by inserting remaining cities in deterministic order.",
                    "action": "Append remaining cities in index order to minimize total cost under feasibility."
                },
                "validate_and_finalize_route": {
                    "description": "Ensure all constraints satisfied and route is closed.",
                    "action": "Compute total_cost and assert feasibility; return route."
                }
            }
        },
        "cost_model": {
            "edge_cost": "distance_between_cities",
            "penalty_for_infeasibility": 0.0,
            "tie_breaking": "lexicographic_on_indices",
        },
        "outputs": {
            "route": "list of city indices forming a feasible tour",
            "total_cost": "numeric total distance",
            "feasibility": "boolean indicating if a feasible tour was found",
        }
    }
    return heuristic
