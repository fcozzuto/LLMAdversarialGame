def build_heuristic():
    return {
        'name': 'deterministic_tsp_heuristic',
        'techniques': ['nearest_neighbor', '2_opt', 'exchange'],
        'initialization': 'nearest_neighbor',
        'local_search': '2_opt',
        'improvement': 'exchange',
        'criteria': {
            'max_iterations': 1000,
            'max_no_improve': 100,
            'time_limit_seconds': 300
        },
        'experience': {
            'training_instances': ['eil51', 'kroA100', 'pr2392'],
            'validation_instances': ['lin105', 'att532', 'pcb1173'],
            'synthetic_instances': ['synthetic_1', 'synthetic_2'],
            'transfer_performance': 'robust'
        },
        'parameters': {
            'nearest_neighbor': {
                'start_node': 'deterministic_seed_1'
            },
            '2_opt': {
                'differential_move': True
            },
            'exchange': {
                'swap_size': 3
            }
        }
    }

