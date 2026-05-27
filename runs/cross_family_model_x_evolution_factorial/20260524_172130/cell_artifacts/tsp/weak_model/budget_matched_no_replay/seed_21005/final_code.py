def build_heuristic():
    return {
        'name': 'budget_matched_no_replay',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initial_solution': 'greedy_nearest_neighbor',
            'local_search': '2opt',
            'budget_ratio': 1.0,
            'max_iterations': 1000,
            'acceptance_criterion': 'improvement_only',
            'restart_strategy': 'none'
        },
        'heuristic': {
            'description': 'Construct initial solution with a greedy nearest neighbor heuristic, then improve via 2-opt local search, respecting the original budget. No replay or memory mechanisms are used to ensure simplicity and interpretability.',
            'robustness': 'designed for good generalization across TSPLIB instances and synthetic datasets without overfitting.',
            'complexity': 'moderate, allowing ease of understanding and implementation.'
        }
    }

