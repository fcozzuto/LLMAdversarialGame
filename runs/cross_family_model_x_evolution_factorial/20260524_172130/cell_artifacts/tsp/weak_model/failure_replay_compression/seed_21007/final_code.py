def build_heuristic():
    return {
        'name': 'failure_replay_compression',
        'parameters': {
            'replay_buffer_size': 50,
            'compression_ratio': 0.2,
            'failure_threshold': 0.15,
            'batch_size': 10,
            'max_iterations': 1000,
            'stopping_condition': 'convergence',
            'convergence_tolerance': 0.01,
            'use_heuristic_initialization': True,
            'initial_solution_method': 'nearest_neighbor',
            'neighbor_criteria': 'closest_unvisited',
            'local_search': '2_opt',
            'local_search_iterations': 50,
            'acceptance_strategy': 'improvement_only',
            'random_seed': 42
        }
    }

