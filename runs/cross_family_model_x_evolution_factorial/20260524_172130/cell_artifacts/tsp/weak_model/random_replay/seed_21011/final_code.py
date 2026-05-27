def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "description": "A robust, deterministic heuristic for constrained TSP, favoring interpretability and transferability.",
        "parameters": {
            "initial_solution_method": "nearest_neighbor",
            "improvement_strategy": "2-Opt",
            "max_iterations": 1000,
            "delta_threshold": 1e-4,
            "use_constant_penalties": True,
            "penalty_coefficient": 1.0,
            "constraint_handling": "soft_with_penalties",
            "heuristic_variants": ["greedy_construction", "local_search"]
        },
        "rules": {
            "construct_solution": {
                "method": "nearest_neighbor",
                "parameters": {
                    "start_node": "random",
                    "random_seed": 42
                }
            },
            "improve_solution": {
                "method": "2-opt",
                "parameters": {
                    "max_iterations": 1000,
                    "delta_threshold": 1e-4
                }
            },
            "constraint_management": {
                "approach": "soft_penalty",
                "penalty_factor": 1.0
            },
            "record": {
                "enable": False
            }
        }
    }

