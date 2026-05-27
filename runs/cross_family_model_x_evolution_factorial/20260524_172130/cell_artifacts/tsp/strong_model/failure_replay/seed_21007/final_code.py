def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "problem": "tsp",
        "deterministic": True,
        "interpretability": "high",
        "complexity": "low",
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "technique": "failure_replay",
        "replay_archive": [],
        "construction": {
            "start_rule": "nearest_to_centroid",
            "candidate_filter": "k_nearest",
            "k": 12,
            "tie_break": "lexicographic",
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "segment_reversal"],
            "first_improvement": True,
            "max_passes": 10,
        },
        "robustness": {
            "use_distance_normalization": True,
            "prefer_short_edges": True,
            "avoid_overfitting_to_instance_size": True,
        },
        "failure_replay": {
            "enabled": True,
            "strategy": "append_misleading_edges_and_bad_starts_to_reject_list",
            "update_rule": "on_failures_only",
            "memory_limit": 64,
        },
        "scoring": {
            "edge_cost": "euclidean_distance",
            "tour_cost": "sum_edges",
        },
    }
