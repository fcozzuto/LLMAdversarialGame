def build_heuristic():
    return {
        'name': 'deterministic_heuristic_scaffold',
        'technique': 'failure_replay',
        'replay_archive': [],  # No replay archive entries yet
        'candidate': 1,
        'steps': [
            {
                'type': 'initialization',
                'description': 'Start with a greedy tour using the nearest neighbor heuristic.',
            },
            {
                'type': 'local_search',
                'method': '2-opt',
                'description': 'Iteratively improve tour by reversing segments to reduce total length.',
            },
            {
                'type': 'augmentation',
                'description': 'Apply small perturbations to escape local optima, e.g., random swaps.',
            },
            {
                'type': 'validation',
                'description': 'Evaluate solution on a hold-out set to ensure robustness.',
            }
        ],
        'parameters': {
            'initialization': {
                'method': 'nearest_neighbor',
            },
            'local_search': {
                'method': '2-opt',
                'max_iterations': 1000,
            },
            'augmentation': {
                'method': 'random_swap',
                'max_attempts': 50,
            },
            'validation': {
                'performance_metrics': ['tour_length', 'robustness_score'],
                'hold_out_instances': ['tsplib', 'synthetic_transfer'],
            }
        }
    }

