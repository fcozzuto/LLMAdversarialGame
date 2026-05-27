def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate": 1,
        "description": "Interpretable multi-start local search scaffold with randomization hooks for replay, prioritizing robust transfer on held-out TSPLIB and synthetic instances.",
        "objective": "minimize_tour_length",
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "stable_random",
        },
        "improvement": {
            "primary": ["2-opt", "or-opt-1"],
            "secondary": ["3-opt_limited"],
            "acceptance": "first_improvement",
            "restart_policy": "random_restarts",
            "restart_count": 8,
        },
        "randomization": {
            "seed_strategy": "deterministic_stream",
            "shuffle_edges": True,
            "candidate_sampling": "uniform_without_replacement",
        },
        "replay": {
            "enabled": True,
            "archive_entries": [],
            "selection": "none_available",
        },
        "constraints": {
            "time_budget_mode": "adaptive",
            "memory_mode": "low",
            "interpretability": "high",
        },
        "transfer_bias": {
            "favor_metric": "robustness_over_train_fit",
            "penalize_overfitting": True,
            "instance_features": ["n", "coordinate_scale", "spread", "aspect_ratio"],
        },
    }
