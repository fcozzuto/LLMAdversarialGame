def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a simple,
    # interpretable approach suitable for held-out TSPLIB and synthetic transfer
    # evaluation. This scaffold emphasizes robustness over complexity and
    # provides clear hooks for failure_replay-style replay behavior.
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": "1.0",
        "description": "Deterministic, interpretable constrained TSP heuristic scaffold with placeholders for failure replay.",
        "strategy": {
            "preprocess": {
                "normalize_coordinates": True,
                "resolve_disconnected": True,
                "degenerate_points": False,
            },
            "constraint_handling": {
                "time_window": {
                    "enabled": True,
                    "window_open": 0.0,
                    "window_close": 24.0,
                    "penalty": 1000.0
                },
                "capacity": {
                    "enabled": True,
                    "vehicle_capacity": 100,
                    "demand_tolerance": 0.05
                },
            },
            "routing_heuristic": {
                "base_method": "nearest_neighbor_with_lookahead",
                "lookahead_steps": 2,
                "tie_breaker": "lower_index",
                "local_search": {
                    "enabled": True,
                    "move_types": ["2-opt", "swap"],
                    "iterations": 50
                }
            },
            "multi_route": {
                "enabled": False,
                "aggregation": "sequential_concat",
            }
        },
        "failure_replay": {
            "enabled": True,
            "archive": "none",
            "replay_strategy": "deterministic_fallback",
            "fallback_steps": [
                "use_corner_case_boundaries",
                "split_large_demand",
                "retry_with_smaller_stepsize"
            ],
            "diagnostics": {
                "log_levels": ["WARNING", "ERROR"],
                "record_route_quality": True
            }
        },
        "transfer_robustness": {
            "synthetic_transfer": {
                "enabled": True,
                "domains": ["synthetic_high_variance", "synthetic_surface"],
                "metrics": ["cost_increase", "time_increase", "feasibility_rate"],
            },
            "held_out_tsplib": {
                "enabled": True,
                "test_sets": ["browcar", "kroA", "kroB"],
                "minimization_goal": "cost",
            }
        },
        "interpretability": {
            "log_summaries": True,
            "traceability": {
                "route_prefix": "heur_scaffold",
                "step_logging": True
            }
        },
        "parameters": {
            "seed": 1,
            "distance_scaling": 1.0,
            "time_window_penalty": 1000.0,
            "capacity_penalty": 0.0
        }
    }
