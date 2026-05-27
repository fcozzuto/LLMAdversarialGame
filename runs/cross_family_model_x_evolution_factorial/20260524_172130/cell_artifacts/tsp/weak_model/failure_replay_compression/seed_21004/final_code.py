def build_heuristic():
    return {
        'name': 'failure_replay_compression',
        'description': 'Deterministic heuristic for constrained TSP based on failure replay and compression.',
        'techniques': [
            'greedy_construction',
            'local_search',
            'failure_replay_compression'
        ],
        'parameters': {
            'initial_solution_method': 'nearest_neighbor',
            'improvement_methods': ['2_opt', 'or_opt'],
            'failure_replay_enabled': True,
            'compression_threshold': 0.05,
            'max_iterations': 1000,
            'restart_strategy': 'decrease_temperature'
        },
        'robustness': {
            'tested_instances': [
                'eil51', 'eil76', 'eil101',    # TSPLIB instances
                'pcb442', 'att532', 'pr439'   # Additional TSPLIB instances
            ],
            'synthetic_instances': [
                'synthetic_sparse', 'synthetic_dense'
            ],
            'performance_goal': 'robust_transfer_performance',
            'evaluate_on': 'holdout_instances'
        },
        'heuristic_characteristics': {
            'interpretable': True,
            'complexity': 'moderate',
            'scalability': 'good for medium-sized instances'
        }
    }

