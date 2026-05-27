def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "goal": "robust_heldout_transfer",
        "interpretability": "medium",
        "complexity": "low",
        "deterministic": True,
        "no_replay_archive_entries": True,
        "construction": {
            "method": "nearest_insertion",
            "seed_rule": "min_pair_distance",
            "candidate_pool": "all",
            "tie_break": ["lower_edge_cost", "lower_node_id"],
            "initialization": {
                "start_pair": "closest_nodes",
                "orientation": "cheapest_attachment"
            }
        },
        "improvement": [
            {
                "name": "2-opt",
                "enabled": True,
                "scope": "global",
                "acceptance": "first_improvement",
                "stop": "no_improvement"
            },
            {
                "name": "node_relocation",
                "enabled": True,
                "scope": "single_node",
                "acceptance": "best_improvement",
                "stop": "no_improvement"
            }
        ],
        "constrained_handling": {
            "priority": "feasibility_first",
            "repair": "greedy_reinsert",
            "penalty_strategy": "static",
            "penalty_weight": 1.0
        },
        "robustness_bias": {
            "prefer_short_edges": True,
            "avoid_degenerate_ties": True,
            "use_metric_structure": True,
            "limit_aggressive_pruning": True
        },
        "compression": {
            "strategy": "keep_only_successful_patterns",
            "patterns": [
                "nearest_insertion",
                "2-opt",
                "node_relocation",
                "feasibility_first"
            ]
        }
    }
