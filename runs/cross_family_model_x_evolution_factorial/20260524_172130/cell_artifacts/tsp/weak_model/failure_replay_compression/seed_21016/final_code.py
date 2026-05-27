def build_heuristic():
    return {
        'technique': 'failure_replay_compression',
        'parameters': {
            'replay_archive_entries': 0,
            'compression_threshold': 0.1,
            'max_replay_attempts': 5,
            'use_incremental_learning': True,
            'validation_set': ['a280', 'berlin52', 'att48', 'eil51', 'kroA100', 'bayg128', 'dantzig42'],
            'training_set': ['tsp_instance_001', 'tsp_instance_002', 'tsp_instance_003']
        },
        'heuristic_rules': [
            'nearest_neighbor + 2-opt',
            'greedy_insertion + 2-opt',
            'combo heuristics with early stopping',
            'stochastic local search with controlled randomness'
        ],
        'robustness': {
            'holdout_performance': 'optimized for TSPLIB and synthetic benchmarks',
            'performance_metrics': ['avg_tour_length', 'std_dev', 'best_case', 'worst_case'],
            'training_instances': 'not overfitting, emphasis on transfer robustness'
        },
        'interpretability': 'heuristics are composed of simple, well-understood procedures',
        'complexity_control': 'limit heuristic depth and iteration counts'
    }

