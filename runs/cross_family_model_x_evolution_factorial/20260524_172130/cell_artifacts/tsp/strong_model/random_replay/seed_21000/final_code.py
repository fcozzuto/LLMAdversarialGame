def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": "minimize_tsp_tour_length",
        "interpretability": "high",
        "complexity": "low",
        "transfer_priority": [
            "held_out_TSPLIB",
            "synthetic_instances"
        ],
        "heuristic": {
            "construction": "nearest_neighbor",
            "seeded_starts": "deterministic_multi_start",
            "multi_start_count": 8,
            "start_selection": "farthest_point_then_distance_ties",
            "replay_policy": "none",
            "local_search": [
                "2-opt",
                "limited_3-opt"
            ],
            "improvement_budget": {
                "2-opt_passes": 5,
                "3-opt_moves": 20
            },
            "candidate_lists": {
                "enabled": True,
                "size": 20,
                "metric": "euclidean"
            },
            "tie_breaking": "lexicographic",
            "pruning": {
                "crossing_elimination": True,
                "angle_filter": True
            }
        },
        "robustness": {
            "normalize_coordinates": True,
            "handle_duplicate_points": "stable_deduplicate",
            "fallback": "nearest_insertion"
        }
    }
