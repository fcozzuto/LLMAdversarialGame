def build_heuristic():
    return {
        'name': 'deterministic_heuristic_scaffold',
        'technique': 'random_replay',
        'parameters': {
            'replay_archive': [],
            'candidate_selection': 'deterministic',
            'heuristic_strategy': 'greedy_nearest_neighbor',
            'initialization': 'nearest_neighbor',
            'improvement_moves': ['2-opt', '3-opt'],
            'max_iterations': 1000,
            'stopping_condition': 'fixed_iterations',
            'evaluation_metrics': ['tour_length', 'robustness_scores'],
            'robustness_metric': 'average_tour_length',
            'performance_focus': 'generalization',
            'training_instances': 'TSPLIB_lower_bound',
            'validation_instances': 'TSPLIB_upper_bound',
            'synthetic_test_instances': True,
            'interpretable_components': True,
            'complexity_limit': 'moderate',
        }
    }

