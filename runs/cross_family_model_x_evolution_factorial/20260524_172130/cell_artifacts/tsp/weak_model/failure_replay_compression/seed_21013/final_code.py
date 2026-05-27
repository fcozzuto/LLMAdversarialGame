def build_heuristic():
    return {
        "technique": "failure_replay_compression",
        "parameters": {
            "max_replay_size": 100,
            "compression_ratio": 0.5,
            "trigger_failure_threshold": 0.3,
            "max_iterations": 50,
            "initial_solution_algorithm": "nearest_neighbor",
            "local_search_methods": ["2-opt", "or-opt"],
            "failure_replay": {
                "enabled": True,
                "failure_threshold": 0.2
            },
            "robustness_checks": True,
            "training_data": ["eil51", "berlin52", "pr2392"],
            "validation_data": ["kroA100", "kroB100"],
            "synthetic_transfer": ["linear", "cyclic"]
        }
    }

