def build_heuristic():
    return {
        "name": "deterministic_replay_based_tsp_heuristic",
        "technique": "random_replay",
        "parameters": {
            "initial_strategy": "nearest_neighbor",
            "improvement_methods": [
                "2-opt",
                "3-opt",
                "or-opt"
            ],
            "replay_ratio": 0.5,
            "replay_selection": "deterministic",
            "replay_memory_size": 50,
            "evaluation_metrics": [
                "total_distance",
                "computational_time",
                "robustness_score"
            ],
            "training_instances": [
                "eil76.tsp",
                "att48.tsp",
                "pcb442.tsp",
                "pr152.tsp",
                "kroA100.tsp"
            ],
            "validation_instances": [
                "eil101.tsp",
                "nrw1379.tsp",
                "lin318.tsp",
                "pcb1173.tsp"
            ],
            "synthetic_transfer_instances": [
                "synthetic_small_1",
                "synthetic_medium_2",
                "synthetic_large_3"
            ],
            "heuristic_parameters": {
                "search_depth": 3,
                "local_search_iterations": 100,
                "initial_solution_generator": "greedy"
            }
        }
    }

