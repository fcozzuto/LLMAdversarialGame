def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'heuristic_name': 'deterministic_simple_nearest_neighbor',
        'parameters': {
            'approach': 'nearest_neighbor',
            'start_node': 'first_node',
            'distance_metric': 'euclidean',
            'tie_breaking': 'lowest_node',
            'evaluation': 'robust_transfer',
            'performance_metric': 'total_distance',
            'robustness_over_fit': True,
            'interpretability': True,
            'complexity': 'low',
        }
    }

