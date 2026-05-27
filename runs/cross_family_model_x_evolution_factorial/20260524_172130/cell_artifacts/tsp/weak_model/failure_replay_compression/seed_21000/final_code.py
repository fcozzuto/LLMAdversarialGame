def build_heuristic():
    return {
        'name': 'failure_replay_compression_candidate_1',
        'technique': 'failure_replay_compression',
        'parameters': {
            'replay_archive': None,  # No replays at initialization
            'compression_threshold': 0.1,
            'max_replay_entries': 50,
            'heuristic_steps': [
                'nearest_neighbor',
                '2_opt_local_search',
                'failure_replay_rescue'
            ],
            'evaluation_metrics': [
                'tour_length_stability',
                'performance_on_tsp_libs',
                'synthetic_transfer_efficiency'
            ],
            'fallback_strategy': 'greedy_insertion',
            'robustness_checks': True
        }
    }

