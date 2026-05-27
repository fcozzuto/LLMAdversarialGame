def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "robust_tsp_heuristic",
        "principles": [
            "deterministic",
            "interpretable",
            "transfer_robust",
            "low_complexity",
        ],
        "representation": {
            "tour_encoding": "permutation",
            "distance_usage": "full_matrix_or_callback",
        },
        "construction": {
            "method": "nearest_neighbor_seeded_by_extremes",
            "seeds": ["min_x", "max_x", "min_y", "max_y"],
            "tie_break": "lexicographic",
        },
        "improvement": {
            "primary": "2-opt",
            "secondary": "3-opt_limited",
            "candidate_filter": "delta_gain_only",
            "stop_rule": "no_improvement_pass",
        },
        "replay_compression": {
            "enabled": True,
            "archive_policy": "keep_only_distinct_failure_patterns",
            "pattern_keys": [
                "crossing_edges",
                "short_cycle_traps",
                "hub_and_spoke_misorder",
                "cluster_boundary_errors",
            ],
            "action": "prefer_moves_that_remove_multiple_replayed_failures",
        },
        "robustness_bias": {
            "metric": "multi_instance_generalization",
            "preferences": [
                "reduce edge crossings",
                "preserve cluster coherence",
                "avoid greedy dead-ends",
            ],
        },
        "fallbacks": {
            "if_construction_degenerates": "insert_remaining_by_minimum_increase",
            "if_improvement_stalls": "apply_limited_randomness_free_shuffle_by_geometry_rank",
        },
        "parameters": {
            "max_2opt_passes": 8,
            "max_3opt_trials_per_pass": 64,
            "max_replay_patterns": 16,
        },
    }
