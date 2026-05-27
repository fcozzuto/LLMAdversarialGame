def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'description': 'A deterministic heuristic based on budget-matching and simple greedy selection without replay or failure memory.',
        'parameters': {
            'initial_tour_construction': 'nearest_neighbor',
            'improvement': '2_opt',
            'termination_condition': 'budget_limit',
            'budget_ratio': 1.0,
        },
        'details': {
            'initial_tour_method': 'nearest_neighbor',
            'improvement_method': '2_opt',
            'termination_criteria': 'reach_budget',
            'heuristic_interpretability': 'high',
            'robustness': 'designed to generalize across TSPLIB and synthetic instances',
            'complexity': 'moderate, straightforward greedy-based with local optimization',
        }
    }

