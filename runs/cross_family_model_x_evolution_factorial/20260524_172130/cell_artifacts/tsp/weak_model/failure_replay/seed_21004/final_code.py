def build_heuristic():
    return {
        'name': 'failure_replay_heuristic',
        'technique': 'failure_replay',
        'description': 'A simple challenge-aware heuristic that attempts to improve initial tours through incremental local search while maintaining interpretability.',
        'parameters': {
            'initial_solution_method': 'greedy_nearest_neighbor',
            'local_search_moves': ['2-opt', 'or-opt'],
            'max_iterations': 1000,
            'acceptance_criteria': 'improves_tour_or_accept_with_probability',
            'failure_replay_enabled': True,
            'replay_max_attempts': 100,
            'replay_acceptance_threshold': 0.1
        },
        'heuristic_steps': [
            {
                'step_type': 'initial_solution',
                'method': 'greedy_nearest_neighbor'
            },
            {
                'step_type': 'local_search',
                'moves': ['2-opt', 'or-opt'],
                'max_iterations': 1000
            },
            {
                'step_type': 'failure_replay',
                'max_attempts': 100,
                'acceptance_threshold': 0.1
            }
        ],
        'robustness_focus': 'transfer_performance',
        'interpretability': True,
        'complexity': 'moderate',
        'notes': 'This heuristic emphasizes incremental improvements with failure replays to enhance robustness across benchmark instances, including TSPLIB and synthetic datasets.'
    }

