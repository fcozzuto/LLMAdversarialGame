def build_heuristic():
    return {
        'name': 'deterministic_transfer_heuristic',
        'technique': 'random_replay',
        'parameters': {
            'initial_seed': 42,
            'replay_buffer_size': 1000,
            'replay_strategy': 'fifo',
            'sampling_probability': 0.3,
            'update_strategy': 'every_episode',
            'use_transfer': True,
            'transfer_data': {
                'source_instances': ['rl1323', 'pr1002', 'ftv170', 'pcb1173'],
                'target_instances': ['tsp225', 'berlin52', 'eil51', 'a280'],
                'transfer_method': 'heuristic_guided_initialization',
                'heuristic_rules': {
                    'nearest_neighbor': True,
                    '2_opt_local_search': True
                }
            },
            'heuristic_evaluation': {
                'test_on': ['berlin52', 'st70', 'rd100', 'pcb1173'],
                'performance_metric': 'total_tour_length',
                'robustness_criteria': 'consistent_performance_across_domains'
            }
        }
    }

