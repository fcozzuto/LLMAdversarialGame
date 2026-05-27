def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'strategy': 'nearest_neighbor',
        'improvement': '2-opt',
        'initial_solution': 'greedy',
        'termination_condition': 'max_iterations',
        'max_iterations': 1000,
        'distance_metric': 'euclidean',
        'constraints': None,  # No additional constraints
        'robustness': 'balanced',
        'interpretability': 'high',
        'performance_focus': 'generalization'
    }

