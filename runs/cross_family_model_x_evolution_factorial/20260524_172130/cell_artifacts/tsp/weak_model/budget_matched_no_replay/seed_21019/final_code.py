def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initial_tour_method': 'nearest_neighbor',
            'improvement_moves': ['2-opt', '3-opt'],
            'stopping_condition': 'budget_time_or_iterations',
            'max_iterations': 1000,
            'candidate_selection': 'greedy',
            'candidate_filter': 'basic',
            'cost_function': 'tour_length',
            'acceptance_criteria': 'improve_or_equal',
            'heuristic_depth': 2,
            'local_search_strategies': ['2-opt', 'or-opt'],
            'perturbation': 'small_swaps',
            'balancing': 'cost_budget_matching',
            'robustness_focus': True,
            'interpretability': True
        }
    }

