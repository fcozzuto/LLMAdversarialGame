def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold emphasizes robustness across held-out TSPLIB-like instances
    # and synthetic transfers while remaining interpretable and not overly complex.
    return {
        "name": "deterministic_constrained_tsp_scaffold_v1",
        "description": (
            "Robust, interpretable deterministic scaffold for constrained TSP heuristics. "
            "Uses a simple sequential insertion with feasibility checks and a basic repair step."
        ),
        "version": "1.0.0",
        "algorithm": {
            "type": "insertion_with_feasibility",
            "steps": [
                "initialize_tour_with_fixed_start_node",
                "sequentially_insert_nodes_in_order_of_fixed_priority",
                "enforce_constraints_during_insertion",
                "if_constraint_violation_then_disable_problematic_move",
                "after_insertion_apply_local_optimization_covering_eg_edgestep"
            ],
            "priority_criteria": [
                "minimize_additional_distance",
                "respect_disjunctions_and_capacity_constraints",
                "prefer_edges_with_lower_cost",
            ],
            "feasibility_checks": [
                "capacity_constraint_check",
                "time_window_constraint_check",
                "mandatory_edge_constraints",
                "forbidden_edges_and_nodes"
            ],
            "repair_mechanism": [
                "identify_infeasible_segments",
                "perform_local_repair_by_swapping_neighbors",
                "fallback_to_subset_removal_and_reinsertion"
            ],
        },
        "data_handling": {
            "instance_sources": [
                "tsplib_like_robust_holdout",
                "synthetic_transfer_sets",
            ],
            "seed_behavior": "deterministic_constant_seed",
            "scaling": {
                "normalize_distances": True,
                "treat_unit_costs_as_int": False
            },
            "feature_encoding": {
                "node_features": ["degree", "positional_order", "demand_or_capacity"],
                "edge_features": ["distance", "is_forbidden", "is_mandatory"]
            }
        },
        "tuning_and_transfer": {
            "transfer_strategy": "rule_based_scaling_and_prioritization",
            "robustness_checks": [
                "cross_instance_consistency",
                "edge_cost_sensitivity_analysis",
                "constraint_violation_rate_monitoring"
            ],
            "fallback_modes": [
                "increase_insertion_buffer",
                "prefer_shorter_edges_in_early_phase"
            ]
        },
        "interpretability": {
            "explanation_hooks": [
                "trace_insertion_sequence",
                "log_constraints_applied",
                "record_feasibility_decisions"
            ],
            "reporting": {
                "tour_cost",
                "constraint_violations_count",
                "infeasible_segments",
                "dominant_edge_choices"
            }
        },
        "determinism_artifacts": {
            "random_seed": 42,
            "pseudo_random_sequence": "deterministic_allocation",
            "reproducibility_notes": "outputs and decisions identical across runs given same seed and data order"
        }
    }
