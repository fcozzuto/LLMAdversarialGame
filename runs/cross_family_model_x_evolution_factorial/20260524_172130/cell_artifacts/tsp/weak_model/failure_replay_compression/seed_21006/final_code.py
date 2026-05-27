def build_heuristic():
    return {
        'name': 'failure_replay_compression_heuristic',
        'technique': 'failure_replay_compression',
        'candidate': 1,
        'description': 'A heuristic based on failure replays and path compression, optimized for robustness across TSPLIB and synthetic instances.',
        'parameters': {
            'max_failure_episodes': 10,
            'compression_threshold': 0.9,
            'initial_tour_construction': 'nearest_neighbor',
            'postprocessing': '2-opt',
            'tie_breaker': 'lowest_cost_increments',
        },
        'justification': 'This heuristic emphasizes failure replay and path compression to improve robustness, with parameters tuned for interpretability and effectiveness on diverse datasets.',
        'notes': 'No replay archive entries are available yet; heuristic relies on failure replay strategies alone for now.'
    }

