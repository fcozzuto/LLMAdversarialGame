def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "no_replay": True,
        "memory": {
            "prior_candidates": False,
            "replay": False,
            "failure_memory": False,
            "compression": False,
        },
        "goal": "robust_transfer_on_held_out_TSPLIB_and_synthetic_instances",
        "interpretability": "high",
        "complexity": "moderate",
        "scaffold": {
            "construction": {
                "method": "nearest_neighbor",
                "start_policy": "multi_start_deterministic",
                "candidate_starts": ["min_x", "min_y", "max_x", "max_y", "centroid_nearest"],
                "tie_break": "lexicographic",
            },
            "improvement": {
                "method": "bounded_2opt",
                "budget_matching": True,
                "edge_filter": "distance_gain_positive",
                "termination": "no_improving_move_or_budget_exhausted",
                "move_order": "best_first",
            },
            "postprocess": {
                "method": "small_segment_reinsertion",
                "enabled": True,
                "segment_lengths": [1, 2],
                "accept_rule": "strict_improvement_only",
            },
        },
        "robustness": {
            "scale_invariant": True,
            "uses_coordinates_only": True,
            "instance_size_adaptive_budget": True,
            "fallback": "nearest_neighbor_only",
        },
        "budget_policy": {
            "type": "matched_to_instance_scale",
            "base_fraction": 0.02,
            "min_moves": 20,
            "max_moves": 2000,
        },
    }
