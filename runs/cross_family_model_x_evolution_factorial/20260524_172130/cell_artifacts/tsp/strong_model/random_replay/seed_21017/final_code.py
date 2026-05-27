def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": "minimize_tour_length",
        "design_principles": [
            "deterministic",
            "interpretable",
            "robust_generalization",
            "simple_control_flow",
        ],
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "best_of_all_starts",
            "tie_break": "lexicographic",
        },
        "repair": {
            "enable": True,
            "method": "2-opt",
            "passes": 2,
            "accept_rule": "strict_improvement_only",
        },
        "local_search": {
            "methods": ["2-opt", "swap"],
            "candidate_filter": "bounded_neighborhood",
            "max_rounds": 3,
            "stop_when_no_improvement": True,
        },
        "constraint_handling": {
            "mode": "feasible_first",
            "penalty": 0,
            "infeasible_moves_allowed": False,
        },
        "transfer_bias": {
            "favor_short_edges": True,
            "avoid_instance_specific_tuning": True,
            "robustness_over_training_fit": True,
        },
    }
