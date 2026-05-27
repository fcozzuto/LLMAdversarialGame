def build_heuristic():
    return {
        "heuristic_name": "failure_replay_scaffold",
        "technique": "failure_replay",
        "candidate": 1,
        "objective": "robust_transfer",
        "target_problem": "tsp",
        "representation": "tour_permutation",
        "scaffold_style": "interpretable_local_search",
        "replay_archive": [],
        "selection_policy": {
            "type": "best_improvement_then_first_failure_replay",
            "tie_break": "deterministic",
            "candidate_order": [
                "2-opt",
                "3-opt",
                "node_shift",
                "swap"
            ],
        },
        "operators": [
            {
                "name": "2-opt",
                "enabled": True,
                "scope": "global",
                "acceptance": "best_improvement",
                "priority": 1,
            },
            {
                "name": "node_shift",
                "enabled": True,
                "scope": "local",
                "acceptance": "improving_only",
                "priority": 2,
            },
            {
                "name": "swap",
                "enabled": True,
                "scope": "local",
                "acceptance": "improving_only",
                "priority": 3,
            },
            {
                "name": "3-opt",
                "enabled": True,
                "scope": "selective",
                "acceptance": "improving_only",
                "priority": 4,
            },
        ],
        "parameters": {
            "max_restarts": 2,
            "max_passes_per_restart": 8,
            "max_failures_before_replay": 3,
            "replay_budget": 0,
            "candidate_sample_size": 1,
            "improvement_threshold": 0.0,
            "use_deterministic_seed_order": True,
        },
        "heldout_transfer_bias": {
            "prefer_small_number_of_simple_moves": True,
            "avoid_instance_specific_tuning": True,
            "prefer_metric_agnostic_moves": True,
            "robust_to_euclidean": True,
            "robust_to_non_euclidean": True,
        },
        "interpretability": {
            "primary_reasoning": "local_edge_crossing_removal",
            "secondary_reasoning": "small_neighborhood_refinement",
            "complexity": "low",
        },
        "fallback": {
            "on_no_improvement": "rotate_restart_anchor",
            "on_replay_empty": "continue_standard_search",
        },
    }
