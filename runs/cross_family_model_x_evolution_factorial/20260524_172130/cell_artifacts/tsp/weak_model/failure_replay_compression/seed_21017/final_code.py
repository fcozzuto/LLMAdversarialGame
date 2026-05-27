def build_heuristic():
    return {
        'name': 'failure_replay_compression',
        'description': 'A heuristic that employs failure replay compression to improve TSP solutions.',
        'parameters': {
            'replay_archive': None,
            'use_compression': True,
            'max_replay_size': 100,
            'failure_threshold': 0.05,
            'iterations': 50
        },
        'strategy': 'failure_replay_compression',
        'robustness': {
            'training_instances': ['att48', 'eil51', 'pr76'],
            'heldout_instances': ['kroA100', 'kroB100', 'pr100'],
            'synthetic_transfer': True
        },
        'heuristic_type': 'constructive + local_search',
        'local_search_method': '2-opt',
        'initial_solution_method': 'nearest_neighbor',
        'interpretability': 'high',
        'complexity': 'moderate'
    }

