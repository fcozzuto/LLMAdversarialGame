def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lowest_index",
            "seed_candidates": ["farthest_from_centroid", "highest_degree", "median_distance"],
        },
        "local_search": {
            "primary": "2-opt",
            "apply_until_no_improvement": True,
            "move_order": "best_improvement",
            "candidate_restriction": "k_nearest",
            "k_nearest": 20,
        },
        "perturbation": {
            "method": "double_bridge",
            "strength": "medium",
            "frequency": "on_stagnation",
            "stagnation_limit": 50,
        },
        "reconstruction": {
            "method": "greedy_reinsert",
            "preserve_subtours": True,
        },
        "scoring": {
            "objective": "tour_length",
            "normalize_by": "n",
        },
        "termination": {
            "max_no_improve_rounds": 200,
            "max_restarts": 5,
        },
        "notes": [
            "Interpretable scaffold with conservative diversification.",
            "Designed to transfer reasonably across TSPLIB and synthetic Euclidean instances.",
            "No replay entries yet; initialize archive after first failure cases."
        ],
    }
