def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "objective": "constrained_tsp",
        "design_principles": [
            "deterministic",
            "interpretable",
            "robust_transfer",
            "simple_local_improvement",
        ],
        "scaffold": {
            "construction": {
                "method": "nearest_feasible_insertion",
                "tie_break": ["minimum_added_cost", "minimum_lookahead_risk", "lexicographic_index"],
                "start_rule": "best_singleton_or_best_edge_seed",
            },
            "repair": {
                "method": "constraint_aware_2opt",
                "accept_only_if": "feasible_and_cost_decreases",
                "max_passes": 3,
            },
            "fallbacks": [
                "greedy_edge_addition",
                "infeasible_penalty_avoidance",
                "randomness_disabled",
            ],
            "feature_weights": {
                "distance": 1.0,
                "constraint_risk": 2.0,
                "future_insertion_slack": 0.5,
            },
        },
        "heldout_generalization_bias": {
            "prefer_sparse_rules": True,
            "avoid_instance_specific_tuning": True,
            "normalize_distances": True,
        },
    }
