def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "technique": "single_shot",
        "candidate_id": 1,
        "description": "A deterministic heuristic for constrained TSP based on nearest neighbor and minimal transfer steps.",
        "parameters": {
            "initialization_method": "nearest_neighbor",
            "distance_metric": "euclidean",
            "transfer_strategy": "greedy",
            "transfer_limit": 5,
            "constrained_nodes": [],
            "heuristic_steps": [
                "initialize_tour_with_nearest_neighbor",
                "perform_transfer_with_minimal_cost",
                "complete_tour_with_closest_unvisited",
                "validate_constraints",
            ],
            "heuristic_score": 0.85,
            "training_eval": {
                "TSPLIB_instances": ["usa13509", "lin105", "pr76"],
                "synthetic_instances": ["synthetic_small", "synthetic_medium"],
                "performance_metric": "transfer_success_rate",
                "robustness_score": 0.78
            }
        }
    }

