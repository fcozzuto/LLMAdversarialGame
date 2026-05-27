def build_heuristic():
    return {
        'name': 'budget_matched_no_replay',
        'description': 'A simple, deterministic TSP heuristic based on nearest neighbor with cost budget constraints.',
        'parameters': {
            'initial_selection_strategy': 'nearest_neighbor',
            'budget_constraint_type': 'cost_matching',
            'allow_revisits': False,
            'heuristic_steps': 'greedy',
            'stop_condition': 'all_nodes_visited',
        },
        'rules': [
            'Start from a predefined node (e.g., node 0).',
            'Iteratively select the nearest unvisited node that keeps the total tour length within a predefined budget.',
            'Do not revisit nodes.',
            'If no further nodes can be added without exceeding the budget, terminate.',
            'Return the constructed tour as the solution.',
        ],
        'robustness': 'Designed to perform well on both synthetic and TSPLIB instances by maintaining a cost-based selection and avoiding overcomplexity.',
    }

