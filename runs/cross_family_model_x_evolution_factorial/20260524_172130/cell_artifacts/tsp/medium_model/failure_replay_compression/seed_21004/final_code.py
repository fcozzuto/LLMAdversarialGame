def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with interpretability and robustness across TSPLIB and synthetic transfer instances.",
        "approach": "two-phase: feasibility-first pruning, deterministic constructive tour with local refinements; failure_replay_compression placeholder for future replay handling.",
        "domains": ["constrained_tsp", "tsplib", "synthetic_transfer"],
        "constraints": {
            "must_visit_all_nodes": True,
            "mandatory_nodes": None,  # can be updated to a fixed set or left as None for full problem
            "time_budget_ms": 2000,      # deterministic upper bound for construct phase
            "memory_budget_mb": 64,      # deterministic bound
            "edge_costs_nonnegative": True,
            "deterministic_seed": 42,
            "symmetry_consideration": "assume symmetric tour costs by default",
            "capacity_constraints": "explicit per-node or per-subset limits if provided in instance",
        },
        "scaffold": {
            "constructive_phase": {
                "strategy": "greedy_component_build",
                "start_node_selection": "fixed_seed_seeded",
                "neighbor_order": "sorted_by_incremental_cost",
                "tie_breaker": "node_id",
                "feasibility_checks": [
                    "respect_dummy_capacity",
                    "respect_subtour_elimination",
                    "respect_ordering_constraints"
                ],
                "result_representation": "tour_list_of_node_ids",
            },
            "local_refinement_phase": {
                "swap_moves": ["2-opt", "3-opt"],
                "exchange_moves": ["edge_exchange"],
                "acceptance_criterion": "improvement_only",
                "max_iterations": 100,
            },
            "failure_handling": {
                "failure_replay_compression": {
                    "enabled": True,
                    "archive_entries": 0,
                    "policy": "no_replays_available_yet",
                    "fallback": "return_feasible_approx_with_pruning_bound",
                }
            }
        },
        "robustness_heuristics": {
            "transfer_friendly": True,
            "tsplib_robustness": True,
            "default_instance_scaling": "normalize_costs_to_unit_range",
            "deterministic_behavior": True
        },
        "output": {
            "tour": "list_of_node_ids_in_order",
            "lower_bound_proxy": "LKH_like_bound_placeholder",
            "statistics": {
                "construction_time_ms": "deterministic_runtime",
                "refinement_time_ms": "deterministic_runtime",
                "tour_cost": "computed_cost_on_instance",
            },
        },
        "notes": [
            "This scaffold is intentionally interpretable and avoids heavy heuristics.",
            "No external libraries; all behavior is deterministic via fixed seeds and simple operations.",
            "Pleasantly compatible with TSPLIB-like constraints and synthetic transfer scenarios."
        ],
    }
