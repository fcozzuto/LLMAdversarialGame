def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "strategy": {
            "family": "constructive_local_search",
            "construction": {
                "method": "nearest_neighbor",
                "seed_policy": "multi_start_deterministic",
                "start_nodes": "extremes_and_centroid",
            },
            "improvement": {
                "method": "2-opt",
                "acceptance": "strict_improvement",
                "stopping": "no_improvement_pass",
                "pass_limit": 3,
            },
            "repair": {
                "enabled": True,
                "method": "segment_relink",
                "priority": "reconnect_long_edges_first",
            },
        },
        "robustness": {
            "transfer_focus": ["tsplib", "synthetic_euclidean", "clustered", "grid"],
            "tie_breaking": "lexicographic",
            "distance_normalization": "none",
            "stability_bias": "moderate",
        },
        "interpretability": {
            "complexity": "low",
            "notes": "Use simple nearest-neighbor construction followed by bounded 2-opt refinement.",
        },
    }
