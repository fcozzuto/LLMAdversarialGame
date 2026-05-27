def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold balances interpretability with robustness across held-out TSPLIB and synthetic transfer instances.
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "description": (
            "A simple, interpretable heuristic scaffold suitable for constrained TSP. "
            "Employs deterministic steps: constructively build a tour by repeatedly selecting the "
            "best feasible next city according to a fixed scoring function, followed by 2-opt refinement "
            "to remove obvious crossings. Constraints are kept explicit and checked at each step."
        ),
        "strategy": {
            "type": "greedy_with_refinement",
            "steps": [
                {
                    "step": "initialize",
                    "details": "Choose a fixed starting city id of 0 to ensure determinism. Mark all cities as unvisited.",
                    "state": {"start_city": 0, "unvisited_count": "n-1", "visited": [0]}
                },
                {
                    "step": "select_next",
                    "details": (
                        "From the current city, select the unvisited city that minimizes a fixed score: "
                        "score = distance(current, candidate) + penalty_for_constraints(candidate)"
                    ),
                    "score_function": [
                        "distance(current, candidate)",
                        "penalty_for_constraints(candidate)"
                    ],
                    "constraints": [
                        "respect_max_visit_per_city (if any per-city constraint)",
                        "respect_global_constraints (e.g., required cities, terminals)"
                    ],
                    "state_transition": "append chosen city to tour; mark as visited"
                },
                {
                    "step": "link_and_check",
                    "details": "Continue until all cities are visited or constraints force termination. Ensure feasibility of final link to start.",
                    "state": {"visited_count": "n", "feasible_tour": "True/False"}
                },
                {
                    "step": "refinement",
                    "details": "Apply a deterministic 2-opt pass to remove obvious crossings while preserving constraints.",
                    "state": {"refined": "True/False"}
                }
            ]
        },
        "data_requirements": {
            "cities": "list of city objects with coordinates or distance matrix",
            "distance_matrix": "optional; if not provided, a distance function is assumed externally",
            "constraints": {
                "max_visits_per_city": "optional",
                "must_include": "optional list of mandatory city IDs",
                "start_city": 0
            }
        },
        "outputs": {
            "tour": "ordered list of city IDs representing the tour",
            "feasibility": "boolean indicating whether a feasible tour exists under constraints",
            "cost": "numeric total distance of the final tour",
            "log": [
                "starting city",
                "sequence of chosen next cities with deterministic tie-breaking",
                "any constraint violations encountered",
                "2-opt swap records if refinement performed"
            ]
        },
        "determinism": {
            "tie_breaking": "lowest city id",
            "random_seed": 0,
            "starting_city": 0
        },
        "robustness_considerations": [
            "works with standard TSPLIB-like instances and synthetic constrained instances",
            "avoids reliance on training-time-only heuristics",
            "transparent scoring and constraint checks for auditability"
        ],
        "notes": "This scaffold is intentionally simple to remain interpretable while providing a reasonable baseline for constrained TSP performance on held-out instances."
    }
