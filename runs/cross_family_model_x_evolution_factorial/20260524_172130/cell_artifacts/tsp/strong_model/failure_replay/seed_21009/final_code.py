def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": {
            "primary": "minimize_tour_length",
            "generalization_priority": [
                "held_out_TSPLIB",
                "synthetic_transfer",
                "robustness"
            ]
        },
        "heuristic": {
            "name": "interpretable_local_search_with_restarts",
            "components": [
                "nearest_neighbor_seed",
                "2_opt_local_search",
                "limited_candidate_reinsertion",
                "deterministic_multi_start"
            ],
            "design_principles": [
                "favor_simple_geometry_based_moves",
                "avoid_instance_specific_tuning",
                "use_small_candidate_sets_for_transfer",
                "keep_improvement_rules_monotone"
            ]
        },
        "move_policy": {
            "primary_moves": [
                {"type": "2_opt", "accept": "strict_improvement"},
                {"type": "reinsert", "accept": "strict_improvement"}
            ],
            "tie_breaking": "lexicographic",
            "restart_policy": {
                "seeds": ["nearest_neighbor", "farthest_insertion", "greedy_cheapest_insertion"],
                "deterministic_order": True
            }
        },
        "constraints": {
            "deterministic": True,
            "no_randomness": True,
            "bounded_complexity": True,
            "interpretability": True
        },
        "fallbacks": {
            "if_no_improvement": "return_best_seen",
            "if_archive_empty": "use_generic_improvement_rules"
        }
    }
