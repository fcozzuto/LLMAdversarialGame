def build_heuristic():
    return {
        "technique": "failure_replay_compression",
        "parameters": {
            "max_retries": 3,
            "compression_threshold": 0.05,
            "use_replay_archive": False,
            "initial_heuristic": "nearest_neighbor",
            "improvement_strategy": "2-opt",
            "max_iterations": 10000,
            "validation_instances": [
                "berlin52",
                "eil51",
                "kroA100",
                "pcb1173",
                "pr2392"
            ],
            "training_instances": [
                "att48",
                "eil76",
                "lin318",
                "pcb1173"
            ],
            "heuristic_parameters": {
                "local_search": {
                    "method": "2-opt",
                    "max_no_improve": 100
                },
                "initial_solution": {
                    "method": "nearest_neighbor"
                }
            }
        }
    }

