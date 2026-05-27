def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'parameters': {
            'initial_solution': 'nearest_neighbor',  # Use a simple, interpretable heuristic for initial solution.
            'refinement': '2_opt',                   # Apply a classical local search for improvement.
            'budget_ratio': 0.05,                    # Allocate 5% of total tour length as computational budget.
            'termination_condition': 'fixed_time',   # Stop after running for a fixed amount of time.
            'time_limit': 60,                        # Time limit in seconds for the heuristic.
            'candidate_selection': 'nearest_unvisited',  # Select next candidate as the nearest unvisited node.
            'neighbor_search': 'greedy',             # Use a greedy approach during local optimization.
            'preprocessing': 'none',                # No preprocessing steps, keeping interpretability.
        }
    }

