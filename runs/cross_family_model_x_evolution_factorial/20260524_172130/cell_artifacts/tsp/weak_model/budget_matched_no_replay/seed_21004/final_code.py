def build_heuristic():
    return {
        'technique': 'budget_matched_no_replay',
        'candidate': 1,
        'parameters': {
            'heuristic_type': 'nearest_neighbor',
            'initial_route': 'greedy',
            'improvement': '2-opt',
            'max_runtime': 300,  # seconds
            'budget_constraint': True,
            'transfer_performance_weight': 1.0,
            'robustness_weight': 1.0,
            'instance_selection': 'TSPLIB_and_synthetic',
            'evaluation_metric': 'total_distance',
            'stopping_criteria': 'no_improvement_after_100_iterations',
            'interpretability': True
        }
    }

