def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "strategy": "constructive_plus_local_search",
        "objective": "minimize_tour_length",
        "transfer_priority": ["TSPLIB", "synthetic"],
        "interpretability": "high",
        "complexity": "low",
        "deterministic": True,
        "failure_replay": {
            "enabled": True,
            "archive_entries": [],
            "selection_policy": "none_available",
            "fallback": "nearest_neighbor_with_2opt",
        },
        "construction": {
            "seed_rule": "farthest_pair",
            "insertion_rule": "cheapest_insertion",
            "tie_breaker": "lexicographic",
        },
        "local_search": {
            "primary": "2opt",
            "secondary": "none",
            "max_passes": 8,
            "first_improvement": True,
        },
        "robustness": {
            "scale_invariant": True,
            "distance_only": True,
            "avoid_overfitting": True,
        },
        "stopping": {
            "no_improvement_passes": 2,
            "max_total_rounds": 1,
        },
    }
