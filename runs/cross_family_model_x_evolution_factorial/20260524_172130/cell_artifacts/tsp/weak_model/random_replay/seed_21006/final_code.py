def build_heuristic():
    return {
        "name": "deterministic_tsp_heuristic",
        "description": "A robust, interpretable heuristic for constrained TSP, focusing on generalization across TSPLIB and synthetic instances.",
        "techniques": [
            {
                "type": "nearest_neighbor",
                "parameters": {
                    "starting_point": "closest",
                    "sampling_strategy": "deterministic"
                }
            },
            {
                "type": "2_opt",
                "parameters": {
                    "improve": True,
                    "max_iterations": 100
                }
            },
            {
                "type": "constraint_handling",
                "parameters": {
                    "capacity_limit": 100,
                    "time_window": None,
                    "penalty_method": "hard"
                }
            }
        ],
        "selection_strategy": "greedy",
        "evaluation_criteria": [
            "total_tour_length",
            "constraint_violation"
        ],
        "robustness_features": {
            "multi_instance_training": True,
            "cross_validation": True,
            "performance_metrics": [
                "average_tour_length",
                "standard_deviation",
                "success_rate_on_constraints"
            ]
        }
    }

