def build_heuristic():
    return {
        'name': 'deterministic_simple_heuristic',
        'description': 'A robust, simple heuristic based on nearest neighbor with held-out validation.',
        'techniques': [
            {
                'name': 'nearest_neighbor',
                'parameters': {
                    'start_node': 'first',
                    'max_neighbors': 10
                }
            },
            {
                'name': 'skip_visited',
                'parameters': {}
            },
            {
                'name': 'local_optimization',
                'parameters': {
                    'method': '2-opt',
                    'iterations': 100
                }
            }
        ],
        'training_instances': [
            'att48', 'berlin52', 'bier127', 'st70', 'a280'
        ],
        'validation_instances': [
            'eil101', 'pr144', 'rat575', 'dsj1000'
        ],
        'heuristic_rules': [
            'Start at first node.',
            'Iteratively select the nearest unvisited neighbor within max_neighbors.',
            'Skip over already visited nodes.',
            'After initial tour, apply local 2-opt optimization for improvement.',
            'Ensure tour validity and enforce constraints during neighbor selection.'
        ],
        'robustness_measures': 'Technique selection and parameter tuning based on validation performance on held-out TSPLIB instances to maximize transferability.'
    }

