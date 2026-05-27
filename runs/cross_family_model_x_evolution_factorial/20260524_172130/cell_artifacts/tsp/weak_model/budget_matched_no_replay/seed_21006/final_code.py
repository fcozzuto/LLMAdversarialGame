def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "description": "A simple, deterministic heuristic for constrained TSP that matches a budget constraint without using replay memory or failure memory.",
        "technique": "budget_matched_no_replay",
        "parameters": {
            "initial_solution_strategy": "greedy_insertion",  # start with a greedy insertion heuristic
            "refinement_steps": 2,                             # number of local refinement iterations
            "distance_metric": "euclidean",                    # use Euclidean distance
            "budget_constraint": "approximate",                # approximate the budget constraint
            "heuristic_sorting": "shortest_edge_first",        # prioritize shortest edges
        },
        "heuristic_details": {
            "initial_solution": "construct_initial_solution",
            "refinement_method": "2-opt",
            "constraint_handling": "match_budget_closest",
            "robustness_considerations": "test_on_TSPLIB_and_synthetic",
            "complexity": "O(n^2)",  # basic quadratic complexity for small to medium instances
        },
        "additional_notes": "This heuristic focuses on creating a feasible route that closely matches the given budget without complex memory structures, emphasizing interpretability and cross-instance robustness."
    }

