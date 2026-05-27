def build_heuristic():
    return {
        'technique': 'failure_replay',
        'parameters': {
            'max_failures': 100,
            'replay_depth': 10,
            'confidence_threshold': 0.8
        },
        'heuristic': {
            'initial_solution': 'ssp',  # use sequential shortest path for initial solution
            'local_search': {
                'type': '2-opt',
                'max_iterations': 1000
            },
            'selection_strategy': 'greedy',
            'acceptance_criteria': 'improvement',
            'tabu_search': {
                'enabled': True,
                'tabu_tenure': 10,
                'max_iterations': 500
            }
        },
        'robustness': {
            'tested_instances': [
                'lin105', 'pr144', 'pcb1173', 'rl1304', 'eil51', 'eil76', 'bier127'
            ],
            'synthetic_transfer': True,
            'transfer_tests': 3
        },
        'interpretability': True
    }

