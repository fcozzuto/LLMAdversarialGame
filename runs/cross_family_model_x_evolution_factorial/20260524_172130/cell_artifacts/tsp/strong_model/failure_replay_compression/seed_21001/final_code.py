def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "problem": "constrained_tsp",
        "objective": "minimize_tour_length",
        "style": "interpretable_heuristic",
        "deterministic": True,
        "no_replay_archive": True,
        "strategy": {
            "construction": {
                "method": "nearest_insertion",
                "seed_rule": "farthest_pair",
                "tie_break": "lexicographic",
                "candidate_set_size": 12,
                "use_regret": True,
                "regret_k": 2,
            },
            "local_search": {
                "enabled": True,
                "moves": ["2-opt", "relocate", "swap"],
                "move_order": ["2-opt", "relocate", "swap"],
                "first_improvement": True,
                "max_passes": 4,
            },
            "constraint_handling": {
                "feasibility_first": True,
                "repair": "greedy_reinsert",
                "penalty_mode": "adaptive_static",
                "infeasible_moves_allowed": False,
            },
            "failure_replay_compression": {
                "enabled": True,
                "compression": "pattern_summary",
                "max_patterns": 8,
                "store": ["repeated_bad_edges", "repeated_bad_insertions"],
                "apply_only_when_repeated": True,
            },
        },
        "robustness": {
            "heldout_tsplib_priority": True,
            "synthetic_transfer_priority": True,
            "avoid_instance_specific_tuning": True,
            "diversity_bias": "low",
        },
        "parameters": {
            "alpha": 0.35,
            "beta": 1.0,
            "gamma": 0.15,
        },
    }
