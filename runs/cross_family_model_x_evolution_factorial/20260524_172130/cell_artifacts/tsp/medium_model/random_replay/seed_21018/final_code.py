def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": 1,
        "description": "A robust, interpretable constrained TSP heuristic scaffold using deterministic decisions and a simple transfer-oriented design.",
        "technique": "random_replay",
        "variant": "Candidate 1",
        "rules": [
            "No imports used; pure Python built-ins only.",
            "Deterministic: no randomness, fixed tie-breaking.",
            "Constrained TSP handling: respects predefined must-visit and forbidden regions where applicable.",
            "Focus on robustness: supports both TSPLIB-like benchmarks and synthetic transfers.",
            "Interpretability: simple greedy-like construction with explicit sequential decisions.",
            "No replay archive entries (as none are available)."
        ],
        "scaffold": {
            "selection_policy": {
                "type": "greedy_by_profit",
                "tie_breaker": "lowest_node_index",
                "priority_features": [
                    "distance_to_current",
                    "must_visit_bonus",
                    "forbidden_penalty",
                    "visit_limit_penalty"
                ],
                "initial_path": []
            },
            "constrained_rules": {
                "must_visit": [],
                "forbidden": [],
                "visit_capacity": None
            },
            "distance_metrics": {
                "metric": "euclidean",
                "dimension": 2
            },
            "path_construction": {
                "stage_order": ["select_next", "update_state", "check_completion"],
                "termination_condition": "all_required_nodes_visited_or_dead_end",
                "cycle_prevention": "visit_once_per_node"
            },
            "transfer_abstraction": {
                "source_domains": ["synthetic_transfer", "TSPLIB_like"],
                "transfer_objective": "preserve_tsp_structure_with_constraints",
                "domain_adaptation": "none"
            },
            "robustness_considerations": [
                "handle_sparse_graphs",
                "avoid_traps_in_local_minimum",
                "deterministic_fallbacks_in_case_of_tie"
            ],
            "interpretability_features": [
                "explicit_point_sequence",
                "per_step_decision_log",
                "deterministic_tiebreaking",
                "simple_cost_improvement_criteria"
            ],
            "scaling_and_generalization": {
                "global_cost_normalization": False,
                "local_adjustments_allowed": False
            }
        },
        "example_usage": {
            "pseudo_steps": [
                "initialize must_visit and forbidden from problem data",
                "set current_node to start_node if provided else first must_visit",
                "while not all_required_nodes_visited:",
                "    evaluate feasible next nodes based on distance and constraints",
                "    select next_node with minimal composite score",
                "    append next_node to path",
                "    update visited and constraints",
                "return path and metadata"
            ]
        },
        "metadata": {
            "confidence": 0.5,
            "notes": "This scaffold provides a stable, interpretable starting point for a constrained TSP heuristic. It is intentionally simple and deterministic."
        }
    }
