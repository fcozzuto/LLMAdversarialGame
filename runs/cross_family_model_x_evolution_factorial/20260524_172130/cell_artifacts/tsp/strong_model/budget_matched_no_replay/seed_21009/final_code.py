def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "interpretable": True,
        "complexity": "moderate",
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "no_replay": True,
        "no_memory": {
            "prior_candidates": False,
            "failure_memory": False,
            "compression": False,
        },
        "construction": {
            "method": "nearest_insertion",
            "seed_rule": "min_sum_dist_to_all",
            "tie_break": "lexicographic",
            "candidate_list_size": 12,
            "use_angle_filter": False,
        },
        "improvement": {
            "local_search": ["2-opt", "or-opt-1"],
            "move_order": "best_improvement",
            "acceptance": "strict_improvement",
            "max_passes": 5,
            "stagnation_limit": 2,
        },
        "budget_matching": {
            "strategy": "match_construction_and_improvement_cost",
            "construction_share": 0.35,
            "improvement_share": 0.65,
            "cap_restarts": 1,
        },
        "restart": {
            "enabled": False,
            "method": "none",
        },
        "robustness": {
            "scale_invariant": True,
            "distance_only": True,
            "symmetry_assumed": True,
            "prefer_short_edges": True,
        },
        "scoring": {
            "objective": "tour_length",
            "secondary": "edge_stability",
        },
    }
