def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate_id': 'candidate_1',
        'description': 'A simple, interpretable heuristic for the constrained TSP based on greedy nearest neighbor with constraint filtering.',
        'parameters': {
            'initialization': 'nearest_neighbor',
            'selection_criterion': 'minimum_increase_in_cost',
            'constraint_enforcement': 'vertex_lower_bound_and_upper_bound',
            'heuristic_type': 'greedy',
            'termination_condition': 'all_vertices_visited',
        },
        'details': {
            'approach': 'Start from the vertex with the lowest lower bound, then iteratively select the next closest vertex that satisfies all constraints.',
            'constraint_checks': 'Before selecting a candidate, ensure adding it does not violate the prescribed constraints (e.g., degree limits, time windows).',
            'robustness': 'Designed to perform consistently across TSPLIB and synthetic instances by relying on local greedy choices with straightforward constraints.',
            'interpretability': 'The heuristic uses easily understandable rules: greedy selection respecting constraints, making it transparent and adjustable.',
        }
    }

