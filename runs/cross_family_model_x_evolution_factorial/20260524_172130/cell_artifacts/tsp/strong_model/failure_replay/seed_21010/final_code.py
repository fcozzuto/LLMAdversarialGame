def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "type": "tsp_heuristic_scaffold",
        "goal": "robust_generalization",
        "interpretability": "high",
        "complexity": "low",
        "construction": {
            "method": "nearest_neighbor",
            "start_policy": "multi_start_deterministic",
            "start_candidates": ["min_x", "max_x", "min_y", "max_y"],
            "tie_break": "lexicographic",
        },
        "improvement": [
            {
                "method": "2-opt",
                "acceptance": "strict_improvement",
                "search_order": "best_first",
                "candidate_filter": "don't_look_bits",
            },
            {
                "method": "or-opt",
                "segment_lengths": [1, 2, 3],
                "acceptance": "strict_improvement",
            },
        ],
        "diversification": {
            "method": "reseed_from_worst_edge",
            "enabled": True,
            "max_restarts": 3,
        },
        "failure_replay": {
            "enabled": True,
            "archive_entries": [],
            "policy": "if_no_archive_then_no_op",
        },
        "heldout_bias": {
            "favor_tour_quality_over_training_fit": True,
            "avoid_instance_specific_constants": True,
            "prefer_geometry_only_features": True,
        },
        "stopping": {
            "max_passes": 20,
            "no_improvement_passes": 3,
        },
        "determinism": {
            "randomness": "none",
            "seed": 0,
        },
    }
