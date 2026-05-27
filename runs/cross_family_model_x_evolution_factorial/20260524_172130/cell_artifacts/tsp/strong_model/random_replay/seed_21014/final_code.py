def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "deterministic": True,
        "interpretable": True,
        "complexity": "low",
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "robustness_bias": "high",
        "components": {
            "construction": {
                "method": "nearest_neighbor",
                "tie_break": "stable_index",
                "start_policy": "multi_start_deterministic",
                "start_count": 8
            },
            "improvement": {
                "method": "2-opt",
                "acceptance": "strict_improvement",
                "first_improvement": True,
                "max_passes": 20
            },
            "replay": {
                "enabled": True,
                "archive_initialized": False,
                "selection_policy": "none_available",
                "fallback": "deterministic_multistart"
            }
        },
        "parameters": {
            "candidate_starts": 8,
            "seed_mode": "fixed",
            "seed_value": 0,
            "edge_filtering": "none",
            "restart_strategy": "spread_by_index"
        }
    }
