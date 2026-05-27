def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "type": "tsp_heuristic_scaffold",
        "strategy": "nearest_neighbor_with_2opt_cleanup",
        "selection": {
            "start_rule": "farthest_from_centroid",
            "tie_break": "lexicographic",
            "candidate_rule": "nearest_unvisited",
        },
        "cleanup": {
            "enabled": True,
            "local_search": "2opt",
            "max_passes": 5,
            "first_improvement": True,
        },
        "robustness": {
            "scale_invariant": True,
            "coordinate_normalization": "center_and_scale",
            "heldout_transfer_bias": "moderate",
            "synthetic_generalization_bias": "high",
        },
        "interpretability": {
            "complexity": "low",
            "components": ["start_rule", "greedy_construction", "2opt"],
        },
        "determinism": {
            "randomness": False,
            "seed": 0,
        },
    }
