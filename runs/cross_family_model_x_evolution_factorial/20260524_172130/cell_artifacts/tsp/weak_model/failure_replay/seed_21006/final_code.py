def build_heuristic():
    return {
        'name': 'failure_replay_candidate_1',
        'technique': 'failure_replay',
        'description': 'Deterministic TSP heuristic using failure replay technique, focused on simplicity and interpretability.',
        'parameters': {
            'max_attempts': 1000,
            'failure_threshold': 10,
            'replay_strategy': 'basic',
            'use_node_clustering': False,
            'connectivity_constraint': 2,
            'computed_routes': None
        },
        'robustness_focus': 'balanced',
        'performance_targets': {
            'TSPLIB': {
                'brazil62': {'cost': None, 'status': 'untested'},
                'dantzig42': {'cost': None, 'status': 'untested'},
                'pr76': {'cost': None, 'status': 'untested'},
            },
            'synthetic': {
                'random_50_node': {'cost': None, 'status': 'untested'},
                'grid_20x20': {'cost': None, 'status': 'untested'},
            }
        },
        'interpretability': True,
        'complexity': 'moderate',
        'notes': 'A straightforward heuristic employing failure replay without sophisticated re-optimization, prioritizing robustness across diverse instances.',
    }

