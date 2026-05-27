def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "candidate": 1,
        "constraints": {
            "no_imports": True,
            "deterministic": True,
            "no_replay_memory": True,
            "no_failure_memory": True,
            "no_compression": True,
        },
        "objective": {
            "primary": "minimize_tour_length",
            "secondary": "robust_transfer_performance",
            "focus": ["held_out_TSPLIB", "synthetic_generalization"],
        },
        "scaffold": {
            "init": ["nearest_neighbor", "farthest_insertion"],
            "construction": [
                "candidate_budget_matched_selection",
                "deterministic_tie_breaking",
            ],
            "improvement": [
                "2-opt",
                "limited_or_opt_1",
                "cross_exchange_local",
            ],
            "finalize": ["best_of_all_routes"],
        },
        "budget_policy": {
            "match_effort_to_instance_size": True,
            "small_instance": {"construction_passes": 2, "improvement_passes": 2},
            "medium_instance": {"construction_passes": 3, "improvement_passes": 3},
            "large_instance": {"construction_passes": 4, "improvement_passes": 2},
        },
        "selection": {
            "route_pool_size": 4,
            "use_diverse_seed_routes": True,
            "accept_only_improving_moves": True,
            "deterministic_seed_order": ["nearest_neighbor", "farthest_insertion"],
        },
        "tie_breaking": {
            "rule": "lexicographic",
            "keys": ["tour_length", "edge_gain", "seed_index", "move_index"],
        },
        "transfer_bias": {
            "prefer_geometry_agnostic_moves": True,
            "avoid_instance_specific_tuning": True,
            "preserve_sparse_neighbors": True,
        },
        "interpretability": {
            "simple_move_set": True,
            "explicit_budgeting": True,
            "explicit_seed_diversity": True,
        },
    }
