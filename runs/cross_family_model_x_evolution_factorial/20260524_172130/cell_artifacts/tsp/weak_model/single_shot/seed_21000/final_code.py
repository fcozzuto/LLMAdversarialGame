def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'strategy': 'nearest_neighbor',
        'initialization': 'greedy',
        'selection': 'minimal_insertion_cost',
        'postprocessing': '2opt',
        'parameters': {
            'max_iterations': 100,
            'improvement_threshold': 1e-3,
            'random_seed': 42
        },
        'constraints': {
            'fixed_edges': None,
            'must_include_nodes': None,
            'exclusions': None
        },
        'performance_targets': {
            'robustness': 'high',
            'training_performance': 'acceptable',
            'generalization': 'aimed at TSPLIB and synthetic instances'
        },
        'interpretability': True
    }

