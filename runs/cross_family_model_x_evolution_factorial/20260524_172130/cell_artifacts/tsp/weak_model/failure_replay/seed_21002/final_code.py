def build_heuristic():
    return {
        "name": "failure_replay",
        "heuristic_type": "heuristic_scaffold",
        "parameters": {
            "initial_solution_method": "nearest_neighbor",
            "improvement_methods": [
                {"method": "2opt", "max_iterations": 100},
                {"method": "or_opt", "max_iterations": 50}
            ],
            "restart_strategy": {
                "type": "failure_replay",
                "max_restarts": 5,
                "termination_condition": "no_improvement"
            },
            "validation": {
                "test_instances": [
                    "eil51",
                    "pr1002",
                    "pcb442",
                    "rl5915",
                    "ftv170"
                ],
                "synthetic_transfers": true
            },
            "robustness": {
                "holdout_performance": "balanced",
                "performance_metrics": ["tour_length", "computational_time"]
            },
            "interpretability": true
        }
    }

