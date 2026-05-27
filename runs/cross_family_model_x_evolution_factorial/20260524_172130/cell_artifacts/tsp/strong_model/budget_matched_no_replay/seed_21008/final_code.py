def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 1,
        "deterministic": True,
        "imports": [],
        "memory": {
            "prior_candidates": False,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "objective": {
            "primary": "tour_length",
            "secondary": "generalization_to_heldout_tsplib_and_synthetic",
        },
        "scaffold": {
            "construction": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "local_search": ["2-opt", "segment_relink"],
            "acceptance": "strict_improvement",
            "restart_policy": "none",
        },
        "budget_matching": {
            "enabled": True,
            "match_to_instance_size": True,
            "small_instance_moves": 1,
            "medium_instance_moves": 2,
            "large_instance_moves": 3,
        },
        "transfer_bias": {
            "prefer_metric_geometry": True,
            "avoid_instance_specific_tuning": True,
            "use_scale_normalization": True,
        },
        "interpretability": {
            "simple_components_only": True,
            "explainable_move_order": True,
        },
    }
