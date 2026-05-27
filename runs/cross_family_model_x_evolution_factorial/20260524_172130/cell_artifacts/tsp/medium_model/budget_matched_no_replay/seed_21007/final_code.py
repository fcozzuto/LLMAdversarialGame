def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP (CTSP) with a
    # budget_matched_no_replay strategy. This scaffold emphasizes robustness
    # on held-out TSPLIB-like instances and synthetic transfers, while keeping
    # the policy simple and interpretable.
    return {
        "name": "ctsp_budget_matched_no_replay",
        "description": (
            "Deterministic CTSP heuristic using a budget-aware, non-replay "
            "construction with greedy feasibility and simple edge-budget checks."
        ),
        "technique": "budget_matched_no_replay",
        "budget_strategy": {
            "total_budget": None,  # No fixed global budget; uses per-step budget pacing
            "per_node_budget": 1.0,  # unit budget per decision step
            "budget_allocation": "greedy_expand_until_feasible",
            "budget_adjustment": "static",  # no dynamic memory-based adjustments
        },
        "feasibility_rules": {
            "must_include_city": False,
            "required_edges_count": None,  # allow variable-length tours with constraints
            "subtour_elimination": True,
            "time_window_constraints": False,
            "capacity_constraints": False,
        },
        "edge_ordering": {
            "strategy": "greedy_by_cost_and_feasibility",
            "cost_function": "euclidean_distance",  # deterministic metric
        },
        "constraints_handling": {
            "node_representation": "indices",
            "edge_representation": "pair_of_indices",
            "symmetry": True,
            "geometric_preprocessing": True,
            "hard_tour_completion": True,
        },
        "heuristic_steps": [
            "initialize_tour_with_start_node_at_index_0",
            "expand_tour_by_selecting_cheapest_feasible_edge",
            "check_subtour_elimination_and_capacity_limits",
            "if_no_feasible_extension_then_backtrack_one_step",
            "finish_tour_when_all_nodes_visited_or_no_extension",
        ],
        "scalability_notes": {
            "expected_inst_types": ["synthetic_transfer_like", "TSPLIB_like"],
            "typical_instance_sizes": {"min": 20, "max": 200},
            "runtime_characteristics": "polynomial_time_greedy_with_feasibility_checks",
        },
        "interpretability": {
            "explanation": "edge choices based on deterministic cost and feasibility; no learned components",
            "traceability": True,
            "determinism": True,
        },
        "output_format": {
            "tour": "list_of_node_indices_in_order",
            "tour_cost": "sum_of_distances_along_tour",
            "feasibility_flags": "subtour_elimination_satisfied_boolean",
        },
        "notes": (
            "This scaffold avoids replay memory, failure memory, or compression. "
            "It remains deterministic and interpretable, suitable for evaluation on "
            "held-out TSPLIB-like and synthetic transfer instances."
        ),
        "version": 1
    }
