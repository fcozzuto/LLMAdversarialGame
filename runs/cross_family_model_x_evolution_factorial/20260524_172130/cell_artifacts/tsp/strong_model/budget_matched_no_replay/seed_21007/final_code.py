def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "objective": "minimize_tour_length",
        "scope": "constrained_tsp",
        "design_principles": [
            "deterministic",
            "interpretable",
            "budget_matched",
            "no_replay",
            "robust_transfer",
        ],
        "construction": {
            "initial_tour": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lexicographic",
            "candidate_filter": "feasible_only",
        },
        "improvement": {
            "local_search": ["2-opt", "or-opt"],
            "move_acceptance": "strict_improvement",
            "first_improvement": True,
            "restart_count": 0,
        },
        "constraint_handling": {
            "method": "penalty_aware_feasibility_first",
            "infeasible_moves": "reject",
            "repair": "none",
        },
        "budgeting": {
            "use_fixed_iteration_budget": True,
            "budget_match_to_instance_size": True,
            "iteration_schedule": "linear_with_n",
            "max_edge_checks_per_iteration": "O(n)",
        },
        "robustness": {
            "heldout_tsplib_focus": True,
            "synthetic_transfer_focus": True,
            "avoid_overfitting_to_training_instances": True,
            "randomization": "none",
        },
        "memory": {
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": ["feasibility", "stability"],
        },
    }
