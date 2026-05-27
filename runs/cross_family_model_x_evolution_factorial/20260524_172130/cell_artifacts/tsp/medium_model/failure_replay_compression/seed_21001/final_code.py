def build_heuristic():
    return {
        "name": "nn_restarts_2opt_refined_v2",
        "construction": {
            "seed_mode": "farthest_from_centroid",
            "candidate_limit": 14,  # slight expansion for robustness
            "lookahead_limit": 5,
            "distance_weight": 1.0,
            "density_penalty": 0.14,  # small tweak for robustness
            "angle_penalty": 0.11,    # modestly increased to discourage sharp turns
            "regret_bonus": 0.06,       # mild bonus for higher-regret paths
            "cluster_mode": "none",
            "cluster_count": 1,
            "cluster_bonus": 0.13,
        },
        "local_search": {
            "two_opt_passes": 3,
            "two_opt_candidate_limit": 18,  # higher to explore more
            "use_three_opt": True,
            "three_opt_samples": 6,          # targeted three-opt sampling
            "or_opt_span": 2,
        },
        "perturbation": {
            "enabled": True,
            "mode": "double_bridge",
            "strength": 1,
            "attempts": 1,
        },
        "restart": {
            "restart_count": 4,              # increased restarts for resilience
            "seed_pool_size": 6,
            "use_perturbation_restarts": True,
        },
        "acceptance": {
            "mode": "improving_only",
            "worse_acceptance_threshold": 0.0,
            "annealing_temperature": 0.0,
        },
        "metrics": {
            "train_skip_fraction": 0.0,
            "validation_skip_fraction": 0.0,
            "tsplib_eval": True,
        },
        "constraints": {
            "max_tour_time_ratio": 1.1,      # avoid extreme tours
            "min_improvement_per_restart": 0.0005,
        },
        "transfers": {
            "enabled": True,
            "synthetic_transfer_ratio": 0.5,  # balance synthetic and TSPLIB exposure
            "transfer_batches": 2,
        },
    }
