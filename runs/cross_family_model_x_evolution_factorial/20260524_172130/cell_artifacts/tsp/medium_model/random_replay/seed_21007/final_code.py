def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP heuristic
    # Keeps interpretability and balances robustness with held-out and synthetic transfer
    scaffold = {
        "name": "deterministic_constrained_tsp_heuristic_v1",
        "description": (
            "A simple, reproducible heuristic scaffold using a random_replay-like "
            "structure but without external archives. Focuses on robust performance "
            "across TSPLIB-like and synthetic transfer instances while remaining "
            "interpretable."
        ),
        "version": "1.0",
        "seed": 0,
        "strategy": {
            "initialization": {
                "method": "greedy_nearest_neighbor_with_constraints",
                "constraints": {
                    "max_distance_limit": None,  # no hard limit unless set by instance
                    "avoid_subtours": True,
                    "priority": ["must_include_depot", "prefer_high_degree_nodes"],
                },
            },
            "loop_closure": {
                "enabled": True,
                "method": "local_improvement_by_swap_and_2opt",
                "tie_breaker": "lower_index_first",
            },
            "augmentation": {
                "method": "seek_feasible_extension",
                "feasibility_checks": ["capacity_constraint", "precedence_constraints"],
                "limit_steps": 50,
            },
            "termination": {
                "method": "improvement_stopper",
                "improvement_threshold": 1e-6,
                "max_iterations": 200,
            },
        },
        "scalars": {
            "per_edge_cost": "given_by_instance",
            "penalties": {
                "subtour_penalty": 1000.0,
                "feasibility_penalty": 0.0,
            },
            "normalization": {
                "cost_scale": 1.0,
                "edge_cost_floor": 1e-6,
            },
        },
        "constraints": {
            "vehicle_count": 1,
            "capacity": "permutation_based",  # interpreted per instance
            "time_windows": False,
            "precedence": True,
            "subtour_elimination": True,
        },
        "transfer": {
            "training_mode": "no_archive",  # deterministic scaffold; no replay archive
            "transfer_type": "synthetic_and_heldout_robustness",
            "synthetic_mix": {
                "generated_instances": 0,
                "augmentation_ratio": 0.0,
            },
            "heldout_and_transfer": {
                "utilize_heldout": True,
                "transfer_focus": ["TSPLIB_like", "synthetic_transfer"],
                "randomization": False,
            },
        },
        "robustness": {
            "heldout_coverage": "balanced",
            "synthetic_span": [0.3, 0.9],
            "tsplib_coverage": [0.0, 0.7],
        },
        "interpretability": {
            "components": ["initialization", "loop_closure", "augmentation", "termination"],
            "logging": {
                "enabled": True,
                "level": "info",
                "trace": ["step", "decision", "improvement"],
            },
        },
        "random_replay_like": {
            "enabled": True,
            "archive_entries": 0,
            "deterministic_seed": 0,
            "replay_strategy": "none",  # no actual replay; scaffold focuses on structure
        },
        "notes": "This scaffold is deterministic, with no replay archive entries, and emphasizes robust coverage across TSPLIB-like and synthetic transfer instances while remaining interpretable."
    }
    return scaffold
