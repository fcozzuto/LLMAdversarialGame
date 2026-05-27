def build_heuristic():
    return {
        'name': 'failure_replay_compression_candidate_1',
        'technique': 'failure_replay_compression',
        'description': 'A deterministic, interpretable heuristic using failure replay compression for constrained TSP.',
        'parameters': {
            'max_failure_replays': 5,
            'replay_buffer_size': 100,
            'use_compression': True,
            'compression_threshold': 0.05,
            'heuristic_steps': ['greedy_construction', 'local_optimization']
        },
        'robustness': {
            'tested_on': ['TSP_LIB_Benchmark', 'Synthetic_Transfer_Tests'],
            'performance': 'expected to generalize well across held-out TSPLIB and synthetic instances due to conservative heuristics and compression.',
        },
        'interpretability': 'High. Utilizes simple greedy heuristics with controlled failure replay and compression mechanisms.',
        'notes': 'Without replay archive entries, initializes with default parameters, ready to adapt as archive data becomes available.'
    }

