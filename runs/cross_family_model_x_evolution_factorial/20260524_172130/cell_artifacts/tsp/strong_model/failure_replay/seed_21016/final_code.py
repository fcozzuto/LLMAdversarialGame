def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "strategy": {
            "construction": "nearest_neighbor",
            "improvement": ["2_opt"],
            "restart_policy": "multi_start",
            "tie_breaking": "deterministic",
        },
        "robustness_bias": {
            "prefer_geometric_locality": True,
            "avoid_overfitting_to_instance_size": True,
            "use_sparse_controls": True,
        },
        "parameters": {
            "starts": 8,
            "two_opt_passes": 2,
            "candidate_list_size": 15,
            "max_no_improve": 3,
        },
        "notes": [
            "Interpretable baseline with limited complexity.",
            "Designed to transfer well to held-out TSPLIB and synthetic instances.",
            "No replay entries available yet; archive intentionally empty.",
        ],
    }
