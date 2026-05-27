def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "heuristic": {
            "name": "interpretable_tsp_scaffold",
            "construction": {
                "method": "nearest_neighbor",
                "start_policy": "best_of_fixed_seeds",
                "fixed_seeds": [0, 1, 2, 3],
                "tie_break": "lowest_index",
            },
            "improvement": {
                "primary": "2-opt",
                "acceptance": "first_improvement",
                "candidate_filter": "don_t_consider_edges_longer_than_median_times_3",
                "max_passes": 8,
                "stop_when_no_change": True,
            },
            "diversification": {
                "method": "double_bridge",
                "enabled": True,
                "restarts": 2,
                "apply_after_stagnation_passes": 2,
            },
            "robustness_bias": {
                "prefer_short_edges": True,
                "avoid_overfitting_to_training_geometry": True,
                "use_sparse_locality_only": False,
            },
            "evaluation": {
                "objective": "tour_length",
                "deterministic": True,
            },
        },
    }
