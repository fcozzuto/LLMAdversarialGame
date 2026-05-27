def build_heuristic():
    # Deterministic, interpretable TSP heuristic scaffold with constrained rules.
    # This scaffold emphasizes robustness across held-out TSPLIB-like instances
    # and synthetic transfers, while remaining simple and interpretable.
    heuristic = {
        "name": "single_shot_constrained_tsp_heuristic",
        "version": 1,
        "description": "Interpretable single-shot heuristic for constrained TSP with a deterministic plan.",
        "assumptions": {
            "node_coords_type": "euclidean",
            "distance_metric": "euclidean",
            "constraints": {
                "must_visit_all_nodes": True,
                "budget_or_capacity": None,
                "time_window": None,
            },
        },
        "strategy": {
            "type": "greedy_bbox_spanning_path",
            "details": {
                "initial_seed": 0,
                "neighbor_ordering": "by_angle_then_distance",
                "tie_breaker": "lowest_index",
                "acceptance_condition": "prefix_is_feasible_and_progressive",
            },
        },
        "scoring_function": {
            "primary_objective": "minimize_path_length",
            "secondary_objectives": [
                "maximize_balance_across_clusters",
                "increase_sparsity_to_improve_transfer",
            ],
            "penalties": {
                "revisit_penalty": 1,
                "over_budget_penalty": 1e6,
            },
        },
        "constraints_handling": {
            "enforce_all_nodes": True,
            "pruning": {
                "enabled": False,
                "threshold": None,
            },
            "forbidden_subpaths": [],
        },
        "transferability_considerations": {
            "holdout_robustness": True,
            "synthetic_transfer_support": True,
            "cross_instance_sensitivity": "moderate",
        },
        "robustness_and_reproducibility": {
            "random_seed": 0,  # deterministic
            "repeatable_runs": True,
            "logging": {
                "level": "warning",
                "structure": ["step", "node", "action", "cost"],
                "destination": "stdout",
            },
        },
        "output_format": {
            "path_order": "sequence_of_node_indices",
            "summary": ["total_distance", "visited_count", "feasibility"],
            "diagnostics": {
                "last_step_cost": True,
                "prefix_feasibility": True,
            },
        },
        "scope": {
            "applicable_instances": [
                "tsplib-like held-out",
                "synthetic_transferable",
                "small_to_medium_scale",
                "sparse_or_clustered",
            ],
            "limits": {
                "n_nodes_max": 200,
                "compute_budget_seconds": 5
            },
        },
        "notes": "Deterministic single-shot heuristic scaffold intended for constrained TSP. Keeps complexity moderate and interpretation transparent."
    }
    return heuristic
