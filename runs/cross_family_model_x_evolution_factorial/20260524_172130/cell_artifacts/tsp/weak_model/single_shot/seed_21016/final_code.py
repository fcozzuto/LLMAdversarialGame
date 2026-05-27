def build_heuristic():
    return {
        'technique': 'single_shot',
        'candidate': 1,
        'scaffold': {
            'name': 'Deterministic_Simple_TSP_Heuristic',
            'description': 'A deterministic, interpretable heuristic based on Nearest Neighbor approach.',
            'steps': [
                {
                    'name': 'Initialization',
                    'parameters': {
                        'start_node': 'deterministic',
                        'start_node_value': 0
                    }
                },
                {
                    'name': 'Nearest Neighbor',
                    'parameters': {
                        'method': 'greedy',
                        'selection_criteria': 'shortest_distance'
                    }
                },
                {
                    'name': 'Construct Tour',
                    'parameters': {
                        'connectivity': 'full',
                        'distance_metric': 'euclidean'
                    }
                },
                {
                    'name': 'Termination',
                    'criteria': 'visit_all_nodes'
                }
            ],
            'heuristic_parameters': {
                'start_node': 0,
                'selection_method': 'greedy',
                'distance_metric': 'euclidean'
            },
            'robustness': 'designed for TSPLIB and synthetic instances, prioritized for transfer robustness'
        }
    }

