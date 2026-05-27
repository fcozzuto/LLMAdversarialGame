def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "problem": "tsp",
        "style": "interpretable_constructive_with_local_improvement",
        "deterministic": True,
        "no_memory": True,
        "no_replay": True,
        "no_compression": True,
        "objective": "minimize_tour_length",
        "construction": {
            "method": "farthest_insertion",
            "seed_selection": "max_pairwise_distance",
            "tie_break": "lexicographic",
            "insertion_rule": "minimum_increase",
            "candidate_filter": "nearest_k",
            "nearest_k": 12
        },
        "local_search": {
            "enabled": True,
            "passes": 2,
            "operators": ["two_opt", "relocate"],
            "acceptance": "strict_improvement",
            "move_order": "best_first"
        },
        "robustness": {
            "normalize_coordinates": True,
            "use_euclidean_geometry": True,
            "scale_invariant": True,
            "translation_invariant": True,
            "rotation_invariant": True
        },
        "transfer_bias": {
            "prefer_global_structure": True,
            "avoid_overfitting_to_instance_size": True,
            "balanced_exploration_exploitation": True
        },
        "fallbacks": {
            "small_n": "nearest_neighbor_with_2opt",
            "degenerate_geometry": "lexicographic_closest_pair",
            "default": "farthest_insertion_with_local_search"
        }
    }
