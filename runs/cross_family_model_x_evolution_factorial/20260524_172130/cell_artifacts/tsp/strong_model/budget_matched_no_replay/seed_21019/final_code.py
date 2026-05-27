def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "no_replay": True,
        "memory": {
            "prior_candidates": False,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "goal": "constrained_tsp_heuristic",
        "design_priorities": [
            "held_out_tsplib_transfer",
            "synthetic_transfer",
            "interpretability",
            "robustness",
        ],
        "construction": {
            "initialization": "nearest_neighbor",
            "seed_rule": "min_index_then_min_distance",
            "tie_break": "lexicographic",
            "candidate_filter": "feasible_only",
        },
        "improvement": {
            "local_search": ["2-opt", "relocation"],
            "acceptance": "strict_improvement_only",
            "budget_matching": True,
            "replay": False,
            "restart_policy": "single_pass",
        },
        "constraint_handling": {
            "hard_constraints_first": True,
            "repair": "greedy_feasible_repair",
            "penalty": "none",
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "constraint_violation",
            "objective_order": ["feasibility", "length"],
        },
        "budget_matched_no_replay": {
            "enabled": True,
            "match_to_available_budget": True,
            "adaptive_step_cap": True,
            "use_history": False,
        },
        "simplicity": {
            "interpretable": True,
            "max_components": 4,
            "avoid_overfitting": True,
        },
    }
