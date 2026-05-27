def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "type": "tsp_heuristic_scaffold",
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "no_replay": True,
            "no_memory": True,
            "budget_matched": True,
            "target_generalization": ["tsplib", "synthetic"],
        },
        "construction": {
            "init": "nearest_neighbor",
            "start_rule": "best_of_k",
            "k_starts": 5,
            "tie_break": "lexicographic",
        },
        "candidate_generation": {
            "primary": "2-opt_greedy",
            "secondary": "3-opt_limited",
            "move_order": ["shortest_gain_first", "bounded_randomized?"],
            "bounded_randomized": False,
            "candidate_sets": "alpha_nearest",
            "alpha": 20,
        },
        "local_search": {
            "phases": [
                {"name": "2-opt", "passes": 2, "accept": "strict_improvement"},
                {"name": "node_reinsertion", "passes": 1, "accept": "strict_improvement"},
                {"name": "3-opt", "passes": 1, "accept": "strict_improvement_limited"},
            ],
            "terminate_on_first_improvement": False,
            "max_no_improve_rounds": 2,
        },
        "budget_allocation": {
            "construction_share": 0.15,
            "improvement_share": 0.75,
            "final_polish_share": 0.10,
            "matched_to_instance_size": True,
            "small_instance_threshold": 200,
            "large_instance_threshold": 1000,
        },
        "final_polish": {
            "method": "2-opt",
            "passes": 1,
            "accept": "strict_improvement",
        },
        "robustness": {
            "avoid_overfitting": True,
            "use_problem_scaling": True,
            "distance_normalization": "implicit",
            "parameter_defaults": "conservative",
        },
        "scoring": {
            "objective": "tour_length",
            "secondary": "runtime",
            "lexicographic": True,
        },
    }
