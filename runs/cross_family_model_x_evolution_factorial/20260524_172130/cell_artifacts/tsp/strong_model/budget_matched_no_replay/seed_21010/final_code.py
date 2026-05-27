def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "candidate": 2,
        "deterministic": True,
        "imports": False,
        "memory_policy": {
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
            "prior_candidates": 0,
        },
        "objective": {
            "primary": "tour_length",
            "secondary": "stability",
            "target": "robust_transfer",
        },
        "construction": {
            "method": "nearest_neighbor_seeded",
            "seeds": ["nearest", "farthest", "centroid"],
            "tie_break": "lexicographic",
            "candidate_limit": 3,
        },
        "improvement": {
            "local_search": ["2-opt", "segment_reversal"],
            "budget_policy": "matched_to_instance_size",
            "restart_count": 0,
            "acceptance": "strict_improvement",
        },
        "budget_matched_no_replay": {
            "match_on": ["n", "edge_density_proxy"],
            "budget_curve": "sqrt_scaled",
            "reuse_previous_runs": False,
        },
        "robustness": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "avoid_overfitting": True,
            "prefer_interpretable_rules": True,
        },
        "parameters": {
            "alpha": 0.5,
            "beta": 1.0,
            "gamma": 0.0,
            "max_moves_per_round": 1000,
            "max_rounds": 5,
        },
    }
