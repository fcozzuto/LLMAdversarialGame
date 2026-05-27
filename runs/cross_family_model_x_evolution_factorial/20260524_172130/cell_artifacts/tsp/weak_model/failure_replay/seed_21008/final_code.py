def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "description": "Deterministic TSP heuristic scaffold focusing on information gain and local search, using failure replay technique.",
        "techniques": [
            "nearest_neighbor_construction",
            "2_opt_local_search",
            "attempt_failure_replay"
        ],
        "parameters": {
            "construction_method": "nearest_neighbor",
            "neighbor_count": 5,
            "local_search": "2_opt",
            "max_iterations": 1000,
            "failure_replay": {
                "enabled": True,
                "max_replay_attempts": 50,
                "replay_threshold": 0.9,
                "replay_strategy": "candidate_list_reserve"
            }
        },
        "heuristic_strategy": "information_gain",
        "validation_folders": [
            "TSPLIB_instances",
            "synthetic_transfer_instances"
        ],
        "robustness_focus": "generalization across instances",
        "interpretable": True,
        "complexity": "moderate"
    }

