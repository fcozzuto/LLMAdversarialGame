def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "description": "A robust, interpretable scaffold for constrained TSP with deterministic behavior and failure_replay_compression-style structure.",
        "parameters": {
            "seed": 0,
            "start_node_strategy": "lowest_index",
            "constrained_edge_selection": "feasible_min_cost",
            "neighborhood_search": {
                "enabled": True,
                "method": "2opt",
                "max_iterations": 50,
                "acceptance_criterion": "progress_only"
            },
            "repair_mechanism": {
                "enabled": True,
                "strategy": "nearest_feasible_insert",
                "max_steps": 100
            },
            "termination": {
                "type": "improvement_stop",
                "improvement_window": 10,
                "no_improvement_bound": 50
            },
            "restriction_handling": {
                "type": "budget_and_constraints",
                "budget_permutations": 1000,
                "active_constraints": ["maximum_tour_length", "required_edges"]
            },
            "transfer_performance_considerations": {
                "train_focus": "robustness_across_synthetic_and_realworld_tsplib_like_instances",
                "held_out_evaluation": True,
                "transfer_schema": "cross_instance_consistency"
            }
        },
        "data_space": {
            "instances": {
                "tsplib_like": True,
                "synthetic": True,
                "constraints": ["time_window", "capacity", "precedence"],
                "scaling": "unit_cost"
            },
            "instance_sampling": {
                "method": "deterministic_representation",
                "count": 1,
                "seed": 0
            }
        },
        "objective": {
            "type": "minimize_cost",
            "penalties": {
                "soft_constraints": 0.0,
                "hard_constraints": 1.0
            }
        },
        "algorithmic_components": [
            {
                "type": "construction",
                "strategy": "greedy_feasible_seed",
                "details": {
                    "seed_node": "lowest_index",
                    "edge_cost_eval": "aggregated"
                }
                },
            {
                "type": "local_search",
                "name": "2-opt_swap",
                "parameters": {
                    "max_steps": 50,
                    "acceptance": "improvement_only"
                }
            },
            {
                "type": "repair",
                "name": "nearest_feasible_insert",
                "parameters": {
                    "attempts": 100
                }
            }
        ],
        "robustness_and_failure_handling": {
            "failure_replay_compression": {
                "enabled": True,
                "archive": None,
                "policy": "none_available_yet",
                "planned_replay": "deterministic_placeholder"
            },
            "fallbacks": [
                "deterministic_rebuild_from_seed",
                "safe_pruning_of_infeasible_segments"
            ]
        },
        "interpretability": {
            "summary": True,
            "logging_horizon": 1,
            "traceability": ["seed_node_choice", "edge_selection", "local_search_moves"]
        },
        "constraints": {
            "hard": ["no_subtour_elimination_violation"],
            "soft": ["minimize_tour_length_change", "limit_repair_insertion_cost"]
        },
        "determinism": {
            "ensured_by": ["fixed_seed", "fixed_ordering", "no_random_sampling"],
            "reproducibility_notes": "scaffold intentionally deterministic for evaluation"
        }
    }
