def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "robust_transfer",
        "interpretability": "high",
        "complexity": "moderate",
        "no_replay_entries": True,
        "components": {
            "construction": {
                "method": "nearest_neighbor",
                "seed_policy": "deterministic_multi_start",
                "start_nodes": ["min_x", "max_x", "min_y", "max_y", "centroid_nearest", "farthest_pair"],
            },
            "repair": {
                "method": "2-opt",
                "apply_until_stable": True,
                "max_passes": 50,
            },
            "compression": {
                "method": "failure_pattern_clustering",
                "store_only_distinct_failures": True,
                "signature": ["edge_crossing", "long_edge", "late_regret"],
                "limit": 16,
            },
            "selection": {
                "metric": "tour_length",
                "tie_break": ["fewer_crossings", "lower_max_edge", "lexicographic"],
            },
        },
        "scoring": {
            "primary": "total_length",
            "secondary": ["crossing_count", "max_edge_length", "variance_of_edge_lengths"],
            "robustness_bias": 0.2,
        },
        "constraints": {
            "deterministic": True,
            "no_randomness": True,
            "bounded_memory": True,
        },
    }
