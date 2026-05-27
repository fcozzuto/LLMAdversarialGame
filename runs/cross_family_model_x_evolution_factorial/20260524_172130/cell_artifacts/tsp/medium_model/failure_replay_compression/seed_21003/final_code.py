def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic with a focus on
    # robustness and interpretability. This uses a simple, transparent structure
    # that can be extended with additional constraints or transfer evaluations.

    heuristic = {
        "name": "deterministic_constrained_tsp_scaffold",
        "version": 1,
        "description": (
            "A robust, interpretable heuristic scaffold for constrained TSP. "
            "Does not rely on external imports and is designed for clear "
            "transferability across TSPLIB-like and synthetic instances."
        ),
        "technique": "failure_replay_compression",
        "replay_archive": {
            "entries": [],
            "note": "No replay entries available yet."
        },
        "components": {
            "problem_representation": {
                "type": "symmetric_distance_matrix",
                "constraints": ["max_visit_per_city = 1", "subtour_elimination"],
                "preprocessing": ["triangle_inequality_check"],
            },
            "initialization": {
                "method": "nearest_neighbor_linearized",
                "start_city": "deterministic_min_index",
                "tie_breaker": "city_index",
            },
            "construction": {
                "step": "greedy_feasible_extension",
                "local_search": {
                    "enabled": True,
                    "strategy": "2opt",
                    "max_restarts": 1,
                    "swap_limit": 50
                }
            },
            "feasibility_checks": {
                "degree_constraint": 2,
                "subtour_elimination": True,
                "capacity_constraints": None
            },
            "termination": {
                "when": "no_improvement_after_iters",
                "max_iters": 100
            }
        },
        "transfer_fidelity": {
            "training_focus": ["construction_consistency", "feasibility", "tight_bound_estimates"],
            "robustness": {
                "out_of_sample_eval": True,
                "synthetic_transfers": True
            },
            "interpretability": {
                "path_dependency": True,
                "decision_trace": True
            }
        },
        "outputs": {
            "routes": "list_of_city_sequences",
            "cost": "float",
            "feasibility_report": "dictionary",
            "debug_log": "optional"
        },
        "parameters": {
            "max_visits_per_city": 1,
            "subtour_elimination": True,
            "allow_zero_cost_edges": False,
            "epsilon": 1e-9
        }
    }

    return heuristic
