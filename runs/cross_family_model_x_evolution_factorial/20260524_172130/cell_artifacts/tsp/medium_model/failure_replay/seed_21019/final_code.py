def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold focuses on robustness across held-out TSPLIB-like instances
    # and synthetic transfer scenarios, while keeping interpretation and simplicity.
    heuristic = {
        "name": "deterministic_constrained_tsp_scaffold",
        "version": "1.0",
        "description": "A robust, interpretable constrained TSP heuristic scaffold with deterministic behavior and simple transfer capabilities.",
        "parameters": {
            "seed": 42,
            "max_neighbors": 8,
            "edge_cost_model": "euclidean",
            "constraint_handling": "precedence_and_capacity",
            "tour_completion": "nearest_insertion_by_cost",
            "repair": {
                "enabled": True,
                "method": "2-opt",
                "max_iterations": 1000
            },
            "termination": {
                "iterations_without_improvement": 200,
                "time_limit_seconds": None
            }
        },
        "structure": {
            "initialization": {
                "type": "seeded_random_spanning_path",
                "seed_position": 0
            },
            "construction": {
                "method": "greedy_nearest_with_constraints",
                "neighbors_considered": "$max_neighbors",  # reference to parameter
                "cost_function": "edge_cost_model"
            },
            "insertions": {
                "strategy": "insert_min_increment",
                "tiebreaker": "lower_constraint_violation",
                "considered_nodes": "all_unvisited_with_validity_check"
            },
            "repair_and_optimize": {
                "local_search": "2-opt",
                "start_from": "current_tour",
                "iterations": "$max_iterations"  # reference to parameter
            }
        },
        "constraints": {
            "type": "precedence_and_capacity",
            "precedence_rules": [],
            "capacity_limit": None,
            "time_window": None
        },
        "transfer": {
            "robustness_focus": True,
            "test_set": {
                "held_out_tsplib_like": True,
                "synthetic_transfer": True
            },
            "evaluation": {
                "metrics": ["tour_cost", "feasibility", "constraint_violations", "runtime"],
                "benchmarks": ["TSPLIB-like_holdout", "synthetic_transfer_sets"]
            }
        },
        "interpretability": {
            "log_trace": True,
            "component_blocks": [
                "initialization",
                "construction",
                "insertions",
                "repair_and_optimize",
                "constraints"
            ],
            "explainability": {
                "feature_importance": "manual",
                "decision_trace": True
            }
        },
        "determinism": {
            "random_seed": 42,
            "seed_reproducibility": True
        }
    }
    return heuristic
