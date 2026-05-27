def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate": 1,
        "archive": [],
        "policy": {
            "type": "heldout_robust",
            "objective": "tour_length",
            "selection": "best_improvement",
            "tie_break": "first",
        },
        "operators": [
            {
                "name": "2-opt",
                "scope": "all_edges",
                "accept": "improves_tour",
            },
            {
                "name": "swap",
                "scope": "city_pairs",
                "accept": "improves_tour",
            },
            {
                "name": "insertion",
                "scope": "single_city",
                "accept": "improves_tour",
            },
        ],
        "move_order": [
            "2-opt",
            "swap",
            "insertion",
        ],
        "replay": {
            "enabled": True,
            "source": "archive",
            "fallback": "greedy_local_search",
            "max_replays": 0,
        },
        "construction": {
            "type": "nearest_neighbor",
            "start": "farthest_from_centroid",
        },
        "local_search": {
            "enabled": True,
            "passes": 2,
            "neighborhood": ["2-opt", "swap", "insertion"],
        },
        "robustness": {
            "favor_short_edges": True,
            "avoid_overfitting": True,
            "transfer_bias": "moderate",
        },
    }
