def build_heuristic():
    return {
        "technique": "random_replay",
        "candidate_id": 1,
        "replay_archive": [],
        "policy": {
            "construction": "nearest_neighbor",
            "seed_strategy": "deterministic",
            "multi_start": True,
            "start_nodes": ["min_x", "max_x", "min_y", "max_y"],
        },
        "local_search": {
            "enabled": True,
            "operators": ["2-opt", "swap"],
            "first_improvement": True,
            "max_passes": 3,
        },
        "scoring": {
            "objective": "tour_length",
            "tie_break": "lexicographic",
        },
        "robustness": {
            "favor_geometry": True,
            "scale_invariant": True,
            "heldout_generalization": "prioritize",
        },
        "complexity": "low",
        "interpretability": "high",
    }
