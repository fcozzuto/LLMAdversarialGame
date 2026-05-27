def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "problem": "tsp",
        "deterministic": True,
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "interpretability": "high",
        "complexity": "moderate",
        "construction": {
            "method": "nearest_neighbor",
            "multi_start": 4,
            "start_nodes": ["min_x", "max_x", "min_y", "max_y"],
            "tie_break": "lexicographic",
        },
        "improvement": {
            "primary": ["2-opt", "swap"],
            "secondary": ["3-opt_like_segment_reversal"],
            "acceptance": "strict_improvement",
            "search_budget": {
                "edge_checks": 5000,
                "move_evaluations": 8000,
            },
            "restart_policy": "budget_matched",
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "scoring": {
            "objective": "tour_length",
            "candidate_ranking": "best_length_then_deterministic_tie_break",
        },
        "robustness": {
            "normalize_coordinates": True,
            "use_centroid_seed": True,
            "prefer_short_edges": True,
            "avoid_instance_specific_tuning": True,
        },
    }
