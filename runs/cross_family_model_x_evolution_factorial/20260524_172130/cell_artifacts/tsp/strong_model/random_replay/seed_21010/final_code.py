def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "description": "Deterministic random-replay scaffold with restrained diversification and robust local improvement.",
        "objective": "tsp",
        "style": "interpretable",
        "complexity": "low",
        "transfer_bias": {
            "held_out_tsplib": 0.75,
            "synthetic": 0.25,
            "notes": "Prefer broadly stable moves over instance-specific tuning."
        },
        "construction": {
            "method": "nearest_neighbor_seeded",
            "seeds": ["farthest_pair", "min_x", "min_y"],
            "tie_break": "lexicographic",
            "deterministic": True
        },
        "replay": {
            "enabled": True,
            "archive_policy": "none_available",
            "fallback": "multi_start_deterministic",
            "candidate_order": ["construction", "2-opt", "or-opt-1", "swap"]
        },
        "local_search": {
            "primary": "2-opt",
            "secondary": "or-opt-1",
            "tertiary": "swap",
            "acceptance": "strict_improvement",
            "first_improvement": True,
            "move_budget": 2000
        },
        "perturbation": {
            "enabled": True,
            "method": "segment_shuffle",
            "intensity": 0.08,
            "restarts": 4
        },
        "scoring": {
            "edge_length_penalty": 1.0,
            "crossing_penalty": 1.5,
            "stability_bonus": 0.1
        },
        "stopping": {
            "no_improvement_rounds": 3,
            "max_rounds": 8
        }
    }
