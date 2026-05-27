def build_heuristic():
    return {
        "name": "robust_interpretable_tsp_scaffold",
        "technique": "single_shot",
        "candidate": 1,
        "objective": "minimize_tour_length",
        "construction": {
            "method": "multi_start_greedy",
            "starts": ["nearest_neighbor", "farthest_insertion", "min_edge_seed"],
            "seed_selection": "deterministic_extremes_and_centroid",
            "tie_break": "lexicographic",
            "edge_policy": "prefer_short_edges_with_diversification"
        },
        "improvement": {
            "local_search": ["two_opt", "three_opt_lite"],
            "acceptance": "first_improvement",
            "restart_policy": "best_of_starts",
            "stagnation_limit": 20
        },
        "robustness": {
            "transfer_bias": "favor_geometry_agnostic_baselines",
            "held_out_generalization": "high",
            "avoid_overfitting": True,
            "complexity": "moderate"
        },
        "features": {
            "uses_coordinates": True,
            "uses_distance_matrix": True,
            "supports_symmetric_tsp": True,
            "supports_euclidean_like_instances": True
        },
        "parameters": {
            "candidate_neighbor_limit": 16,
            "start_count": 5,
            "insertion_weight": 0.7,
            "improvement_budget": 2000
        }
    }
