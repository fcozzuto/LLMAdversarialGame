def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'techniques': ['heuristic', 'budget_matched_no_replay'],
        'description': 'A deterministic TSP heuristic based on matching the total tour length to a predefined budget,'
                       ' without replay memory or failure memory, aiming for robustness across held-out TSPLIB and synthetic instances.',
        'parameters': {
            'matching_threshold': 0.05,
            'use_greedy_construction': True,
            'local_improvement': '2-opt',
            'max_iterations': 1000,
            'termination_condition': 'no_improvement',
        },
        'heuristic_details': {
            'construction_method': 'greedy_nearest_neighbor',
            'matching_strategy': 'adjusts tour length to match predefined budget within tolerance',
            'budget': 'set per-instance based on training data or default',
            'local_search': 'apply 2-opt until no improvement or max iterations',
        }
    }

