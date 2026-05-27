def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "interpretable": True,
        "complexity": "low",
        "transfer_bias": ["held_out_TSPLIB", "synthetic"],
        "objective": {
            "primary": "tour_length",
            "secondary": ["stability", "generalization"],
        },
        "construction": {
            "start_rule": "nearest_to_centroid",
            "candidate_set": "k_nearest",
            "k": 12,
            "tie_break": "lowest_index",
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "node_swap"],
            "pass_limit": 2,
            "accept_rule": "strict_improvement",
        },
        "budgeting": {
            "match_instance_size": True,
            "replay": False,
            "memory": False,
            "compression": False,
        },
        "robustness": {
            "scale_invariant": True,
            "distance_normalization": "none",
            "outlier_handling": "clamp_far_candidates",
        },
        "fallbacks": {
            "if_no_improvement": "keep_current_tour",
            "if_ties_persist": "deterministic_order",
        },
    }
