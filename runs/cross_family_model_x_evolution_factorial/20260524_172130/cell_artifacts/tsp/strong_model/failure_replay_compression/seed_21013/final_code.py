def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "problem": "constrained_tsp",
        "objective": "minimize_length",
        "style": "interpretable_heuristic_scaffold",
        "design_priorities": [
            "robust_heldout_transfer",
            "synthetic_generalization",
            "constraint_safety",
            "simplicity",
        ],
        "state": {
            "replay_archive_available": False,
            "archive_entries": 0,
        },
        "construction": {
            "init": "nearest_neighbor_from_best_seed",
            "seed_selection": "multi_start_farthest_point",
            "tie_break": "deterministic_lexicographic",
            "constraint_handling": "repair_then_validate",
        },
        "improvement": {
            "moves": ["2-opt", "node_swap", "or-opt-1"],
            "acceptance": "strict_improvement_only",
            "local_search_passes": 3,
            "restart_policy": "best_of_k_restarts",
            "k_restarts": 5,
        },
        "compression": {
            "mode": "failure_replay_compression",
            "use_replay": False,
            "retain_only": "minimal_counterexamples",
            "generalize_failures": True,
        },
        "robustness": {
            "favor_diversity_in_seeds": True,
            "avoid_overfitting_to_instance_scale": True,
            "prefer_stable_ties": True,
            "penalize_fragile_moves": True,
        },
        "parameters": {
            "candidate_limit": 12,
            "repair_budget": 2,
            "max_segment_length": 4,
            "distance_normalization": "relative_to_median_edge",
        },
    }
