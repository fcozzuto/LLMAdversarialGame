def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "deterministic": True,
        "goal": "robust_transfer_on_TSP",
        "interpretability": "high",
        "complexity": "moderate",
        "replay_archive": {
            "available": False,
            "entries": [],
            "compression": {
                "mode": "none",
                "policy": "defer_until_failures_exist",
            },
        },
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lowest_index",
        },
        "improvement": {
            "primary": "2-opt",
            "secondary": "or-opt-1",
            "search_order": "best_improvement_then_first_improvement",
            "stopping": {
                "max_no_improve_passes": 2,
                "max_restarts": 0,
            },
        },
        "failure_replay": {
            "enabled": True,
            "trigger": "stagnation_or_regression",
            "store": ["edge_set", "tour_length", "move_context"],
            "compression": {
                "retain": "smallest_regressions",
                "deduplicate": True,
                "canonicalize": True,
            },
        },
        "perturbation": {
            "enabled": True,
            "method": "double_bridge",
            "strength": "light",
            "schedule": "only_after_local_optimum",
        },
        "acceptance": {
            "policy": "strict_improvement",
            "allow_equal": False,
        },
        "heldout_bias": {
            "favor_sparse_geometric_instances": True,
            "favor_scale_robust_moves": True,
            "avoid_overfitting_to_fixed_size_patterns": True,
        },
        "fallback": {
            "when_no_improvement": "return_best_seen",
            "when_archive_empty": "use_base_local_search",
        },
    }
