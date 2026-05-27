def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "description": "A heuristic based on failure replay compression for constrained TSP instances.",
        "technique": "failure_replay_compression",
        "parameters": {
            "stop_after_iterations": 1000,
            "compression_ratio_threshold": 0.95,
            "replay_buffer_size": 50,
            "max_failure_replay_attempts": 10,
            "use_synthetic_transfer": True,
            "robustness_evaluation": True,
            "instance_types": ["TSPLIB", "synthetic"],
            "validation_instances": ["kroA100", "kroC100", "eil51", "berlin52"]
        },
        "heuristic_details": {
            "failure_replay": {
                "initialize": "greedy",
                "compression_method": "run-length encoding",
                "replay_strategy": "failures-based",
                "replay_buffer": "circular",
                "failure_threshold": 0.1,
                "adaptive_parameters": True
            }
        },
        "interpretability": "High",
        "complexity": "Moderate",
        "robustness": "Designed for transfer performance on held-out TSPLIB and synthetic instances."
    }

