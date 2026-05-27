def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "robust_transfer_tsp_heuristic",
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "complexity": "moderate",
            "no_replay_archive": True,
        },
        "pipeline": [
            "normalize_instance",
            "construct_initial_tour",
            "compress_failure_signals",
            "apply_local_search",
            "final_repair",
        ],
        "initial_tour": {
            "method": "nearest_neighbor_multi_start",
            "starts": ["min_x", "max_x", "min_y", "max_y"],
            "tie_break": "lexicographic",
            "seedless": True,
        },
        "failure_replay_compression": {
            "enabled": True,
            "archive_policy": "compact_recent_failures",
            "compression": {
                "representation": "edge_penalty_table",
                "update_rule": "increment_on_improvement_failure",
                "decay": "none",
            },
            "uses": [
                "crossing_edges",
                "long_edges_in_small_instances",
                "repeat_bad_2opt_moves",
            ],
        },
        "local_search": {
            "passes": ["2-opt", "or-opt-1", "or-opt-2"],
            "acceptance": "strict_improvement",
            "candidate_restriction": "k_nearest",
            "k_nearest": 16,
            "stop_when_no_change": True,
        },
        "repair": {
            "enable_3opt_like_cleanup": True,
            "prefer_short_edges": True,
            "avoid_edge_reuse_from_failures": True,
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": ["edge_crossings", "maximum_edge_length"],
            "penalty_weights": {
                "crossing": 4.0,
                "failure_edge": 2.0,
                "max_edge": 0.5,
            },
        },
        "transfer_bias": {
            "favor": ["planar_geometry", "low_parameter_count", "scale_invariance"],
            "avoid": ["instance_specific_tuning", "deep_search_overfitting"],
        },
    }
