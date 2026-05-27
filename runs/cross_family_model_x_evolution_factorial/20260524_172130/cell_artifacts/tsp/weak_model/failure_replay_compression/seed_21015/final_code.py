def build_heuristic():
    return {
        'name': 'failure_replay_compression_v1',
        'technique': 'failure_replay_compression',
        'parameters': {
            'max_replay_size': 100,
            'compression_threshold': 0.95,
            'replay_interval': 10,
            'failure_tolerance': 0.05,
            'use_node_priorities': True,
            'initial_solution_method': 'nearest_neighbor',
            'improvement_heuristic': '2-opt',
            'termination_criteria': {
                'max_iterations': 1000,
                'improvement_threshold': 1e-4
            }
        },
        'heuristic_components': [
            'initial_solution',
            'failure_detection',
            'replay_compression',
            'local_search'
        ],
        'interpretability': 'high',
        'robustness': 'moderate',
        'performance_considerations': {
            'training_instances': 'balanced with synthetic data',
            'held_out_TSPLIB': True,
            'synthetic_transfer': True
        }
    }

