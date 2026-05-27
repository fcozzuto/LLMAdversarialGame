def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "archive": [],
        "policy": {
            "construction": "nearest_insertion",
            "seed_strategy": "farthest_pair",
            "tie_break": "lexicographic",
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "swap"],
            "pass_limit": 3,
            "improve_only": True,
        },
        "replay": {
            "enabled": False,
            "mode": "none",
            "weighting": "uniform",
        },
        "robustness": {
            "instance_transfer": "high",
            "synthetic_transfer": "high",
            "held_out_tsplib_focus": True,
        },
        "interpretability": {
            "complexity": "low",
            "components": ["construction", "local_search"],
        },
    }
