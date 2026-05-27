def build_heuristic():
    return {
        'name': 'failure_replay_candidate_1',
        'technique': 'failure_replay',
        'description': 'A deterministic, interpretable heuristic based on minimal insertion and modification.',
        'parameters': {
            'initial_solution_method': 'nearest_neighbor',  # Greedy seed for initial circuit
            'improvement_strategy': '2opt',  # Simple local search improvement
            'max_iterations': 1000,  # Limits for robustness
            'selection_rule': 'first_improvement',  # Deterministic choice
            'failure_handling': 'retry_with_different_seed',  # Repetition rule
            'seed_selection': 'fixed',  # For deterministic behavior
        },
        'heuristic_steps': [
            'Generate initial tour using nearest neighbor heuristic with fixed seed.',
            'Apply 2-opt local search repeatedly until no improvement or max iterations reached.',
            'If no solution found or early termination, retry with different fixed seed.',
            'Select the best solution found over retries.',
        ],
        'robustness': 'designed for transferable performance on TSPLIB and synthetic instances, balancing simplicity and effectiveness.',
        'interpretability': 'Uses well-understood heuristics like nearest neighbor and 2-opt, with clear control parameters.'
    }

