def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "technique": "single_shot",
        "parameters": {
            "initial_solution_method": "nearest_insertion",
            "improvement": "2-opt",
            "max_iterations": 1000,
            "seed": 42
        },
        "heuristic_type": "constructive",
        "description": "Constructs an initial route using nearest insertion, then refines with 2-opt. Deterministic with fixed seed for reproducibility.",
        "robustness_priority": "high",
        "interpretability": "high",
        "target_performance": {
            "held_out_TSPLIB": ">95% optimality",
            "synthetic_transfer": ">90% route quality"
        }
    }

