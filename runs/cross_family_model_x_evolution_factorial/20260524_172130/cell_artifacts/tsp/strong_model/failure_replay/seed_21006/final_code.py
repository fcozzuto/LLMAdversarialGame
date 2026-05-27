def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "technique": "failure_replay",
        "deterministic": True,
        "goal": "robust_transfer_to_held_out_tsplib_and_synthetic_instances",
        "principles": [
            "prefer_simple_interpretable_moves",
            "repair_constraint_violations_first",
            "balance_greedy_progress_with_local_refinement",
            "avoid_overfitting_to_training_instance_patterns",
        ],
        "candidate_policy": {
            "construction": [
                "nearest_feasible_neighbor",
                "cheapest_insertion",
                "tie_break_by_lowest_degree_then_lowest_cost",
            ],
            "improvement": [
                "2-opt",
                "segment_relocation",
                "swap_if_feasible_and_better",
            ],
            "stopping": [
                "no_improvement_after_fixed_passes",
                "max_passes_small_constant",
            ],
        },
        "failure_replay": {
            "enabled": True,
            "archive_entries": [],
            "update_rule": "on_failure_store_instance_signature_and_bad_edges",
            "replay_priority": [
                "avoid_repeating_same_bad_prefix",
                "penalize_edges_seen_in_failed_tours",
                "prefer_alternative_feasible_connections",
            ],
        },
        "constraint_handling": {
            "mode": "hard_feasibility_first",
            "infeasible_penalty": 1000000,
            "repair_steps": [
                "remove_violating_edges",
                "reconnect_with_best_feasible_edges",
                "preserve_large_compatible_segments",
            ],
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "feasibility",
            "tertiary": "stability_under_small_perturbations",
        },
        "robustness": {
            "instance_normalization": "scale_invariant_costs",
            "diversification": "lightweight_tie_break_randomness_disabled",
            "transfer_bias": [
                "works_well_on_metric_instances",
                "handles_sparse_and_dense_graphs",
                "prefers_low_regret_insertion",
            ],
        },
        "complexity_budget": {
            "interpretability": "high",
            "time": "modest",
            "memory": "low",
        },
    }
