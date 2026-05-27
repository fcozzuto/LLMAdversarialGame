def build_heuristic():
    return {
        'name': 'single_shot_candidate1',
        'technique': 'single_shot',
        'candidate': 1,
        'description': 'Deterministic heuristic using a simple nearest neighbor approach with predefined parameters for robustness and interpretability.',
        'parameters': {
            'initial_node': 0,
            'use_closest_unvisited': True,
            'max_iterations': None,
            'early_stop_threshold': None,
            'improve_with_2opt': False
        },
        'heuristic_steps': [
            'Start from the initial_node (node 0).',
            'At each step, move to the nearest unvisited node.',
            'Repeat until all nodes are visited.',
            'Return to the starting node to complete the tour.',
        ],
        'notes': 'This heuristic is deterministic, interpretable, and designed for robustness across classical TSP benchmarks, balancing simplicity and effectiveness.'
    }

