def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "interpretable": True,
        "complexity": "moderate",
        "target": "constrained_tsp",
        "goal": "robust_transfer_on_tsplib_and_synthetic_instances",
        "no_replay": True,
        "no_memory": True,
        "no_compression": True,
        "construction": {
            "start_rule": "best_regret_seed",
            "candidate_selection": "nearest_feasible_with_slack",
            "insertion_rule": "cheapest_feasible_insertion",
            "tie_break": ["lower_added_cost", "larger_remaining_budget", "smaller_index"]
        },
        "budget_handling": {
            "primary": "budget_matched",
            "match_target": "estimated_tour_length",
            "feasibility_margin": 0.02,
            "repair": "single_pass_prune_and_reinsert"
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "or-opt-1", "or-opt-2"],
            "acceptance": "first_improvement",
            "feasibility_check": "incremental"
        },
        "scoring": {
            "edge_cost_weight": 1.0,
            "budget_slack_weight": 0.4,
            "constraint_violation_penalty": 1000000,
            "diversification": 0.0
        },
        "stopping": {
            "construction_passes": 1,
            "local_search_passes": 2,
            "max_no_improve": 1
        }
    }
