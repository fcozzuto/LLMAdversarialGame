def build_heuristic():
    return {
        'name': 'single_shot_candidate_1',
        'technique': 'single_shot',
        'candidate': 1,
        'description': 'Deterministic heuristic based on nearest neighbor chaining with threshold filtering for robustness on TSPLIB and synthetic instances.',
        'parameters': {
            'initialization_method': 'nearest_neighbor',
            'neighbor_selection': 'closest_unvisited',
            'distance_threshold': 1e-5,
            'selection_strategy': 'greedy',
            'termination_condition': 'all_nodes_visited'
        },
        'heuristic_steps': [
            'Start from a fixed node (e.g., node 0).',
            'Iteratively select the nearest unvisited neighbor within the distance threshold.',
            'Append selected node to the route.',
            'Repeat until all nodes are visited.',
            'Return to the start node to complete the cycle.'
        ],
        'robustness_features': [
            'Distance threshold to avoid local minima due to small edge variations.',
            'Greedy selection ensures simplicity and interpretability.',
            'Fixed start node for deterministic output.'
        ],
        'expected_performance': 'Robust transfer performance on held-out TSPLIB and synthetic problems, with consistent route quality.',
        'notes': 'This heuristic emphasizes interpretability and robustness over aggressive optimization.'
    }

