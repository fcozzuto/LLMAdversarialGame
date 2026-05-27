def build_heuristic():
    return {
        "name": "nn_restarts_2opt",
        "construction": {
            "seed_mode": "farthest_from_centroid",
            "candidate_limit": 14,
            "lookahead_limit": 3,
            "distance_weight": 1.0,
            "density_penalty": 0.18,
            "angle_penalty": 0.08,
            "regret_bonus": 0.06,
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.16,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 18,
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
            "restart_count": 4,
            "seed_pool_size": 4,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
    }
