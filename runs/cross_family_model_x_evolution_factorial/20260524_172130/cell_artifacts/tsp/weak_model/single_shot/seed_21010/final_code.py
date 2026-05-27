def build_heuristic():
    return {
        "technique": "single_shot",
        "candidate": 1,
        "description": "A simple, deterministic nearest-neighbor heuristic optimized on a fixed set of TSPLIB instances, emphasizing interpretability and robustness.",
        "parameters": {
            "start_node": "deterministic",
            "selection_strategy": "nearest_neighbor",
            "lookahead": 1,
            "improvement": False
        },
        "performance_focus": "robust_transfer",
        "used_instances": [
            "a280", "att532", "berlin52", "brazil58", "ch130", "eil51", "kroA100", "rd100", "st70", "eil76"
        ],
        "training_instances": [
            "berlin52", "att532", "st70"
        ],
        "evaluation_instances": [
            "a280", "kroA100", "eil51", "brazil58", "ch130", "rd100", "eil76"
        ],
        "heuristic_details": {
            "method": "nearest_neighbor",
            "start_point": "deterministic_first_node",
            "heuristic_goal": "quick_bad_solution",
            "robustness": "acceptable on unseen instances",
            "interpretability": "high",
            "complexity": "low"
        }
    }

