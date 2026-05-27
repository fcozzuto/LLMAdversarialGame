def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP with budget_matched_no_replay technique.
    # This scaffold is interpretable and avoids replay/failure/compression components.
    scaffold = {
        "name": "budget_matched_no_replay_constrained_tsp",
        "version": 1,
        "description": "Deterministic constrained TSP heuristic scaffold using budget-matched approach with no replay memory.",
        "technique": "budget_matched_no_replay",
        "components": {
            "problem_representation": {
                "type": "graph",
                "representation": "sparse_adjacency",
                "node_features": ["x_coord", "y_coord", "demand" if False else None],
                "edge_features": ["distance", "is_forbidden"],
                "constraints": ["budget_constraint", "city_capacity_constraints", "time_window_constraints"]  # placeholders for extensibility
            },
            "budget_management": {
                "budget_type": "global",
                "budget_unit": "distance",
                "initial_budget": "adaptive_from_problem_scale",
                "budget_adjustment": "proportional_step",
                "guardrails": {
                    "min_budget": 0.0,
                    "max_budget": None
                }
            },
            "construction_strategy": {
                "method": "greedy_feasible_extension",
                "selection_criteria": [
                    "feasibility_by_constraints",
                    "shortest_distance_to_current",
                    "budget_residual"
                ],
                "initial_tour": "single_start_node",
                "extension_rule": "append_best_feasible_node",
                "stopping_condition": "no_feasible_extension or budget_exhausted"
            },
            "feasibility_checks": {
                "types": ["capacity", "time_window", "forbidden_edges"],
                "order": ["quick_pruning", "full_feasibility_check"]
            },
            "transfer_performance_focus": {
                "robustness": True,
                "generalization": {
                    "targets": ["TSPLIB_symmetric", "synthetic_transfer"],
                    "sampling": "deterministic_split"
                },
                "evaluation_metrics": ["tour_cost", "feasibility_rate", "budget_utilization"]
            },
            "output": {
                "tour": "ordered_list_of_node_ids",
                "cost": "computed_tour_cost",
                "status": ["feasible", "infeasible"],
                "stats": {
                    "nodes_visited": "count",
                    "extensions_attempted": "count",
                    "budget_used": "sum_distance"
                }
            }
        },
        "assumptions": [
            "deterministic_node_ordering",
            "no_random_sampling",
            "no_replay_memory",
            "no_failure_memory",
            "no compression"
        ],
        "parameters": {
            "tuning": {
                "greedy_weight": 1.0,
                "distance_weight": 1.0,
                "constraint_penalty": 0.0
            },
            "limits": {
                "max_nodes": 1000,
                "max_extensions": 1000
            }
        }
    }
    return scaffold
