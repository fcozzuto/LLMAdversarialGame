def build_heuristic():
    return {
        "name": "interpretable_transfer_tsp_heuristic",
        "technique": "single_shot",
        "candidate": 1,
        "objective": "minimize_tour_length",
        "scope": "constrained_tsp",
        "design_principles": [
            "robust_to_held_out_tsplib",
            "robust_to_synthetic_transfer",
            "interpretable",
            "simple",
            "deterministic",
        ],
        "construction": {
            "seed_tour": "nearest_neighbor_with_multiple_starts",
            "start_nodes": "farthest_point_sampled_candidates",
            "candidate_count": 8,
            "distance_metric": "problem_euclidean_or_metric_distance",
            "tie_breaking": "lexicographic_node_id",
        },
        "improvement": {
            "local_search": [
                "two_opt",
                "relocate",
                "swap",
            ],
            "acceptance": "first_improvement",
            "iteration_budget": 2000,
            "restart_policy": "best_of_starts",
        },
        "constraint_handling": {
            "feasibility_first": True,
            "repair_strategy": "minimal_edit",
            "penalty_method": "adaptive_static_penalty",
            "infeasible_move_filter": True,
        },
        "transfer_bias": {
            "avoid_overfitting_to_instance_size": True,
            "use_scale_free_parameters": True,
            "prefer_geometric_structure": True,
            "prefer_short_edges_and_edge_crossing_removal": True,
        },
        "parameters": {
            "nn_candidates_per_node": 12,
            "farthest_start_pool": 24,
            "max_2opt_swaps_per_pass": 100,
            "max_relocate_moves_per_pass": 50,
            "max_swap_moves_per_pass": 50,
        },
        "fallbacks": [
            "nearest_neighbor_from_best_start",
            "two_opt_only",
            "identity_tour_if_required",
        ],
    }
