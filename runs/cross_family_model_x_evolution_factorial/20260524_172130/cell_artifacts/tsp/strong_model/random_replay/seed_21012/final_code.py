def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "deterministic": True,
        "archive_available": False,
        "core": {
            "type": "replay_seeded_construction",
            "description": "Use a simple reproducible construction with local improvement fallback.",
            "construction": {
                "method": "nearest_neighbor",
                "start_rule": "minimum_edge_risk",
                "tie_break": "lexicographic",
            },
            "improvement": {
                "method": "2-opt",
                "passes": 2,
                "accept_equal": False,
            },
        },
        "robustness": {
            "heldout_focus": True,
            "tsplib_transfer": True,
            "synthetic_transfer": True,
            "bias": "low_complexity_interpretable",
        },
        "replay": {
            "enabled": False,
            "strategy": "none",
            "archive_entries": 0,
        },
        "parameters": {
            "candidate_pool": 8,
            "seed_policy": "fixed",
            "symmetric_only": False,
        },
        "notes": [
            "Deterministic scaffold with no archive replay available.",
            "Designed to generalize via simple construction plus limited local search.",
        ],
    }
