def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "type": "tsp_heuristic_scaffold",
        "deterministic": True,
        "no_imports": True,
        "memory": {
            "prior_candidates": False,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "goal": {
            "primary": "robust_transfer_performance",
            "secondary": "interpretability",
            "avoid": ["overfitting_to_training_instances", "excess_complexity"],
        },
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lowest_index",
        },
        "improvement": {
            "method": "2-opt",
            "budget_matching": True,
            "accept_rule": "strict_improvement",
            "scan_order": "deterministic_first_improvement",
            "restart": False,
        },
        "budget_policy": {
            "matched_to_instance_scale": True,
            "scale_signal": ["n", "distance_spread"],
            "budget_unit": "edge_evaluations",
            "allocation": "construction_plus_local_search",
        },
        "robustness": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "safeguards": ["centroid_based_seed", "bounded_local_search"],
        },
        "fallbacks": {
            "on_no_improvement": "return_current_tour",
            "on_tie": "prefer_lexicographically_smaller_tour",
        },
    }
