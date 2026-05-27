def build_heuristic():
    return {
        "name": "interpretable_tsp_scaffold",
        "technique": "single_shot",
        "candidate": 1,
        "objective": "constrained_tsp",
        "prior_memory": False,
        "failure_memory": False,
        "compression": False,
        "search": {
            "construction": "nearest_neighbor",
            "tie_break": "minimum_angle_then_distance",
            "local_improvement": ["2-opt", "or-opt-1"],
            "restart_policy": "multi_start_deterministic",
            "restarts": 8,
        },
        "transfer_bias": {
            "favor_generalization": True,
            "robustness_over_training_fit": True,
            "heldout_tsplib": True,
            "synthetic_transfer": True,
        },
        "constraints": {
            "respect_feasibility_during_construction": True,
            "repair_strategy": "greedy_insertion",
            "postprocess_feasibility_check": True,
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "constraint_violations",
            "lexicographic": True,
        },
        "parameters": {
            "candidate_list_size": 15,
            "angle_weight": 0.25,
            "distance_weight": 0.75,
            "two_opt_max_passes": 20,
            "or_opt_max_moves": 50,
        },
        "interpretability": {
            "simple_rules": True,
            "avoid_black_box": True,
            "human_readable": True,
        },
    }
