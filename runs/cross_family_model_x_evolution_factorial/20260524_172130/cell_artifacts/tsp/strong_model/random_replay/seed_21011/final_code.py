def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "notes": [
            "No replay archive entries available yet.",
            "Use a simple, robust scaffold that can transfer across TSPLIB and synthetic instances.",
        ],
        "representation": {
            "type": "tour",
            "closed": True,
            "city_indexing": "0..n-1",
        },
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "multi_start_deterministic",
            "start_candidates": [0, 1, 2, 3],
            "tie_break": "lowest_index",
        },
        "improvement": {
            "method": "2-opt",
            "apply": True,
            "max_passes": 3,
            "accept_rule": "first_improvement",
            "candidate_pruning": "distance_gain",
        },
        "random_replay": {
            "enabled": True,
            "policy": "sample_and_replay_best",
            "sample_count": 8,
            "temperature": 0.0,
            "deterministic_seed": 0,
        },
        "robustness": {
            "objective": "tour_length",
            "regularization": "none",
            "transfer_bias": "favor_geometry_over_instance_specific_patterns",
        },
    }
