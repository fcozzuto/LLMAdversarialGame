def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "goal": "robust_transfer_for_tsp",
        "interpretability": "medium",
        "complexity": "low",
        "replay_archive": [],
        "assumptions": {
            "problem": "symmetric_euclidean_tsp",
            "held_out_focus": ["tsplib", "synthetic"],
        },
        "heuristic": {
            "construction": "nearest_neighbor_with_seed_diversification",
            "local_search": ["2-opt", "limited_3-opt"],
            "tie_breaking": "lexicographic_deterministic",
            "restart_policy": "fixed_multistart",
            "candidate_filter": "distance_plus_angle",
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": ["crossing_penalty", "local_stagnation_penalty"],
            "replay_weight": 1.0,
        },
        "failure_replay": {
            "enabled": True,
            "source": "none",
            "update_rule": "append_failed_structures_for_next_run",
            "selection": "most_recent_and_diverse",
            "budget": 0,
        },
        "parameters": {
            "num_restarts": 8,
            "seed_order": "sorted_node_index",
            "angle_threshold": 0.35,
            "stagnation_limit": 20,
            "max_2opt_passes": 5,
            "max_3opt_moves": 12,
        },
        "fallbacks": [
            "centroid_start",
            "farthest_insertion",
            "greedy_edge_repair",
        ],
    }
