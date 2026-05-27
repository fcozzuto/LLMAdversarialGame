def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "description": "Deterministic, interpretable TSP heuristic scaffold with constraints and transfer-ready structure. Uses held-out TSPLIB-compatible framing and synthetic transfer placeholders.",
        "version": "1.0",
        "taxonomy": {
            "problem_type": "constrained_tsp",  # Explicitly notes node sequence with possible constraints
            "constraints": [
                "mandatory_visit_once_per_node",  # each node must be visited exactly once
                "precedence_constraints_maybe_supported",  # optional: some edges may enforce order
                "non_negative_costs",  # costs are non-negative
            ],
            "objective": "minimize_total_cost",
        },
        "data_interfaces": {
            "instances_source": "stable_tsplib_like_and_synthetic_transfer",
            "instances_format": {
                "tsplib_like": True,
                "node_coords": True,
                "edge_costs": True,
                "constraints_file": True  # optional file specifying constraints
            },
            "transfer_settings": {
                "enable_transfer": True,
                "transfer_targets": ["synthetic_holdout", "real_world_like"],
                "transfer_strategy": "basic_parameter_preservation",
            },
        },
        "heuristic_components": [
            {
                "name": "greedy_feasible_init",
                "purpose": "build initial feasible tour respecting basic constraints",
                "logic_hint": "start at fixed root, iteratively add nearest feasible node that maintains feasibility",
                "denotation": "initialization"
            },
            {
                "name": "local_improvement_step",
                "purpose": "improve tour locally with simple swaps",
                "operation": "2-opt_like_pairwise_swaps_with_constraint_check",
                "denotation": "improvement"
            },
            {
                "name": "constraint_checker",
                "purpose": "verify all problem constraints on a candidate tour",
                "logic_hint": "walk tour; ensure each node visited once; check precedence if provided",
                "denotation": "validation"
            },
            {
                "name": "transfer_prep",
                "purpose": "prepare features for transfer evaluation",
                "logic_hint": "extract tour length, constraint-violation flags, node order statistics",
                "denotation": "transfer_feature_extractor"
            }
        ],
        "evaluation_protocol": {
            "in_domain": {
                "note": "use a deterministic fixed seed-like order to ensure repeatability",
                "metrics": ["tour_cost", "feasibility_rate", "constraint_violation_count"]
            },
            "out_of_domain_transfer": {
                "note": "structure allows plugging in held-out TSPLIB-like instances and synthetic transfers",
                "metrics": ["transfer_cost_consistency", "transfer_feasibility", "score_stability"]
            },
            "repeatability": "deterministic_runs_only",
        },
        "heuristic_parameters": {
            "root_node": 0,
            "neighborhood": "nearest_feasible",
            "max_iterations": 1000,
            "tie_breaker": "lowest_index",
            "constraint_tolerance": "strict",
            "transfer_related": {
                "enable": True,
                "feature_set": ["tour_length", "num_nodes", "constraint_flags"],
            }
        },
        "robustness_considerations": {
            "handle_missing_constraints": "graceful_noop_and_continue",
            "fallback_mechanism": "return_best_feasible_or_empty_with_cost_infinity",
        },
        "serialization": {
            "format": "dict_structure_only",
            "version_tag": "1.0",
        },
        "notes": [
            "Deterministic scaffold suitable for extension with actual constraint data.",
            "Designed to be interpretable and not overly complex while remaining transfer-ready.",
            "No external imports; all behavior implied by described components and deterministic rules."
        ]
    }
