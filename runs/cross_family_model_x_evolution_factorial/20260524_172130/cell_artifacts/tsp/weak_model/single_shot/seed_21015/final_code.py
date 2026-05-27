def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "technique": "single_shot",
        "heuristic_type": "constrained_tsp",
        "approach": "nearest_neighbor_with_constraints",
        "parameters": {
            "initial_node_selection": "smallest_index",
            "neighbor_choice": "nearest_unvisited",
            "distance_metric": "euclidean",
            "constraint_handling": "check_feasibility_during_choice",
            "termination_condition": "all_nodes_visited",
            "additional_constraints": {
                "delivery_time_window": None,
                "pickup_delivery_mapping": None
            }
        },
        "robustness_focus": "balanced_transfer_performance",
        "interpretability": "high",
        "complexity": "simple",
        "training_eval": "heuristic tested on TSPLIB and synthetic instances with promising transfer performance"
    }

