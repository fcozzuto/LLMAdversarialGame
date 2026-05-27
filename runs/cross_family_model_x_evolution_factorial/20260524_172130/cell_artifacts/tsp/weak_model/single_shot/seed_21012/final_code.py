def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'parameters': {
            'initialization': 'nearest_neighbor',
            'improvement': '2_opt',
            'stopping_criterion': 'max_iterations',
            'max_iterations': 1000,
            'local_search': True,
            'seed': 42
        }
    }

