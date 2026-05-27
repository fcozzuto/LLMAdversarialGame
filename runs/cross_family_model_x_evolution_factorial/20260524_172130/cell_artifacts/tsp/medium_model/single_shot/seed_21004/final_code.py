def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "description": "Deterministic single-shot TSP heuristic scaffold with constraints, designed for robustness on held-out TSPLIB and synthetic transfer instances.",
        "version": "1.0",
        "technique": "single_shot",
        "properties": {
            "constraints": {
                "time_limit_seconds": 60,
                "max_runtime_per_step_ms": 5,
                "vehicle_capacity": None,  # not used in single-vehicle TSPLIB style by default
                "subtour_elimination": True,
                "must_visit_all_nodes": True
            },
            "scoring": {
                "objective": "minimize_total_distance",
                "balance": {
                    "penalty_for_constraint_violation": 1000.0,
                    "penalty_for_disconnected": 50.0
                }
            },
            "initialization": {
                "method": "nearest_neighbor_with_constraints",
                "seed": 0
            },
            "neighborhood": {
                "step": "2-opt",
                "local_search_limit": 1000
            },
            "transfer_factors": {
                "robustness_hint_against_holdout": True,
                "synthetic_transfer_consideration": True
            },
            "interpretability": {
                "description": "Solution assembled via a deterministic, constrained nearest-neighbor tour with optional 2-opt refinements; no learned weights or opaque components.",
                "complexity_bound": "O(n^2) for construction; O(n^2) for 2-opt refinement in worst case"
            },
            "outputs": {
                "tour": None,
                "distance": None,
                "feasible": None,
                "log": None
            }
        },
        "data_requirements": {
            "tsplib_like": True,
            "synthetic_transfer_ready": True,
            "expected_features": [
                "node_coords",
                "node_id",
                "distance_matrix_or_coords",
                "time_window_or_capacity_constraints_optional"
            ]
        },
        "robustness": {
            "holdout_evaluation": {
                "expected_holdout_robustness": "moderate",
                "fallback_behaviors": [
                    "if_time_exceeded_return_greedy_path",
                    "if_constraints_violate_then_shorten_and_restart"
                ]
            }
        },
        "determinism": {
            "seed": 0
        }
        }
