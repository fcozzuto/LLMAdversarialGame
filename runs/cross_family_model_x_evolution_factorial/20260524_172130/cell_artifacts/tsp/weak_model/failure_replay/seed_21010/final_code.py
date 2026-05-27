def build_heuristic():
    return {
        "name": "failure_replay",
        "technique": "failure_replay",
        "description": "A simple, interpretable heuristic based on failure replay with deterministic parameters.",
        "parameters": {
            "initial_solution": "nearest_neighbor",
            "improvement_strategy": "2opt",
            "max_iterations": 1000,
            "restart_threshold": 10,
            "acceptance_criteria": "improvement_only",
            "failure_replay": True,
            "failure_threshold": 5,
            "success_threshold": 3,
            "deterministic_seed": 42,
            "instance_inclusion": ["ehrgott", "att48", "lin318", "tsp225"],
            "robustness_checks": True
        }
    }

