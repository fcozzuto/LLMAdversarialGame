def build_heuristic():
    return {
        "name": "failure_replay",
        "archive": {},
        "parameters": {
            "max_iterations": 1000,
            "improvement_threshold": 1e-4,
            "replay_trials": 10,
            "restart_on_fail": True
        },
        "selection_strategy": "deterministic",
        "initial_solution_method": "nearest_neighbor",
        "improvement_method": "2-opt",
        "termination_condition": "max_iterations",
        "robustness_focus": "transfer_performance",
        "interpretable": True,
        "balanced_tradeoff": True
    }

