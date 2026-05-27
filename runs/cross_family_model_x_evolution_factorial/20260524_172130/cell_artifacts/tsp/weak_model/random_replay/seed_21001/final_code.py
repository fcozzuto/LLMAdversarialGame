def build_heuristic():
    return {
        'technique': 'random_replay',
        'parameters': {
            'replay_probability': 0.1,
            'max_replay_size': 50,
            'initial_solution_strategy': 'nearest_neighbor',
            'perturbation_strength': 0.05,
            'num_iterations': 1000,
            'convergence_criteria': 'no_improvement_in_50_iterations',
            'use_shortcut': True,
            'shortcut_length': 2
        },
        'heuristic_type': 'constrained_tsp',
        'scaffold_description': 'A heuristic that employs random replay with a small probability to revisit previous solutions, combined with a nearest neighbor initial solution, perturbation, and shortcutting for efficiency and robustness.'
    }

