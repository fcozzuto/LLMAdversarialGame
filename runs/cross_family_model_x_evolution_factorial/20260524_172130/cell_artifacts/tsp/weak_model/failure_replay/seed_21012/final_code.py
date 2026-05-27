def build_heuristic():
    return {
        'name': 'heuristic_failure_replay',
        'technique': 'failure_replay',
        'description': 'A simple deterministic heuristic using failure replay technique.',
        'parameters': {
            'max_iterations': 1000,
            'neighborhood_size': 5,
            'acceptance_criteria': 'improvement_or_equal',
            'initial_route': 'nearest_neighbor',
            'retry_limit': 3
        },
        'validation': {
            'robustness_on_TSPLIB': True,
            'transfer_performance': 'moderate',
            'explainability': 'high'
        }
    }

