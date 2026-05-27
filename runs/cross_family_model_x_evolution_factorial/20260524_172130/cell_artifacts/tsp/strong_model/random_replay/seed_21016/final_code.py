def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "deterministic": True,
        "objective": "tsp",
        "priorities": ["robustness", "interpretability", "generalization"],
        "technique": {
            "type": "random_replay",
            "replay_archive": [],
            "use_archive": False,
            "fallback": "nearest_neighbor",
        },
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lexicographic",
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "swap"],
            "move_order": ["2-opt", "swap"],
            "first_improvement": True,
            "max_passes": 3,
        },
        "perturbation": {
            "enabled": True,
            "method": "double_bridge",
            "strength": 0.15,
            "adaptive": False,
        },
        "restarts": {
            "enabled": True,
            "count": 4,
            "selection": "best_of_all",
        },
        "constraints": {
            "respect_tour_validity": True,
            "no_imports": True,
        },
        "parameters": {
            "seed": 0,
            "candidate_limit": 1,
            "archive_weight": 0.0,
        },
    }
