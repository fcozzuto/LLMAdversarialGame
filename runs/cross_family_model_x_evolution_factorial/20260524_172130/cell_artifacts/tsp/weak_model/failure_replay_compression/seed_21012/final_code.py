def build_heuristic():
    return {
        'technique': 'failure_replay_compression',
        'replay_archive': [],
        'heuristic_params': {
            'selection_strategy': 'nearest_neighbor',
            'distance_metric': 'euclidean',
            'initialization': 'random_start',
            'reroute_strategy': 'greedy',
            'compression_threshold': 0.95,
            'max_replays': 10,
            'timeout': 60,
            'seed': 42
        },
        'performance_focus': {
            'robustness': 'balanced',
            'training_instances': 'TSPLIB_and_synthetic_transfer',
            'evaluation': 'holdout_instances',
            'optimized_for': ['transfer_efficiency', 'instance_diversity']
        }
    }

