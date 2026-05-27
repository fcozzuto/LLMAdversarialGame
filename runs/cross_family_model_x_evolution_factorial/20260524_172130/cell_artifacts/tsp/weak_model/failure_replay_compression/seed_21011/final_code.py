def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "techniques": ["failure_replay_compression"],
        "candidate": 1,
        "description": "A simple, deterministic heuristic using failure replay compression, favoring robustness on TSPLIB and synthetic instances.",
        "parameters": {
            "initial_solution_method": "greedy_nearest_neighbor",
            "local_search": {
                "method": "2_opt",
                "max_iterations": 100,
                "improvement_threshold": 1e-6
            },
            "failure_replay_compression": {
                "enable": True,
                "max_replays": 50,
                "consolidation_threshold": 0.01
            }
        },
        "heuristic_properties": {
            "robustness": "high",
            "interpretability": "high",
            "complexity": "low",
            "applicability": ["TSPLIB", "synthetic"]
        }
    }

