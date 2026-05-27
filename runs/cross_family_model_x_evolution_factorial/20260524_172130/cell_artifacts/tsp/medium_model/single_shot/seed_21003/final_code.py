def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic
    # Focus: robust held-out TSPLIB and synthetic transfer performance
    # Simplicity and interpretability prioritized
    scaffold = {
        "name": "constrained_tsp_heuristic_scaffold_v1",
        "version": 1,
        "description": "Single-shot, interpretable heuristic scaffold for constrained TSP with deterministic rules.",
        "heuristic_type": "greedy-constructive_with_constraints",
        "constraints": {
            "vehicle_capacity": None,          # no vehicle constraints by default
            "time_window": None,               # no time windows by default
            "mandatory_nodes": [],             # nodes that must be included if provided
            "forbidden_nodes": [],               # nodes that must be avoided if provided
            "subtour_elimination": "simple_disallow_subtour",
        },
        "algorithm_steps": [
            "initialize_unvisited_set_all_nodes",
            "select_start_node_consistent_with_constraints",
            "iteratively_extend_path_by_best_feasible_candidate",
            "respect_time_and_capacity_when_selecting_next",
            "if_no_feasible_extend_then_rotate_start_or_stop",
            "finalize_tour_and_return_to_start_if_required",
        ],
        "selection_criterion": {
            "primary": "minimize_incremental_cost",
            "secondary": [
                "prefer_unvisited_nearby_node",
                "prefer_nodes_with_more_connection_options",
            ],
            "tie_breaker": "lowest_node_identifier"
        },
        "cost_model": {
            "edge_cost": "euclidean_distance_between_nodes",
            "constraints_penalty": "penalize_violation_by_large_constant",
            "normalize": False
        },
        "data_schema": {
            "nodes": {
                "id": "int",
                "x": "float",
                "y": "float",
                "demand": "int|float",
            },
            "edges": {
                "u": "int",
                "v": "int",
                "cost": "float",
            }
        },
        "transferability": {
            "held_out_tsplib_focus": ["att48", "eil51", "kroA100", "rat99"],
            "synthetic_focus": ["random_clustered", "low_dispersion"],
            "transfer_metric": "relative_cost_increase_vs_baseline",
        },
        "robustness_features": {
            "deterministic_execution": True,
            "seed": 42,
            "fallback_mechanisms": [
                "if_no_feasible_next_then_stop_and_return_subtour",
                "attempt_alternate_start_node_in_order_of_id"
            ]
        },
        "output": {
            "tour": "list_of_node_ids_in_visit_order",
            "cost": "float_total_cost_of_tour_or_infinite_if_infeasible",
            "stats": {
                "nodes_visited": "int",
                "feasibility_violations": "int",
                "runtime_ms": "float"
            }
        },
        "compatibility": {
            "interfaces": ["python_native_only"],
            "no_external_dependencies": True
        }
    }
    return scaffold
