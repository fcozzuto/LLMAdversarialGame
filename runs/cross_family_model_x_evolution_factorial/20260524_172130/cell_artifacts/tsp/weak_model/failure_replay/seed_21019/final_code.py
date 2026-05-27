def build_heuristic():
    return {
        "name": "failure_replay",
        "description": "A deterministic heuristic for constrained TSP using a simple failure-replay approach.",
        "parameters": {
            "initial_solution_strategy": "nearest_neighbor",
            "failure_limit": 100,
            "replay_max_paths": 10,
            "replay_threshold": 0.05,
            "use_distance_matrix": True,
            "improve_with_local_search": True,
            "local_search_iterations": 100,
            "candidate_selection_method": "greedy",
            "robustness_criteria": {
                "tested_instances": ["p06", "pcb442", "eil101", "kroA100", "brg180"],
                "performance_metric": "total_distance",
                "max_variance": 0.02
            },
            "fallback_strategy": "greedy_insertion"
        }
    }

