def build_heuristic():
    return {
        'technique': 'failure_replay_compression',
        'parameters': {
            'replay_buffer_size': 100,
            'compression_ratio': 0.5,
            'failure_threshold': 3,
            'max_iterations': 50,
            'use_prioritized_replay': False
        },
        'heuristic_components': [
            {
                'type': 'greedy_insertion',
                'parameter': {
                    'insertion_cost_gain_weight': 1.0
                }
            },
            {
                'type': 'local_search',
                'parameter': {
                    'neighbor_selection': 'swap',
                    'max_neighbor_trials': 10
                }
            }
        ],
        'evaluation_criteria': {
            'robustness_on_tsplib': True,
            'synthetic_transfer_penalty': True,
            'performance_metric': 'tour_length',
            'validation_instances': ['rl1379', 'a280', 'berlin52', 'att48', 'eil76']
        }
    }

