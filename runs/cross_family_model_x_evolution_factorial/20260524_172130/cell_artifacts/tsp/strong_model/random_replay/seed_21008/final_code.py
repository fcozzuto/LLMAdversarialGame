def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "deterministic": True,
        "goal": "robust_transfer",
        "problem": "tsp",
        "style": "interpretable",
        "complexity": "low",
        "replay_archive": [],
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "smallest_index",
        },
        "improvement": {
            "primary": ["2-opt", "swap"],
            "local_search_depth": 1,
            "acceptance": "strict_improvement",
        },
        "random_replay": {
            "enabled": True,
            "samples": 0,
            "archive_strategy": "none_available",
            "fallback": "deterministic_construction",
        },
        "robustness": {
            "prefer_short_edges": True,
            "diversify_starts": True,
            "heldout_bias": "low",
        },
        "stopping": {
            "max_passes": 2,
            "no_improve_limit": 1,
        },
    }
