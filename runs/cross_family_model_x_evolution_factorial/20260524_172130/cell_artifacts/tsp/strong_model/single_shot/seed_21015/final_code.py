def build_heuristic():
    return {
        "name": "robust_interpretable_tsp_scaffold",
        "version": 1,
        "strategy": "construct_and_improve",
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "best_of_fixed_starts",
            "starts": ["min_x", "max_x", "min_y", "max_y"],
            "tie_break": "lexicographic",
        },
        "candidate_selection": {
            "primary": "distance",
            "secondary": "visibility",
            "visibility_weight": 0.25,
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "relocate"],
            "order": ["2-opt", "relocate"],
            "first_improvement": True,
            "max_passes": 20,
            "stop_when_no_improvement": True,
        },
        "constraint_handling": {
            "enabled": True,
            "mode": "penalty_then_repair",
            "repair_moves": ["swap", "relocate"],
            "infeasibility_penalty": 1000000,
        },
        "robustness": {
            "heldout_bias": "low",
            "smoothing": "edge_length_rank",
            "smoothing_alpha": 0.1,
            "avoid_overfitting": True,
        },
        "transfer": {
            "tsplib": "strong",
            "synthetic": "strong",
            "scale_invariant": True,
            "coordinate_normalization": "none",
        },
        "interpretability": {
            "priority": ["distance", "feasibility", "simple_improvement"],
            "allow_randomness": False,
        },
        "limits": {
            "time_complexity_target": "O(n^2)",
            "memory_complexity_target": "O(n^2)",
        },
    }
