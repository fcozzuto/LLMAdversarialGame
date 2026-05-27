def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "parameters": {
            "initial_path_construction": "greedy_nearest_neighbor",
            "improve_local_search": ["2-opt", "or-opt"],
            "local_search_iterations": 100,
            "failure_tolerance": 10,
            "compression_ratio": 0.5,
            "replay_archive": None,
            "heuristic_robustness": "high",
            "training_instances": ["att48", "eil76", "berlin52"],
            "evaluation_instances": ["pr76", "kroA100", "usa13509"],
            "heuristic_interpretability": "medium",
            "complexity": "moderate",
            "failure_replay_enabled": True,
            "synthetic_transfer": True
        }
    }

