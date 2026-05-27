def build_heuristic():
    return {
        "name": "deterministic_transfer_scaffold",
        "construction": {
            "seed_mode": "farthest_from_centroid",
            "candidate_limit": 12,
            "lookahead_limit": 3,
            "distance_weight": 1.0,
            "density_penalty": 0.15,
            "angle_penalty": 0.07,
            "regret_bonus": 0.05,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.12,
        },
        "local_search": {
            "two_opt_passes": 2,
            "two_opt_candidate_limit": 14,
            "use_three_opt": False,
            "three_opt_samples": 0,
            "or_opt_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
            "strength": 1,
            "attempts": 1,
        },
        "restart": {
            "restart_count": 3,
            "seed_pool_size": 4,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
        "transfer": {
            "enabled": True,
            "source_families": ["kroA", "kroB", "vrp"],
            "transfer_weight": 0.9,
            "synthetic_transfer_balance": 0.5,
            "transfer_schedule": "balanced",
        },
        "robustness": {
            "holdout_tsplib": True,
            "synthetic_transfer": True,
            "variance_guard": 0.02,
        },
    }
