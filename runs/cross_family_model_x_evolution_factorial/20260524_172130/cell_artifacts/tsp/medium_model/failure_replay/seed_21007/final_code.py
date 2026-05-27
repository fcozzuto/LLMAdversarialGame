def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold favors robustness across held-out TSPLIB and synthetic transfers,
    # while remaining interpretable and not overly complex.
    scaffold = {
        "name": "constrained_tsp_heuristic_v1",
        "version": "1.0",
        "description": "Deterministic, interpretable heuristic scaffold for constrained TSP with failure_replay style planning.",
        "parameters": {
            "seed": 42,
            "initial_constr": "price_threshold_100",  # placeholder constraint name
            "city_ordering": "nearest_neighbor_then_repair",
            "repair_strategy": "swap_and_fix_subtour",
            "timeout_seconds": 120,
            "noise": 0.0,  # deterministic
            "maximize_robustness": True
        },
        "constraints": {
            "must_visit_all": True,
            "subtour_elimination": "iterative",
            "capacity_like_limit": None,  # for generalized constraints; None means no extra capacity constraint
            "time_window": None
        },
        "steps": [
            {
                "step": "initialize",
                "action": "prepare_candidate_pool",
                "details": {
                    "pool_source": ["TSPLIB_holdout", "synthetic_transfer"],
                    "selection_criteria": ["distance_minimization", "feasibility_check"],
                    "seed_use": True
                }
            },
            {
                "step": "order_building",
                "action": "build_initial_path",
                "details": {
                    "method": "nearest_neighbor",
                    "start_city": "city_0",
                    "ties_resolved_by": "index_order"
                }
            },
            {
                "step": "constraint_check",
                "action": "verify_constraints",
                "details": {
                    "constraints_checked": ["must_visit_all", "subtour_elimination"],
                    "on_violation": "mark_and_skip_suboptimal_fragments"
                }
            },
            {
                "step": "repair",
                "action": "repair_subtours",
                "details": {
                    "strategy": "swap_and_fix_subtour",
                    "max_iterations": 50
                }
            },
            {
                "step": "local_improvement",
                "action": "2opt_like_improvement",
                "details": {
                    "iterations": 100,
                    "allowed_moves": ["edge_swap", "redistribute_nodes"]
                }
            },
            {
                "step": "selection",
                "action": "select_best_feasible_heuristic",
                "details": {
                    "score_function": "path_length",
                    "penalties": ["constraint_violation_penalty_1", "subtour_penalty"]
                }
            },
            {
                "step": "finalize",
                "action": "prepare_output",
                "details": {
                    "output_format": "dictionary_with_path_and_metadata",
                    "include": ["path", "length", "feasibility", "robustness_estimate"]
                }
            }
        ],
        "output_structure": {
            "path": ["city_0", "city_1", "...", "city_n-1"],
            "length": "computed_total_distance",
            "feasibility": True,
            "robustness_estimate": "high_expected_transfer_robustness"
        },
        "robustness_profile": {
            "heldout_robustness": {
                "tsplib_holdout_weight": 0.6,
                "synthetic_transfer_weight": 0.4
            },
            "transfer_performance_horizon": "medium",
            "interpretability": "high"
        },
        "notes": [
            "Deterministic configuration; no randomness.",
            "Designed to be transparent and easily adjustable for future experiments.",
            "Failure_replay style: if a step fails, scaffold records the failure type but does not randomize."
        ]
    }
    return scaffold
