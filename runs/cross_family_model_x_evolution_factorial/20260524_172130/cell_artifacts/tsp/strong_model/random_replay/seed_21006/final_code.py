def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate": 1,
        "objective": "constrained_tsp",
        "priority": "robust_generalization",
        "interpretability": "high",
        "complexity": "moderate",
        "replay_archive": [],
        "strategy": {
            "construction": "nearest_neighbor_with_feasibility_bias",
            "improvement": ["2_opt", "relocate", "swap"],
            "repair": "constraint_aware_local_fix",
            "restart_policy": "deterministic_multistart",
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": ["constraint_violations", "stability"],
            "tie_break": "lexicographic",
        },
        "transfer_bias": {
            "favor_metric": "balanced",
            "avoid_overfitting": True,
            "synthetic_robustness": True,
            "held_out_tsplib_robustness": True,
        },
        "parameters": {
            "candidate_list_size": 12,
            "max_iterations": 200,
            "max_restarts": 4,
            "local_search_budget": 80,
            "accept_worsening": False,
        },
    }
