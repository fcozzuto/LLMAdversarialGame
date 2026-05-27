def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initialization_method': 'nearest_neighbor',
            'local_search': {
                'enabled': True,
                'iterations': 100,
                'swap_strategy': '2-opt'
            },
            'budget_ratio': 1.0,
            'selection_criteria': 'shortest_edge_first',
            'termination_condition': {
                'max_iterations': 500,
                'no_improvement_limit': 50
            }
        },
        'robustness': {
            'tested_on': ['TSPLIB', 'synthetic_transfer'],
            'performance_focus': 'transfer_robustness',
            'interpretability': True,
            'complexity': 'moderate'
        }
    }

