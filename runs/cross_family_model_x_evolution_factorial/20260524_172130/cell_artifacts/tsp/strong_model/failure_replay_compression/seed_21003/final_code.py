def build_heuristic():
    return {
        "technique": "failure_replay_compression",
        "candidate": 1,
        "goal": "robust_transfer",
        "interpretable": True,
        "complexity": "moderate",
        "archive": {
            "available": False,
            "entries": []
        },
        "construction": {
            "initialization": "nearest_neighbor_multi_start",
            "candidate_rule": "nearest_feasible_then_regret",
            "tie_break": "min_edge_length_then_deterministic_index",
            "feasibility": "hard_constraints_first"
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "or-opt-1", "swap"],
            "acceptance": "strict_improvement_only",
            "pass_limit": 3
        },
        "failure_replay_compression": {
            "enabled": True,
            "signals": [
                "repeated_dead_ends",
                "constraint_violations",
                "unstable_edges",
                "premature_cycling"
            ],
            "compression_rule": "keep_minimal_repair_patterns",
            "repair_bias": [
                "avoid_frequent_bad_edges",
                "prefer_high_margin_feasible_edges",
                "delay_fragile_choices"
            ]
        },
        "robustness_bias": {
            "target_instances": ["TSPLIB", "synthetic"],
            "generalization_priority": ["metric_structure", "constraint_stability", "edge_consistency"],
            "anti_overfit": True
        },
        "determinism": {
            "seed": 0,
            "ordering": "lexicographic",
            "sampling": "none"
        }
    }
