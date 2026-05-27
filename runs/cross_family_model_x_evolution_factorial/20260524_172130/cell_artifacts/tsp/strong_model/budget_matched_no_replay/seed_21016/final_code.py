def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "variant": "candidate_1",
        "problem": "constrained_tsp",
        "goal": "robust_held_out_generalization",
        "interpretability": "high",
        "complexity": "moderate",
        "state": {
            "representation": "tour_plus_unvisited_set",
            "constraint_tracking": ["budget", "feasibility_slack", "edge_cost"],
        },
        "construction": {
            "seed_strategy": "nearest_feasible_to_start",
            "insertion_rule": "best_feasible_insertion",
            "tie_break": ["lower_added_cost", "lower_budget_use", "lexicographic_node_id"],
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "relocate"],
            "acceptance": "strict_improvement",
            "feasibility_first": True,
            "restart": "none",
        },
        "budget_control": {
            "target_usage_ratio": 0.95,
            "matched_sampling": True,
            "penalty_for_slack": 0.25,
            "penalty_for_infeasible": 1000000,
        },
        "transfer_bias": {
            "prefer_short_edges": True,
            "prefer_geometric_consistency": True,
            "avoid_instance_specific_tuning": True,
        },
        "no_replay": True,
        "memory": {
            "prior_candidates": 0,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "budget_feasibility",
            "tertiary": "edge_stability",
        },
    }
