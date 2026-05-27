def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'heuristic_type': 'nearest_neighbor',
        'initialization': 'start_from_closest_node',
        'neighbor_choice': 'greedy',
        'improvement': 'none',
        'restart_strategy': None,
        'parameters': {
            'max_iterations': 1000,
            'random_seed': 42
        },
        'performance_priority': ['robustness', 'transferability', 'interpretability']
    }

