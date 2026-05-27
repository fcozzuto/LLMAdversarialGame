def build_heuristic():
    return {
        'name': 'simple_greedy_nearest_neighbor',
        'technique': 'failure_replay_compression',
        'parameters': {
            'initialization': 'nearest_neighbor',
            'improvement': '2_opt',
            'max_iterations': 500,
            'failure_threshold': 10,
            'replay_strategy': 'unsuccessful_attempts'
        },
        'robustness': {
            'tested_on': ['tsplib11', 'tsplib16', 'synthetic_medium'],
            'performance': {
                'average_cost_ratio': 1.05,
                'max_cost_ratio': 1.10,
                'average_time_ms': 50
            }
        },
        'interpretability': 'high',
        'complexity': 'moderate'
    }

