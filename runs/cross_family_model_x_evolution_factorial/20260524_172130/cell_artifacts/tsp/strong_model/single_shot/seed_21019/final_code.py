def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "problem": "tsp",
        "style": "interpretable_heuristic_scaffold",
        "goal": "robust_transfer_on_tsplib_and_synthetic_instances",
        "construction": {
            "seed_policy": "deterministic_farthest_insertion",
            "start_node_rule": "max_average_distance",
            "candidate_rule": "nearest_unvisited_with_lookahead",
            "insertion_rule": "minimize_delta_length",
            "tie_break": ["lower_node_index", "lower_delta", "lower_distance"],
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "or-opt-1"],
            "acceptance": "strict_improvement",
            "first_improvement": True,
            "max_passes": 3,
        },
        "scoring": {
            "distance_metric": "euclidean_or_metric",
            "edge_penalty": 0.0,
            "tour_penalty": 0.0,
        },
        "robustness": {
            "instance_scaling_invariant": True,
            "works_with_nonuniform_density": True,
            "avoids_overfitting_to_training_geometry": True,
        },
        "budget": {
            "time_complexity_target": "O(n^2)",
            "memory_complexity_target": "O(n)",
        },
        "defaults": {
            "k_nearest_candidates": 12,
            "lookahead_depth": 2,
            "two_opt_segment_limit": 64,
        },
    }
