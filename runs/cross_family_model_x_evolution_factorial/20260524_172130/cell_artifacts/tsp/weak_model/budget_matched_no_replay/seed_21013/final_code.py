def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'heuristic_components': [
            {
                'type': 'nearest_neighbor',
                'params': {
                    'start_node': 'random',
                    'distance_metric': 'euclidean'
                }
            },
            {
                'type': '2_opt',
                'params': {
                    'iterations': 100,
                    'improvement_threshold': 1e-4
                }
            }
        ],
        'budget_matching': 'strict',  # Ensures tour length matches heuristic estimate
        'robustness_considerations': [
            'tested_on_TSPLIB_and_synthetic_transfer',
            'avoids_overfitting_to_training_instances',
            'interpretable_components',
            'simple_control_parameters'
        ],
        'notes': 'Heuristic constructs initial tour with nearest neighbor, then refines with 2-opt, ensuring total length matches heuristic budget.'
    }

