def build_heuristic():
    return {
        "name": "deterministic_heuristic",
        "technique": "random_replay",
        "parameters": {
            "replay_archive": [],  # No archive entries at initialization
            "candidate": 1,
            "heuristic_type": "greedy_nearest_neighbor",
            "distance_metric": "euclidean",
            "initial_state": "random_start_node",
            "termination_condition": "all_nodes_visited",
            "evaluation_metrics": ["robustness"],  # Focus on generalization performance
        },
        "constraints": {
            "max_route_length": None,  # No explicit route length limits
            "max_iterations": 1000,  # Limit iterations for robustness
        },
        "training_data": {
            "datasets": [
                "tsplib/att48", "tsplib/berlin52", "tsplib/gr666", "tsplib/lin318",
                "synthetic/clustered_points", "synthetic/linear_chain"
            ],
            "performance_metrics": ["train_loss", "validation_loss"],
            "evaluation_on": ["held_out_tsplib", "synthetic_transfer"]
        },
        "interpretability": "high",
        "complexity": "low",
        "robustness_score": None  # To be computed after training/evaluation
    }

