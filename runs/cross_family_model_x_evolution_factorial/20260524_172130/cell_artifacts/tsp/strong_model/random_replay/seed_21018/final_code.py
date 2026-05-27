def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "strategy": {
            "type": "construction_plus_local_search",
            "construction": "nearest_insertion",
            "local_search": ["2_opt", "swap"],
            "repair": "feasibility_preserving",
            "restart_policy": "deterministic_multistart",
        },
        "priorities": {
            "robust_transfer": True,
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "interpretability": True,
            "complexity": "low",
        },
        "parameters": {
            "candidate_list_size": 8,
            "restart_count": 3,
            "two_opt_passes": 2,
            "swap_passes": 1,
            "seed_mode": "fixed",
        },
        "notes": [
            "No replay archive entries available; use generic robust defaults.",
            "Favor stable improvements over aggressive specialization.",
        ],
    }
