def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'heuristic_type': 'nearest_neighbor',
        'initialization': 'nearest_node',
        'node_selection_strategy': 'closest_unvisited',
        'edge_selection_strategy': 'shortest_edge_with_budget_constraint',
        'budget': 1.0,  # default budget parameter; can be tuned
        'fit_heuristic_to_instances': [
            'eil51', 'berlin52', 'pr76', 'eil76', 'kroA100', 'kroB100', 'ch150', 'att48', 'lin318'
        ],
        'robustness_targets': ['eil51', 'berlin52', 'pr76', 'kroA100', 'att48'],
        'robustness_priority': ['held-out TSPLIB', 'synthetic_transfer'],
        'parameters': {
            'initial_node_strategy': 'nearest_node',
            'neighbor_distance_metric': 'euclidean',
            'max_iterations': 1000,
            'early_stop_threshold': 10
        }
    }

