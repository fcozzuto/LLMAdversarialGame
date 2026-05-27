def build_heuristic():
    return {
        'name': 'single_shot_candidate_1',
        'method': 'nearest_neighbor',
        'initialization': 'greedy',
        'improvement': '2-opt',
        'iterations': 100,
        'admissible_constraints': True,
        'robustness': 'balanced',
        'performance_tradeoff': {
            'training_performance': 'moderate',
            'test_performance': 'robust'
        },
        'heuristic_explained': 'Starts with a greedy initialization using nearest neighbor approach, then applies 2-opt for local improvement. Designed for interpretability and robustness across benchmark sets including TSPLIB and synthetic instances.',
        'parameters': {
            'initialization_strategy': 'greedy',
            'local_search_method': '2-opt',
            'max_iterations': 100
        }
    }

