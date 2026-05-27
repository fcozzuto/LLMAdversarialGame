def build_heuristic():
    return {
        'technique': 'failure_replay_compression',
        'replay_archive_entries': [],  # No entries yet
        'heuristic_parameters': {
            'max_failure_replays': 3,
            'compression_threshold': 0.05,
            'iteration_limit': 50,
            'early_stopping': True,
            'use_dynamic_threshold': True,
            'performance_metric': 'tour_length_difference',
            'acceptable_difference': 0.01
        },
        'validation_strategy': {
            'test_benchmarks': [
                'att48', 'eil51', 'berlin52', 'pr76', 'eil101', 'pcb1173', 'pcb3048', 'rl1323'
            ],
            'synthetic_instances': [
                'synthetic_simple', 'synthetic_random', 'synthetic_clustered'
            ],
            'performance_goal': 'robustness_across_benchmarks',
            'evaluation_metric': 'average_tour_length_ratio'
        },
        'interpretability': True,
        'complexity_limit': 'moderate',
        'note': 'Deterministic heuristic focusing on failure replay with compression, tested on TSPLIB and synthetic instances.'
    }

