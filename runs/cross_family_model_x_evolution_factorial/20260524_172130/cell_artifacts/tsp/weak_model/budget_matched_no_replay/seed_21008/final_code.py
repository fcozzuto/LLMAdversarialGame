def build_heuristic():
    return {
        'technique': 'budget_matched_no_replay',
        'candidate': 1,
        'description': 'A deterministic, interpretable heuristic for constrained TSP, optimized for transferred performance on TSPLIB and synthetic instances, without using replay memory or failure memory.',
        'components': {
            'initial_tour': 'nearest_neighbor',
            'improvement': '2-opt',
            'constraint_handling': 'greedy_feasible_insertion',
            'termination': 'max_iterations',
            'max_iterations': 1000,
            'stopping_condition': 'no_improvement_after_50_iter',
            'node_selection': 'sequential',
            'edge_selection': 'lower_cost_edges'
        },
        'parameters': {
            'initial_tour': {
                'method': 'nearest_neighbor',
                'start_node': 'deterministic_node_order'
            },
            'improvement': {
                'method': '2-opt',
                'allow_worse_moves': False
            },
            'constraint_handling': {
                'method': 'greedy_feasible_insertion',
                'priority': 'minimal_constraint_violation'
            },
            'termination': {
                'max_iterations': 1000,
                'stopping_condition': 'no_improvement_after_50_iter'
            }
        }
    }

