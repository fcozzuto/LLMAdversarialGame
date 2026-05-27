def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "problem": "tsp",
        "mode": "constrained_heuristic_scaffold",
        "objective": "minimize_tour_length",
        "deterministic": True,
        "interpretable": True,
        "complexity": "moderate",
        "transfer_priority": "held_out_tsplib_and_synthetic",
        "candidate_strategy": {
            "construction": "nearest_neighbor_with_lookahead",
            "lookahead_depth": 2,
            "tie_breaking": "lexicographic",
            "seed_policy": "fixed_small_set_of_start_nodes",
            "start_nodes": ["min_x", "min_y", "max_x", "max_y"],
            "multi_start_selection": "best_of_starts",
        },
        "improvement_strategy": {
            "local_search": ["2-opt", "or-opt-1"],
            "acceptance": "strict_improvement",
            "passes": 3,
            "first_improvement": True,
        },
        "constraint_handling": {
            "feasibility_first": True,
            "repair_method": "edge_swap_then_reconnect",
            "preserve_required_nodes": True,
        },
        "robustness": {
            "normalize_coordinates": True,
            "handle_degenerate_ties": True,
            "avoid_overfitting_to_euclidean_only": True,
            "use_distance_agnostic_structure": True,
        },
        "evaluation": {
            "score": "tour_length",
            "secondary_metrics": ["stability", "runtime"],
        },
    }
