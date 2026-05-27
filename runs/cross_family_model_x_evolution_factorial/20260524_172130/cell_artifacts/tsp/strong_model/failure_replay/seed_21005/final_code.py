def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 7,
        "replay_archive": [
            {
                "family": "a",
                "instance_name": "a280",
                "failure_priority": 1.0,
                "signal": "large-scale euclidean, needs stronger diversification",
            },
            {
                "family": "eil",
                "instance_name": "eil101",
                "failure_priority": 0.95,
                "signal": "medium-scale, nearest-neighbor baseline underperforms",
            },
            {
                "family": "kroA",
                "instance_name": "kroA100",
                "failure_priority": 0.93,
                "signal": "robustness gap on classic TSPLIB geometry",
            },
        ],
        "objective": "minimize_tour_length",
        "representation": "permutation",
        "construction": {
            "method": "multi_start_geometric",
            "start_rule": "farthest_from_centroid",
            "start_pool": [
                "farthest_from_centroid",
                "extreme_x",
                "extreme_y",
                "max_pair_distance_endpoint",
            ],
            "builder_pool": [
                "nearest_neighbor",
                "farthest_insertion",
                "cheapest_insertion",
            ],
            "tie_break": "lowest_index",
            "candidate_limit": 24,
        },
        "improvement": {
            "method": "iterated_local_search",
            "local_search": [
                {"move": "2-opt", "selection": "best_improvement"},
                {"move": "or-opt-2", "selection": "best_improvement"},
                {"move": "swap", "selection": "first_improvement"},
            ],
            "perturbation": {
                "method": "double_bridge",
                "strength": 2,
            },
            "acceptance": {
                "rule": "accept_if_improves_or_equal",
            },
            "restart": {
                "enabled": True,
                "max_restarts": 5,
                "diversify_with": "farthest_insertion",
                "restart_policy": "best_of_starts",
            },
        },
        "robustness_bias": {
            "favor_generalization": True,
            "instance_features": ["coordinates_only", "scale_agnostic"],
            "avoid_overfitting": True,
            "parameter_policy": "small_fixed_set",
            "transfer_priority": "held_out_tsplib_and_synthetic",
        },
        "constraints": {
            "deterministic": True,
            "no_randomness": True,
        },
    }
