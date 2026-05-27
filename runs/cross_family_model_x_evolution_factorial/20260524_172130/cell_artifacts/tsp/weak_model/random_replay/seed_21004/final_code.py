def build_heuristic():
    return {
        "name": "deterministic_replay_candidate_1",
        "technique": "random_replay",
        "parameters": {
            "replay_archive": [],
            "initial_solution_method": "nearest_neighbor",
            "local_search": {
                "method": "2_opt",
                "max_iterations": 1000
            },
            "metaheuristics": {
                "restart_strategy": "best_improvement",
                "restart_limit": 50
            }
        },
        "performance_focus": "robust_transfer",
        "tested_on": ["TSPLIB", "synthetic_transfer"],
        "interpretability": True,
        "complexity": "moderate"
    }

