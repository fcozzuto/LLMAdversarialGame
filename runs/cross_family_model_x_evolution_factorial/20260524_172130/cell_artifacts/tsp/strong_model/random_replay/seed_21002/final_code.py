def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": "minimize_total_tour_length",
        "interpretability": "high",
        "robustness_priority": "held_out_tsplib_and_synthetic_transfer",
        "construction": {
            "method": "nearest_neighbor",
            "seed_policy": "deterministic_multi_start",
            "start_rule": "farthest_from_centroid_then_tie_break_by_index",
        },
        "local_search": {
            "enabled": True,
            "method": "2-opt",
            "move_filter": "first_improvement",
            "candidate_restriction": "symmetric_nearest_candidates",
            "max_passes": 3,
        },
        "constraint_handling": {
            "enabled": True,
            "method": "repair_then_penalize",
            "priority": "feasibility_first",
        },
        "selection": {
            "policy": "best_of_replayed_candidates",
            "tie_break": "lexicographic",
        },
        "termination": {
            "max_replays": 0,
            "max_time_ratio": 1.0,
        },
    }
