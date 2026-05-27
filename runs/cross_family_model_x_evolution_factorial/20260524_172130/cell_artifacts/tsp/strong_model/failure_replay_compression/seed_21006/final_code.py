def build_heuristic():
    return {
        "name": "failure_replay_compression_candidate_1",
        "family": "tsp_heuristic_scaffold",
        "goal": "robust_transfer",
        "interpretability": "high",
        "complexity": "moderate",
        "core": {
            "construction": "nearest_insertion",
            "local_search": ["2-opt", "relocate"],
            "candidate_rule": "nearest_neighbors_and_geometric_closeness",
            "restart_policy": "small_deterministic_multi_start",
        },
        "failure_replay_compression": {
            "enabled": True,
            "archive_entries": 0,
            "compression_mode": "none_available",
            "fallback": "generic_robust_defaults",
        },
        "robustness": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "scale_invariance": True,
            "noise_tolerance": "medium",
        },
        "parameters": {
            "neighbor_list_size": 20,
            "multi_start_count": 4,
            "two_opt_passes": 2,
            "relocate_passes": 1,
            "improvement_threshold": 0.0,
        },
        "determinism": {
            "seed_policy": "fixed",
            "tie_breaking": "lexicographic",
            "randomness": False,
        },
        "fallback_order": [
            "nearest_insertion",
            "2-opt",
            "relocate",
            "deterministic_restart",
        ],
    }
