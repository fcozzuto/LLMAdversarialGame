def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "family": "TSP_heuristic_scaffold",
        "goal": "robust_transfer",
        "interpretability": "high",
        "complexity": "moderate",
        "replay_archive_entries": 0,
        "construction": {
            "method": "nearest_insertion",
            "seeded_starts": ["farthest_pair", "nearest_to_centroid"],
            "start_count": 2,
            "tie_breaker": "lower_index",
        },
        "improvement": {
            "method": "2-opt",
            "apply_until_no_improvement": True,
            "candidate_policy": "restricted_neighborhood",
            "candidate_size": 20,
        },
        "compression": {
            "enabled": True,
            "use_failure_replay": False,
            "reuse_patterns": [
                "long_edge_removal",
                "crossing_elimination",
                "cluster_bridge_shortening",
            ],
        },
        "generalization_bias": {
            "favor_short_edges": True,
            "balance_global_and_local": True,
            "avoid_instance_specific_tuning": True,
        },
        "deterministic": True,
        "output": {
            "type": "scaffold_spec",
            "return_structure": "dict",
        },
    }
