def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "replay_archive": [],
        "fallback": {
            "construction": "nearest_insertion_regret",
            "local_search": ["2-opt"],
            "acceptance": "improving_only",
        },
        "objective": "tsp_tour_length",
        "design_priorities": [
            "robust_generalization",
            "interpretable",
            "low_complexity",
            "deterministic",
        ],
        "held_out_transfer_bias": {
            "prefer": ["insertion_regret", "2-opt", "edge_crossing_removal"],
            "avoid": ["instance_specific_tuning", "deep_search", "randomized_restarts"],
        },
        "parameters": {
            "construction_seed": 0,
            "max_local_search_passes": 3,
            "candidate_list_size": 8,
            "use_replay_if_available": True,
        },
        "notes": "No replay archive entries are available; use the deterministic fallback scaffold.",
    }
