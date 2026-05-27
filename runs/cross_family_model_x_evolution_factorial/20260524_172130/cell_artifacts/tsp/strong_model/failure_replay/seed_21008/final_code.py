def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": "minimize_tour_length",
        "design_priorities": [
            "robustness_on_held_out_TSPLIB",
            "transfer_to_synthetic_instances",
            "interpretability",
            "moderate_complexity",
        ],
        "scaffold": {
            "representation": "tour_permutation",
            "construction": "nearest_insertion_seed",
            "improvement": [
                "2-opt",
                "or-opt",
                "limited_reinsertion",
            ],
            "acceptance": "strict_improvement",
            "restart_policy": "multi_start_with_diverse_seeds",
            "failure_replay": {
                "enabled": True,
                "archive": [],
                "trigger": "repeat_local_minima_or_stagnation",
                "use_case": "prioritize operators that resolved previous failures",
            },
        },
        "parameters": {
            "max_restarts": 8,
            "max_local_passes": 4,
            "stagnation_limit": 50,
            "candidate_list_size": 20,
            "replay_weight": 1.0,
        },
        "notes": [
            "Keep operator ordering simple and deterministic.",
            "Prefer general-purpose local search moves over instance-specific tuning.",
        ],
    }
