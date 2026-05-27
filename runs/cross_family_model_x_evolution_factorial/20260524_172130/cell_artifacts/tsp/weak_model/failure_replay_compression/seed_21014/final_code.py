def build_heuristic():
    return {
        'name': 'failure_replay_compression',
        'parameters': {
            'max_iterations': 1000,
            'convergence_threshold': 1e-5,
            'failure_replay_enabled': True,
            'replay_archive_size': 10,
            'initial_solution_method': 'nearest_neighbor',
            'local_search_method': '2_opt',
            'replay_selection_strategy': 'best_improvement',
            'failure_threshold': 5,
            'compression_ratio': 0.5,
            'robustness_score': {
                'TSPLIB_easy': 0.9,
                'TSPLIB_hard': 0.85,
                'synthetic_transfer': 0.88
            }
        }
    }

