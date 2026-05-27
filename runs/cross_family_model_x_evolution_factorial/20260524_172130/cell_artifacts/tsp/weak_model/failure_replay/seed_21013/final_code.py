def build_heuristic():
    return {
        "name": "failure_replay",
        "technique": "failure_replay",
        "parameters": {
            "initial_seed": 42,
            "max_retries": 100,
            "attempts_per_retry": 10,
            "confidence_threshold": 0.95,
            "selection_strategy": "deterministic",
            "replay_archives": [],
            "heuristic_components": [
                {
                    "type": "nearest_neighbor",
                    "parameters": {
                        "initial_node": None,
                        "skip_nodes": [],
                        "stopping_condition": "tour_complete"
                    }
                },
                {
                    "type": "2_opt",
                    "parameters": {
                        "max_iterations": 100,
                        "acceptance_condition": "improvement"
                    }
                }
            ],
            "evaluation_metrics": [
                "tour_length",
                "robustness_on_TSPLIB_and_synthetic"
            ]
        }
    }

