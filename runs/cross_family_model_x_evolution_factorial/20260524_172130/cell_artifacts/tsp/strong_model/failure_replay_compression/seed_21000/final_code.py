def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "deterministic": True,
        "interpretable": True,
        "complexity": "moderate",
        "target": "constrained_tsp",
        "selection_policy": {
            "primary": "nearest_feasible_gain",
            "tie_breakers": [
                "lower_incremental_cost",
                "higher_slack_remaining",
                "lower_node_id",
            ],
        },
        "repair_policy": {
            "enabled": True,
            "method": "single_swap_then_2opt",
            "accept_if": "feasibility_preserved_and_cost_improves",
        },
        "failure_replay_compression": {
            "enabled": True,
            "archive_capacity": 0,
            "compression": "none",
            "use_replay": False,
        },
        "constraint_handling": {
            "prefer_feasible": True,
            "hard_reject_infeasible": True,
            "soft_penalty_scale": 1000000,
        },
        "construction": {
            "start_rule": "lowest_index_feasible_start",
            "candidate_filter": "feasible_only",
            "lookahead": 1,
        },
        "local_search": {
            "enabled": True,
            "moves": ["2opt", "swap"],
            "max_rounds": 2,
            "first_improvement": True,
        },
        "robustness": {
            "tsplib_transfer": True,
            "synthetic_transfer": True,
            "avoid_instance_specific_constants": True,
        },
    }
