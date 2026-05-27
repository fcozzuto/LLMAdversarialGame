def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": "1.0",
        "description": "Deterministic single_shot constrained TSP heuristic scaffold with interpretable rules and balanced evaluation targets.",
        "technique": "single_shot",
        "design_choices": {
            "scope": "constrained_tsp",
            "determinism": True,
            "interpretability": True,
            "complexity_limit": "moderate",
        },
        "parameters": {
            "allow_subtour_penalty": True,
            "subtour_penalty_weight": 1.0,
            "length_constraint_weight": 0.0,
            "balance_objectives": False,
        },
        "representation": {
            "type": "permutation_path",
            "start_node": "0",
            "edge_cost_metric": "euclidean",
            "constraints": [
                "must_visit_each_node_once",
                "must_satisfy_capacity_or_time_window_if_provided",
            ],
        },
        "heuristic_steps": [
            "build_initial_order_by_nearest_neighbour_from_start",
            "apply_constraint_checker_to_remove_invalid_edges",
            "insert_missing_nodes_in_feasible_positions_in_order",
            "resolve_small_subtours_using_penalty_heuristic",
            "finalize_path_if_feasible_else_fail",
        ],
        "validation": {
            "feasibility_check": "all_nodes_present_and_each_visited_once",
            "conformity_check": "tour_forms_single_cycle_without_disconnected_segments",
            "penalty_application": "apply_subtour_penalty_when_subtours_exist",
            "runtime_considerations": "deterministic_runtime_bound",
        },
        "data_sources_considered": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "training_instances_excluded": True,
        },
        "robustness_considerations": {
            "edge_cost_sensitivity": "low",
            "constraint_violation_behavior": "penalize_then_try_fix",
        },
        "output_schema": {
            "tour": "list_of_node_indices_in_visit_order",
            "cost": "float_total_cost",
            "status": "string_one_of['feasible','infeasible']",
        },
        "notes": [
            "This scaffold prioritizes interpretability and deterministic behavior.",
            "It uses a simple nearest-neighbor start, then enforces constraints and resolves subtours with penalties if necessary.",
            "It is designed to work with constrained variants and to generalize beyond training instances by emphasizing robust constraint handling and transparency."
        ],
    }
