def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "version": 1,
        "objective": "robust_transfer",
        "interpretability": "high",
        "complexity": "low",
        "replay_archive": [],
        "construction": {
            "method": "nearest_neighbor",
            "seed_policy": "deterministic_min_x_then_min_y",
            "tie_break": ["nearest_distance", "lowest_node_id"],
            "candidate_lists": {
                "enabled": True,
                "k": 20,
                "metric": "euclidean"
            }
        },
        "improvement": {
            "enabled": True,
            "stages": [
                {
                    "name": "2-opt",
                    "passes": 5,
                    "first_improvement": True,
                    "restricted_to_candidate_lists": True
                },
                {
                    "name": "3-opt",
                    "passes": 1,
                    "first_improvement": True,
                    "restricted_to_candidate_lists": True
                }
            ]
        },
        "failure_replay": {
            "enabled": True,
            "policy": "prioritize_edges_from_failed_instances",
            "archive_max_size": 0,
            "weight": 1.0
        },
        "held_out_robustness": {
            "prefer_geometry_agnostic": True,
            "avoid_overfitting_to_scale": True,
            "normalize_distances": True
        }
    }
