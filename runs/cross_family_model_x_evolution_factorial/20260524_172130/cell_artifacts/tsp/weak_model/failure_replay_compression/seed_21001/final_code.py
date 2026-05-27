def build_heuristic():
    return {
        'name': 'failure_replay_compression',
        'parameters': {
            'replay_archive': [],  # No entries yet
            'max_replays': 10,
            'compression_threshold': 0.95,
            'failure_tolerance': 5,
            'use_synthetic_transfer': True,
            'synthetic_transfer_num': 3,
            'training_instances': [
                'a280', 'ali535', 'att532', 'berlin52', 'bier130', 'd198', 'eil51', 'lin105', 'pr124', 'pcb1173'
            ],
            'validation_instances': [
                'kroA100', 'kroB100', 'eil76', 'pr76', 'rat99', 'dsj1000'
            ],
            'heuristic_rules': {
                'initial_solution_strategy': 'greedy',
                'local_search': ['2-opt', '3-opt'],
                'replay_trigger_threshold': 10,
                'compression_method': 'failure_replay',
                'failure_tolerance': 3
            }
        }
    }

