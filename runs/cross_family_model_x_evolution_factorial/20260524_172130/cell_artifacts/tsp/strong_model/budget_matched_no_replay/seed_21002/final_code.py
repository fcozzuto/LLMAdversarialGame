def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "type": "tsp_heuristic_scaffold",
        "deterministic": True,
        "interpretable": True,
        "complexity": "moderate",
        "goal": "robust_held_out_transfer",
        "memory": {
            "replay": False,
            "failure_memory": False,
            "compression": False,
            "prior_candidates": 0,
        },
        "construction": {
            "method": "nearest_insertion",
            "seed_rule": "farthest_pair",
            "tie_break": "lexicographic",
            "candidate_limit": 12,
        },
        "improvement": {
            "method": "budget_matched_local_search",
            "moves": ["2-opt", "node_reinsert", "swap"],
            "move_order": ["2-opt", "node_reinsert", "swap"],
            "acceptance": "strict_improvement",
            "restart": False,
            "budget_policy": "match_construction_budget",
            "stagnation_limit": 3,
        },
        "robustness": {
            "distance_normalization": "scale_invariant",
            "geometry_aware": True,
            "outlier_guard": True,
            "small_instance_exact_bias": False,
        },
        "transfer_bias": {
            "favor_sparse_local_structure": True,
            "favor_global_spread_seed": True,
            "avoid_overfitting_to_degree_patterns": True,
        },
        "stopping": {
            "max_passes": 2,
            "max_no_improve_passes": 1,
        },
    }
