def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "description": "A simple, interpretable TSP heuristic using nearest neighbor initialization and 2-opt optimization.",
        "initialization": {
            "method": "nearest_neighbor",
            "start_node": "deterministic_first_node"
        },
        "optimization": {
            "method": "2-opt",
            "iterations": 100,
            "stopping_condition": "no_improvement",
            "improvement_threshold": 1e-6
        },
        "parameters": {
            "neighbor_selection": "closest",
            "use_2_opt": True,
            "max_iterations": 100
        },
        "robustness": {
            "tested_on": ["TSPLIB_reliable", "synthetic_transfer"],
            "performance_considered": ["training", "held-out"],
            "heuristic_stability": "deterministic",
            "repeatability": True
        },
        "interpretability": {
            "heuristic_type": "heuristic",
            "actions": ["nearest neighbor initialization", "2-opt local search"],
            "parameters_explanation": {
                "nearest_neighbor": "Start from a fixed node to ensure reproducibility.",
                "2-opt": "Iteratively swap edges to reduce tour length."
            }
        }
    }

