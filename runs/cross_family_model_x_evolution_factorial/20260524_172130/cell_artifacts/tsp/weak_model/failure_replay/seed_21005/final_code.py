def build_heuristic():
    return {
        'name': 'failure_replay_heuristic',
        'technique': 'failure_replay',
        'parameters': {
            'max_replays': 10,
            'failure_threshold': 0.05,
            'initial_solution_strategy': 'nearest_neighbor',
            'improvement_methods': ['2_opt', 'or_opt'],
            'validate_solution': True,
            'cutting_planes': False,
            'time_limit_seconds': 60,
            'use_tabu_search': True,
            'tabu_tenure': 15,
            'robustness': {
                'test_on_tsplib': True,
                'test_on_synthetic_transfers': True,
                'training_instances': {
                    'tsplib': ['eil51', 'lin318', 'pcb1173'],
                    'synthetic_series': ['synthetic_series_1', 'synthetic_series_2']
                }
            },
            'interpretability': True
        }
    }

