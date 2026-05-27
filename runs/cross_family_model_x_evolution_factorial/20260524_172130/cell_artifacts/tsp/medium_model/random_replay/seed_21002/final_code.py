def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # - No external imports
    # - Designed for robust evaluation on held-out TSPLIB and synthetic transfers
    # - Simple, interpretable mechanisms with deterministic behavior

    scaffold = {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": 1,
        "description": "Robust, interpretable heuristic scaffold for constrained TSP with deterministic behavior.",
        "technique": "random_replay",
        "strategy": {
            "initialization": {
                "seed": 42,  # deterministic seed for reproducibility
                "start_node_choice": "smallest_index",
                "initial_route_build": "greedy_by_distance_with_constraints",
            },
            "constraint_handling": {
                "node_constraints": "per_node_limits",  # e.g., max visits, capacity, or other per-node rules
                "edge_constraints": "allow_if_feasible",  # only add edges that keep feasibility
                "global_constraints": [
                    "subtour_elimination",
                    "budget_or_time_bound",
                ],
            },
            "selection_rule": {
                "method": "lexicographic_min_increase",
                "priority": ["distance", "constraint_violation", "unvisited_neighbors"],
                "tie_breaker": "node_index",
            },
            "replay_mechanics": {
                "episodes": 0,  # no replay archive entries yet; deterministic placeholder
                "replay_window": 0,
                "random_replay": False,  # explicit determinism; no stochastic replay
            },
            "local_search": {
                "enable": True,
                "moves": ["swap", "2-opt", "or-opt"],
                "limit_per_iteration": 5,
                "improvement_acceptance": "improve_only",
            },
            "transferability": {
                "tsplib_robustness": True,
                "synthetic_transfer": True,
                "evaluation_focus": ["held_out_tsplib", "synthetic_transfer"],
            },
            "output": {
                "format": "dictionary",
                "fields": [
                    "route",
                    "cost",
                    "feasibility",
                    "runtime_ms",
                    "constraints_satisfied",
                ],
            },
        },
        "deterministic_controls": {
            "random_seed": 42,
            "precompute_distance_matrix": True,
            "normalize_costs": True,
            "order_by": "node_index",
        },
        "notes": [
            "This scaffold intentionally avoids replay archives and randomization for reproducibility.",
            "It favors interpretability and generalization by using simple constraint-aware heuristics and deterministic local search.",
        ],
    }

    return scaffold
