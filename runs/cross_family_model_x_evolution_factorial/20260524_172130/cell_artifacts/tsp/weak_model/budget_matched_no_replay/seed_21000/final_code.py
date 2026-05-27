def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'description': 'A deterministic heuristic focusing on a simple, interpretable approach for constrained TSP, ensuring robust performance on TSPLIB and synthetic instances.',
        'parameters': {
            'initial_route_construction': 'nearest_neighbor',
            'improvement': '2opt',
            'budget': 0.8,  # Relative percentage of total tour length
            'max_iterations': 1000,
            'convergence_threshold': 1e-4,
            'use_local_search': True,
            'local_search_type': '3opt',
            'candidate_selection': 'closest_unvisited',
            'restart_strategy': 'none'
        }
    }

