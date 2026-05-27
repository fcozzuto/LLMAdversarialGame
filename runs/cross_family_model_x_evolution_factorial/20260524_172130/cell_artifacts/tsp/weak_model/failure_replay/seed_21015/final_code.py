def build_heuristic():
    return {
        "name": "failure_replay",
        "description": "A deterministic heuristic using failure replay strategy for TSP",
        "parameters": {
            "initial_solver": "nearest_neighbor",
            "max_iterations": 100,
            "failure_replay_strategy": {
                "type": "revisit_failed_edges",
                "failure_threshold": 3,
                "retry_limit": 10,
                "edge_selection_heuristic": "most_failed_edges",
                "termination_condition": "no_improvement_over_10_iterations"
            },
            "output": {
                "method": "best_solution",
                "selection_criteria": "shortest_tour_length"
            }
        },
        "notes": "This heuristic prioritizes robustness on both TSPLIB and synthetic instances, favoring interpretability and simplicity."
    }

