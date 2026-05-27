def build_heuristic():
    return {
        'name': 'deterministic_basic_heuristic',
        'technique': 'random_replay',
        'parameters': {
            'initial_heuristic': 'nearest_neighbor',
            'selection_strategy': 'greedy',
            'replay_policy': 'deterministic',
            'max_iterations': 200,
            'improvement_method': '2_opt',
            'stop_condition': 'no_improvement_after_50',
            'fallback_strategy': 'nearest_insertion',
            'robustness_weighting': {
                'training_instances': 0.7,
                'test_instances': 0.3
            }
        },
        'notes': 'A simple, interpretable heuristic emphasizing robustness across TSPLIB and synthetic instances.'
    }

