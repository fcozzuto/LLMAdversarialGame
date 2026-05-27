def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "technique": "budget_matched_no_replay",
        "parameters": {
            "node_selection": "nearest_unvisited",
            "edge_selection": "minimum_cost",
            "initial_solution": "nearest_neighbor",
            "local_improvement": "2-opt",
            "termination_condition": "max_runtime",
            "max_runtime_seconds": 60
        },
        "constraints": {
            "route_length": "budget_matched",
            "replay_memory": False,
            "failure_memory": False,
            "compression": False
        },
        "performance_requirements": {
            "robustness": "held_out_TSPLIB_and_synthetic_transfer",
            "interpretability": True,
            "complexity": "moderate"
        }
    }

