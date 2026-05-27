def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initial_solution_method': 'nearest_neighbor',
            'improvement_method': '2opt',
            'termination_condition': 'budget_based',
            'budget_fraction': 0.1,  # 10% of total nodes as iteration limit
            'selection_strategy': 'greedy',
            'cost_estimate': 'greedy_sum',
        },
        'robustness_features': {
            'use_tsp_lib_instances': True,
            'use_synthetic_transfer': True,
            'performance_bias': 'favor_transfer_performance',
        },
        'interpretability': True,
        'complexity_limit': 'moderate',
    }

