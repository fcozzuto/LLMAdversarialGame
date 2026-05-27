def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a "budget_matched_no_replay" approach.
    # This scaffold avoids external imports and provides interpretable components.
    heuristic = {
        "name": "budget_matched_no_replay",
        "version": 1,
        "description": (
            "Deterministic constrained TSP scaffold with a budget-aware edge selection "
            "strategy. Prioritizes robustness across TSPLIB-like instances and synthetic "
            " transfers while staying interpretable."
        ),
        "parameters": {
            # Global budget controlling allowed total distance for a tour.
            "budget": {
                "type": "float",
                "default": 1.0,  # relative budget w.r.t. a reference tour length
                "description": "Fractional budget cap relative to a reference tour length."
            },
            # Preference for including high-utility edges based on simple features.
            "edge_priority": {
                "type": "string",
                "default": "distance_inverse,degree_balance",
                "description": (
                    "Simple deterministic feature-based priority string. "
                    "Supported tokens: distance_inverse, degree_balance, incident_weight."
                )
            },
            # Deterministic tie-breaking seed (no randomness).
            "tie_breaker": {
                "type": "string",
                "default": "lexicographic",
                "description": "Deterministic tie-breaking rule."
            },
            # Validation settings to ensure scalability on TSPLIB-like data.
            "validation": {
                "type": "dict",
                "default": {
                    "max_nodes": 500,
                    "max_runtime_seconds": 2,
                    "constrain_to_triangle_inequality": True
                },
                "description": "Simple runtime and size checks to keep interpretation straightforward."
            },
        },
        "strategy": {
            "high_level": "construct a Hamiltonian path with budget-aware pruning using a deterministic edge ranking.",
            "phases": [
                {
                    "name": "initial_ordering",
                    "description": (
                        "Create a deterministic visiting order by sorting nodes by their identifier."
                    ),
                    "step": [
                        {"action": "sort_nodes_by_id"},
                        {"action": "build_initial_path_start", "params": {"start_node": 0}}
                    ]
                },
                {
                    "name": "budget_pruning",
                    "description": (
                        "Iteratively attempt to extend the path by adding the next best edge according to the "
                        "edge_priority criteria, skipping edges that would exceed the budget."
                    ),
                    "step": [
                        {"action": "evaluate_candidate_edges", "params": {"mode": "greedy"}}
                    ]
                },
                {
                    "name": "finalize",
                    "description": (
                        "If the path is not a cycle, close it by connecting end to start if budget allows; "
                        "otherwise, return the best feasible path found."
                    ),
                    "step": [
                        {"action": "close_path_if_possible"},
                        {"action": "return_best_feasible_path"}
                    ]
                }
            ]
        },
        "edge_evaluation": {
            "description": "Deterministic scoring of candidate edges using simple features.",
            "features": [
                "distance_inv",         # 1 / distance
                "incident_degree_diff", # balance at endpoints
                "shared_budget_fraction"  # remaining budget impact
            ],
            "scoring": [
                {"weight": 1.0, "feature": "distance_inv"},
                {"weight": 0.5, "feature": "incident_degree_diff"},
                {"weight": 0.25, "feature": "shared_budget_fraction"}
            ],
            "tie_breaker": "lexicographic"
        },
        "budget_model": {
            "type": "relative_budget",
            "definition": (
                "budget is applied as a cap on cumulative distance. Edge additions must not "
                "cause the current_distance + edge_distance to exceed budget * reference_length."
            ),
            "reference_length_source": "assumed_reference",  # placeholder for deterministic reference
        },
        "robustness_properties": [
            "tsplib_compatible",
            "synthetic_transfer_friendly",
            "interpretability",
            "deterministic",
        ],
        "notes": "This scaffold emphasizes robustness across standard benchmarks and synthetic transfers while maintaining simplicity and determinism."
    }
    return heuristic
