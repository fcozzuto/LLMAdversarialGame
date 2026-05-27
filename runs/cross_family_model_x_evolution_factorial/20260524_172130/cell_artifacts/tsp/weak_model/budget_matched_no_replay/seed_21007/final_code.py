def build_heuristic():
    return {
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'neighborhood_size': 20,
            'max_iterations': 1000,
            'early_stop_threshold': 50,
            'initial_solution': 'nearest_neighbor',
            'enhancement_method': '2-opt',
            'evaluation_metric': 'tour_length',
            'use_robust_seed': True,
            'seed_value': 42,
            'convergence_criterion': 1e-4
        },
        'heuristic_type': 'constructive_and_improvement',
        'robustness_settings': {
            'test_on_various_TSPLIB_instances': True,
            'synthetic_transfer_performance': True,
            'instance_size_limits': [50, 1000],
            'performance_thresholds': {
                'average_optimality_gap': 1.5,
                'max_tour_length_ratio': 1.1
            }
        }
    }

