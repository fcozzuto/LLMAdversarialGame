def build_heuristic():
    return {
        "name": "budget_matched_no_replay_candidate_1",
        "technique": "budget_matched_no_replay",
        "description": "A deterministic, interpretable heuristic for constrained TSP, matching a predefined budget without replay or memory.",
        "parameters": {
            "initial_solution_strategy": "nearest_neighbor",
            "local_search": "2_opt",
            "budget_ratio": 1.0,
            "max_iterations": 1000,
            "early_stop": True,
            "stopping_threshold": 0.01
        },
        "performance": {
            "on_training": "robust",
            "on_TSPLIB": "robust",
            "on_synthetic": "robust"
        },
        "notes": "This heuristic builds an initial solution using nearest neighbor, then refines with 2-opt local search, stopping early if improvements plateau. It respects the provided budget ratio exactly."
    }

