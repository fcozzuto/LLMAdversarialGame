def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "type": "tsp_heuristic_scaffold",
        "deterministic": True,
        "goal": "robust_transfer_to_held_out_tsplib_and_synthetic_instances",
        "interpretability": "high",
        "complexity": "moderate",
        "construction": {
            "start_rule": "farthest_from_centroid",
            "initial_tour": "nearest_insertion",
            "tie_breaking": "lexicographic",
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "or-opt-1"],
            "pass_limit": 3,
            "first_improvement": True,
        },
        "candidate_filtering": {
            "restrict_to_k_nearest": 20,
            "use_edge_pruning": True,
            "pruning_rule": "symmetric_distance_threshold",
        },
        "robustness": {
            "multi_start": 3,
            "starts": ["farthest_from_centroid", "min_x", "min_y"],
            "choose_best_by": "tour_length",
        },
        "scoring": {
            "objective": "minimize_tour_length",
            "secondary": ["reduce_crossings", "preserve_planarity_bias"],
        },
        "fallbacks": {
            "if_degenerate": "greedy_nearest_neighbor",
            "if_tie": "stable_deterministic_order",
        },
        "notes": [
            "Designed for strong held-out generalization without heavy tuning.",
            "Keeps the scaffold simple, transparent, and deterministic.",
        ],
    }
