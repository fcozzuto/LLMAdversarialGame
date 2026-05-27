def build_heuristic():
    return {
        "name": "interpretable_transfer_tsp_heuristic",
        "technique": "single_shot",
        "candidate": 1,
        "no_memory": True,
        "objective": "minimize_tour_length",
        "representation": "complete_graph_euclidean_or_metric",
        "components": {
            "construction": {
                "method": "nearest_neighbor",
                "start_rule": "multi_start_deterministic",
                "start_strategy": "farthest_point_seeds",
                "num_starts": 4,
                "tie_break": "lexicographic",
            },
            "improvement": {
                "method": "2_opt",
                "apply_until": "no_improvement",
                "candidate_pruning": "savings_threshold",
                "savings_threshold": 0.0,
            },
            "diversification": {
                "method": "none",
                "reason": "prefer stability and transferability",
            },
            "repair": {
                "method": "tour_relink",
                "enabled": True,
            },
        },
        "robustness_bias": {
            "metric_assumption": "low",
            "scale_invariance": True,
            "translation_invariance": True,
            "rotation_invariance": True,
        },
        "heldout_generalization": {
            "preference": "balanced",
            "avoid_overfitting": True,
            "favor_simple_rules": True,
        },
        "determinism": {
            "seed": 0,
            "stable_sorting": True,
        },
    }
