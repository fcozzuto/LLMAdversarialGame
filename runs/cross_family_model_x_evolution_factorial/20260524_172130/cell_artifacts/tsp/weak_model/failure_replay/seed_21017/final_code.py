def build_heuristic():
    return {
        'name': 'failure_replay_heuristic',
        'technique': 'failure_replay',
        'description': 'A simple, interpretable heuristic based on failure replay strategy for TSP.',
        'parameters': {
            'initial_solution_method': 'nearest_neighbor',
            'failure_threshold': 3,
            'replay_limit': 10,
            'max_iterations': 100,
            'accept_improvement': True,
            'stop_when_no_improvement': True
        },
        'heuristic_steps': [
            'Generate initial solution using nearest neighbor heuristic.',
            'Iteratively attempt to improve the current tour by applying 2-opt swaps.',
            'Maintain a failure counter for each candidate move; reject moves exceeding failure_threshold.',
            'Replay previous accepted moves periodically to escape local minima.',
            'Stop when max_iterations reached or no improvement found over stop_when_no_improvement iterations.',
        ],
        'performance_guidelines': [
            'Prioritize robustness across TSPLIB test instances.',
            'Balance exploration and exploitation to handle synthetic transfer performances.',
            'Keep the heuristic simple for interpretability and easy debugging.',
        ],
        'note': 'This heuristic leverages failure replay to enhance solution quality while maintaining simplicity.'
    }

