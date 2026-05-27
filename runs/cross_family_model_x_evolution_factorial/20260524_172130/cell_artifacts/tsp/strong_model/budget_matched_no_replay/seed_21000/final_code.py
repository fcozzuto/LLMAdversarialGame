def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "strategy": {
            "construction": "nearest_neighbor",
            "seed_rule": "farthest_from_centroid",
            "local_search": ["2-opt", "or-opt-1"],
            "acceptance": "strict_improvement_only",
            "restart": False,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "budgeting": {
            "match_budget_to_instance_scale": True,
            "budget_signal": "n_cities",
            "budget_formula": "max(1, floor(sqrt(n_cities)))",
            "move_cap_per_phase": {
                "2-opt": "2*n_cities",
                "or-opt-1": "n_cities",
            },
        },
        "candidate_policy": {
            "neighbor_filter": "k_nearest",
            "k_rule": "min(20, max(5, floor(log2(n_cities)) + 3))",
            "tie_break": "lexicographic_deterministic",
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "edge_gain",
            "penalty_terms": [],
        },
        "robustness": {
            "instance_transfer": "prefer_scale_free_local_improvement",
            "heldout_generalization": "avoid instance-specific tuning",
            "synthetic_transfer": "use geometry-agnostic improvement rules",
        },
        "interpretability": {
            "description": "Deterministic nearest-neighbor construction followed by bounded 2-opt and 1-node Or-opt refinement under a matched move budget.",
            "complexity": "moderate",
        },
    }
