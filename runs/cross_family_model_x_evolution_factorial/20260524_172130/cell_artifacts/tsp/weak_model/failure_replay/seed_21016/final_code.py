def build_heuristic():
    return {
        'name': 'deterministic_tsp_heuristic',
        'strategy': 'failure_replay',
        'parameters': {
            'initial_solution_method': 'nearest_neighbor',
            'local_search': {
                'method': '2opt',
                'max_iterations': 100,
                'acceptance': 'improves_only'
            },
            'failure_replay': {
                'enabled': True,
                'max_attempts': 10,
                'retries_per_attempt': 3,
                'replay_archive': False  # No archive entries yet
            },
            'evaluation': {
                'validation_instances': [
                    'eil51', 'kroA100', 'pr107', 'pcb442', 'd198'
                ],
                'metrics': ['tour_length', 'robustness']
            },
            'termination': {
                'max_time_seconds': 300,
                'max_iterations': 1000,
                'convergence_threshold': 1e-4
            }
        }
    }

