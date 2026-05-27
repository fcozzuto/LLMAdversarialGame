def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initial_tour_method': 'greedy_insertion',   # approach used to generate initial tour
            'local_optimization': '2-opt',               # local optimization technique
            'budget_strategy': 'capacity_match',         # match resource budget
            'candidate_selection': 'nearest_insertion',  # insertion heuristic for expansion
            'termination_condition': 'max_iterations',   # stopping criterion
            'max_iterations': 1000,                        # number of iterations
            'cost_function': 'total_distance',           # objective to minimize
        },
        'interpretability': 'high',                      # prioritize interpretability
        'robustness_focus': 'balanced',                  # balance transfer and held-out performance
        'heuristic_notes': 'Deterministic approach using greedy insertion and 2-opt, matching budget constraints without replay or memory.', 
    }

