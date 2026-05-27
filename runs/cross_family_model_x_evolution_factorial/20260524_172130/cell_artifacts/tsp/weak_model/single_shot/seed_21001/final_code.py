def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "technique": "single_shot",
        "candidate_id": 1,
        "description": "A simple, deterministic heuristic based on immediate nearest neighbor selection with predefined parameters to ensure robustness and interpretability.",
        "parameters": {
            "initial_selection": "nearest_neighbor",
            "improve_method": "2_opt",
            "max_iterations": 100,
            "stop_criteria": "no_improvement",
            "use_transfer_robustness": True,
            "robustness_check": "held_out_tsplib_and_synthetic",
            "scoring_function": "distance_sum",
            "interpreter": "greedy_nearest_neighbor_with_2opt"
        }
    }

