def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic
    # Designed to be interpretable and robust to held-out TSPLIB and synthetic instances.
    return {
        "name": "constrained_tsp_heuristic_single_shot",
        "description": "A simple, interpretable single-shot heuristic scaffold for constrained TSP with deterministic behavior.",
        "version": "1.0",
        "technique": "single_shot",
        "parameters": {
            # Core scoring weights (adjustable but deterministic)
            "edge_cost_weight": 1.0,
            "constraint_penalty_weight": 10.0,
            "soft_constraint_tolerance": 0.0,
            "step_limit": 0,  # 0 means no explicit step limit in this scaffold
            "seed": 0  # deterministic seed for any internal randomization (no randomness used)
        },
        "constraints": {
            "must_visit_all_nodes": True,
            "distance_metric": "euclidean",  # or "euclidean_squared" if needed, deterministic
            "time_window_constraints": False,
            "capacity_constraints": False
        },
        "heuristic_mechanism": {
            "type": "greedy_lexicographic",
            "start_node_policy": "lowest_index",
            "tie_breaker": "lowest_previous_distance",
            "neighborhood": {
                "range": "ordered_by_distance",
                "max_candidates": 5
            },
            "edge_selection_rule": "select_min_cost_path_that_meets_constraints",
            "rollback_on_failure": False
        },
        "objective": {
            "primary": "minimize_total_distance_with_constraints",
            "secondary": [
                "maximize_visited_nodes_consistency",
                "balance_load_across_path"
            ]
        },
        "data_handling": {
            "instance_format": "tsplib_like",
            "coordinate_type": "float",
            "distance_matrix_provision": "on_the_fly"  # deterministic calculation from coordinates
        },
        "robustness": {
            "held_out_strategy": "use_global_scaling_and_pruning",
            "fallback": "none",
            "determinism": True
        },
        "interpretability": {
            "log_details": True,
            "traceability": ["start_node", "chosen_next", "cost", "constraint_violation"],
            "explanation_interface": "human_readable"
        },
        "compatibility": {
            "tsplib_version_support": ["1.0","1.2"],
            "synthetic_support": True
        },
        "output": {
            "tour": None,  # to be filled by runner
            "cost": None   # to be filled by runner
        }
    }
