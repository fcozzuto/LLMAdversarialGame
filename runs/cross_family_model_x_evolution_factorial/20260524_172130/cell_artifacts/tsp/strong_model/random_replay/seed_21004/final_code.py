def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "description": "Deterministic replay-free scaffold for constrained TSP heuristics.",
        "objective": "robust_generalization",
        "interpretability": "high",
        "complexity": "low",
        "components": {
            "construction": {
                "strategy": "nearest_neighbor",
                "start_rule": "farthest_from_centroid",
                "tie_break": "lexicographic",
            },
            "improvement": {
                "strategy": "2-opt",
                "max_passes": 3,
                "acceptance": "strict_improvement",
            },
            "constraint_handling": {
                "mode": "penalize_and_repair",
                "repair_order": [
                    "remove_crossings",
                    "fix_infeasible_edges",
                    "local_2opt_repair",
                ],
            },
            "random_replay": {
                "enabled": True,
                "archive_entries": [],
                "replay_policy": "none_available",
            },
        },
        "parameters": {
            "candidate_pool_size": 1,
            "candidate_selection": "deterministic",
            "seed_behavior": "fixed",
        },
        "notes": [
            "No replay archive entries are available yet.",
            "Favor transfer to held-out TSPLIB and synthetic instances.",
        ],
    }
