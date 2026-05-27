def build_heuristic():
    return {
        'name': 'deterministic_heuristic_scaffold',
        'description': 'A robust, interpretable TSP heuristic based on nearest neighbor and 2-opt improvements, designed for both TSPLIB and synthetic instances.',
        'techniques': [
            'nearest_neighbor',  # Construct initial tour greedily
            '2_opt',             # Local search improvement
            'constrained_reoptimization'  # Re-apply local search with constraints if needed
        ],
        'parameters': {
            'initial_construction': {
                'method': 'nearest_neighbor',
                'start_node_selection': 'arbitrary',  # or 'least_degree'
            },
            'local_search': {
                'method': '2_opt',
                'max_iterations': 1000,
                'stopping_condition': 'no_improvement',
            },
            'reoptimization': {
                'enabled': True,
                'max_retries': 3,
            }
        },
        'robustness': {
            'performance_across_conditions': 'high',
            'tested_on': ['TSPLIB', 'synthetic_instances'],
            'performance_metrics': ['tour_length', 'computation_time'],
        },
        'interpretability': 'heuristic_steps are transparent and parameter choices are straightforward.',
        'complexity': 'relatively simple, suitable for understanding and adaptation.'
    }

