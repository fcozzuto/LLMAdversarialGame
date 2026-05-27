def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with failure_replay_compression approach placeholder.",
        "technique": "failure_replay_compression",
        "replay_archive": {
            "has_entries": False,
            "entries": []
        },
        "parameters": {
            "determinism": True,
            "seed": 42,
            "max_iterations": 1000,
            "initial_solution": "greedy_constrained",
            "improvement_heuristic": "2opt_swap_with_feasibility",
            "feasibility_check": "validate_constraints",  # e.g., time windows, capacities, precedence
            "constraint_handling": {
                "types": ["capacity", "time_window", "precedence"],
                "penalty_method": "hard_feasibility"  # enforce feasible solutions only
            },
            "stopping_criteria": {
                "no_improvement_epochs": 50,
                "time_limit_seconds": 0  # placeholder; deterministic run uses iterations
            },
            "metrics": ["tour_length", "feasibility_rate", "computation_steps"]
        },
        "scope": {
            "challenge_types": ["TSPLIB_constrained", "synthetic_transfer"],
            "env": "deterministic_offline",
            "robustness_focus": ["holdout_tsplib", "synthetic_transfer_performance"]
        },
        "scaffold": {
            "high_level": [
                "generate_initial_feasible_solution",
                "iterate_improvement_with_feasibility",
                "record_failure_replays_if_relevant",
                "select_best_feasible_solution"
            ],
            "heuristic_primitives": {
                "initialization": ["greedy_constrained"],
                "neighbors": ["2-opt_swap", "relocate", "exchange"],
                "feasibility": ["verify_capacity", "verify_time_windows"],
                "termination": ["iterations", "no_improvement"]
            }
        },
        "deterministic_flags": {
            "shuffle": False,
            "random_choices": False
        }
    }
