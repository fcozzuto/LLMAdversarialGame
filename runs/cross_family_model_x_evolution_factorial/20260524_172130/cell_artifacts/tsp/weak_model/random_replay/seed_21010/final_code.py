def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "description": "A straightforward heuristic for constrained TSP, focusing on robustness and interpretability.",
        "parameters": {
            "initial_strategy": "nearest_neighbor",
            "improvement_method": "2_opt",
            "max_iterations": 100,
            "tour_construction": {
                "method": "greedy",
                "start_node": "node_0"
            },
            "constraint_handling": {
                "capacity_limit": 1000,
                "time_window": None
            },
            "termination_criteria": {
                "max_no_improve": 10,
                "max_total_iterations": 200
            }
        },
        "heuristic_components": [
            {
                "component": "TourConstruction",
                "description": "Build initial tour using greedy nearest neighbor starting from node_0."
            },
            {
                "component": "LocalSearch",
                "description": "Iteratively improve tour using 2-opt swaps to reduce total distance."
            },
            {
                "component": "ConstraintVerification",
                "description": "Ensure constraints such as capacity are not violated; insert checks after each improvement."
            }
        ],
        "performance_goals": {
            "robustness": "Achieve consistent performance across TSPLIB instances and synthetic benchmarks.",
            "simplicity": "Maintain interpretability with minimal parameters and clear steps.",
            "transfer": "Demonstrate stable transfer performance without overfitting to training instances."
        }
    }

