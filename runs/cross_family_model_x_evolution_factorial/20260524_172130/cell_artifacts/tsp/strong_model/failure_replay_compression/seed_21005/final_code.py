def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate_id": 1,
        "objective": "minimize_tour_length",
        "design_principles": [
            "interpretable",
            "robust_to_held_out_instances",
            "simple_transfer_friendly",
            "deterministic"
        ],
        "init": {
            "method": "nearest_insertion",
            "tie_break": "lexicographic",
            "start_node_policy": "best_of_farthest_and_lowest_index",
            "seed_policy": "none"
        },
        "local_search": {
            "primary": "2-opt",
            "secondary": "1-opt_relocation",
            "acceptance": "strict_improvement",
            "max_passes": 50,
            "no_improvement_stop": 5,
            "edge_gain_threshold": 0.0
        },
        "candidate_restriction": {
            "enabled": True,
            "strategy": "k_nearest_neighbors",
            "k": 20,
            "symmetric": True,
            "fallback_full_scan": True
        },
        "compression": {
            "enabled": True,
            "representation": "failure_signature_to_rule",
            "store_only_distinct_failures": True,
            "max_rules": 32,
            "rule_priority": [
                "prevent_repeated_crossing_patterns",
                "preserve_short_edges",
                "avoid_long_detours_after_insertion"
            ]
        },
        "replay": {
            "enabled": False,
            "archive_entries": [],
            "update_policy": "none"
        },
        "perturbation": {
            "enabled": False,
            "method": "double_bridge",
            "strength": 0
        },
        "termination": {
            "time_budget_policy": "instance_size_scaled",
            "iteration_cap_policy": "instance_size_scaled",
            "hard_stop_on_no_gain": True
        },
        "output": {
            "return_format": "tour_indices",
            "validate_tour": True,
            "repair_if_needed": True
        }
    }
