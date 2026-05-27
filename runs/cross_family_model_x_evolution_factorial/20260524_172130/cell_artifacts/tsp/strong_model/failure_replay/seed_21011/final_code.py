def build_heuristic():
    return {
        "name": "failure_replay",
        "candidate": 1,
        "assumptions": {
            "problem": "symmetric_euclidean_tsp",
            "objective": "minimize_tour_length",
            "deterministic": True,
            "no_replay_archive_entries": True,
        },
        "representation": {
            "tour": "permutation",
            "construction": "nearest_neighbor_seeded",
            "local_search": ["2-opt", "or-opt-1"],
        },
        "construction": {
            "seed_rule": "farthest_from_centroid",
            "candidate_list": "k_nearest_by_distance",
            "k": 16,
            "tie_break": "lowest_index",
        },
        "failure_replay": {
            "enabled": True,
            "archive_policy": "empty_initially",
            "trigger": "repeat_failures_on_structurally_similar_instances",
            "similarity_features": [
                "n",
                "bounding_box_aspect",
                "distance_cv",
                "nearest_neighbor_gap",
            ],
            "replay_action": "prioritize_alternative_seed_and_perturbation_patterns",
        },
        "local_search": {
            "two_opt": {
                "enabled": True,
                "candidate_restriction": "k_nearest",
                "k": 20,
                "first_improvement": True,
                "max_passes": 5,
            },
            "or_opt_1": {
                "enabled": True,
                "first_improvement": True,
                "max_passes": 2,
            },
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
            "strength": "low",
            "attempts": 2,
            "only_on_plateau": True,
        },
        "selection": {
            "multi_start": 4,
            "start_nodes": "extremes_and_centroid_proximal",
            "best_of_all": True,
        },
        "stopping": {
            "improvement_rounds": 2,
            "max_total_iterations": 50,
        },
        "robustness": {
            "favor_generalization": True,
            "avoid_instance_specific_tuning": True,
            "geometry_normalization": ["center", "scale_to_unit_box"],
        },
    }
