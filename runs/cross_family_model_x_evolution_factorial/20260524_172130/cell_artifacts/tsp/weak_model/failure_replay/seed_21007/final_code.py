def build_heuristic():
    return {
        "name": "failure_replay",
        "strategy": "failure_replay",
        "parameters": {
            "max_attempts": 100,
            "retry_limit": 5,
        },
        "heuristic_components": [
            {
                "type": "nearest_neighbor",
                "name": "initial_solution",
                "parameters": {
                    "start_node": 0
                }
            },
            {
                "type": "2_opt",
                "name": "local_search_2opt",
                "parameters": {
                    "max_iterations": 1000
                }
            },
            {
                "type": "penalty_adjustment",
                "name": "penalty_tuning",
                "parameters": {
                    "penalty_increment": 1.0,
                    "penalty_decrement": 0.5,
                    "max_penalty": 10.0
                }
            }
        ],
        "failure_replay": {
            "archive": [],
            "max_replays": 50,
            "seed": 42
        },
        "robustness": {
            "evaluation_datasets": [
                "TSPLIB",
                "synthetic_transfer"
            ],
            "performance_metrics": [
                "total_distance",
                "computational_time"
            ],
            "robustness_score_weight": 1.0
        }
    }

