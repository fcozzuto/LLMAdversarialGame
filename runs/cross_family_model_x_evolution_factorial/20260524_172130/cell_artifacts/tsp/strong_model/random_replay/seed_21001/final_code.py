def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "archive_available": False,
        "deterministic": True,
        "objective": "minimize_tour_length",
        "interpretability": "high",
        "complexity": "low",
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "components": {
            "construction": {
                "method": "nearest_neighbor",
                "start_rule": "best_of_fixed_starts",
                "fixed_starts": [0, 1, 2, 3, 4],
            },
            "improvement": {
                "method": "2_opt",
                "pass_limit": 3,
                "first_improvement": True,
            },
            "replay": {
                "mode": "random_replay",
                "archive_entries": [],
                "fallback": "construction_plus_local_search",
            },
        },
        "selection": {
            "candidate_pool": 1,
            "tie_break": "lexicographic",
        },
        "robustness": {
            "scale_invariant": True,
            "distance_metric_assumption": "metric",
            "avoid_overfitting_to_training_instances": True,
        },
    }
