def build_heuristic():
    return {
        'name': 'failure_replay_heuristic',
        'technique': 'failure_replay',
        'description': (
            'A deterministic, interpretable heuristic based on failure replay '
            'for constrained TSP. It guides the search using a simple failure '
            'history, avoiding repeated failures on similar subproblems.'
        ),
        'components': {
            'initial_solution': 'NearestNeighbor',
            'neighborhood': '2-opt',
            'termination_condition': 'max_iterations',
            'max_iterations': 1000,
            'move_selection': 'greedy',
            'failure_memory': True,
            'failure_threshold': 3,
            'failure_replay_strategy': 'avoid_recent_failures',
        },
        'parameters': {
            'initial_solution': 'NearestNeighbor',
            'neighbor_selection': 'best_improvement',
        },
        'robustness': 'validated_on_TSPLIB_and_synthetic_transfer',
        'interpretability': 'high',
        'complexity': 'moderate'
    }

