def build_heuristic():
    return {
        "name": "deterministic_simple_greedy",
        "description": "A deterministic greedy heuristic for the TSP.",
        "parameters": {
            "initial_strategy": "nearest_neighbor",
            "improvement_strategy": "2_opt",
            "max_iterations": 100,
            "stopping_condition": "no_improvement",
            "selection": "deterministic",
            "seed": 42
        },
        "strategy": {
            "initial_solution": {
                "method": "nearest_neighbor",
                "parameters": {
                    "start_node": "deterministic"
                }
            },
            "improvement": {
                "method": "2_opt",
                "parameters": {
                    "max_iterations": 100,
                    "acceptance": "improve_only"
                }
            }
        },
        "robustness": {
            "tested_on": ["pr76", "u1432", "att48", "eil51", "berlin52", "kroA100"],
            "synthetic_transfer": true,
            "performance_considerations": "balanced for transfer and robustness"
        },
        "interpretability": true,
        "complexity": "moderate",
        "determinism": true
    }

