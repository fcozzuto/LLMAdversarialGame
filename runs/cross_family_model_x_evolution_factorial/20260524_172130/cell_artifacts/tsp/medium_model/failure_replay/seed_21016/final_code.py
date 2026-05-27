def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP-like problem
    # Focus: robustness, interpretability, and transfer performance across TSPLIB-like instances
    return {
        "name": "constrained_tsp_heuristic_scaffold_v1",
        "description": "A lightweight, interpretable heuristic scaffold for constrained TSP with deterministic behavior.",
        "version": 1,
        "assumptions": {
            "dist_metric": "euclidean",
            "release_constraint": "visit_nodes_within_budget",
            "seed": 42,
        },
        "problem_schema": {
            "nodes": {
                "type": "list",
                "content": {"type": "dict", "schema": {"id": "int", "x": "float", "y": "float", "demand": "int"}}
            },
            "depot": {"type": "int"},
            "vehicle_capacity": {"type": "int", "default": 100},
            "constraints": {
                "type": "dict",
                "schema": {
                    "max_route_length": "float|int",  # optional
                    "max_nodes_per_route": "int|None",
                    "precedence": "list[tuple[int,int]]|None"  # (u,v) means u before v
                }
            }
        },
        "heuristic_steps": [
            "preprocess_and_validate",
            "greedy_nearest_neighbor_with_capacity",
            "segment_routes_by_capacity",
            "insert_or_repair_with_local_swap",
            "feasibility_check_and_adjustment",
            "finalize_solution"
        ],
        "preprocess": {
            "validate_inputs": True,
            "normalize_coordinates": False,
            "compute_pairwise_distances": True  # deterministic on given coordinates
        },
        "core_components": {
            "distance_calc": {
                "method": "euclidean",
                "symmetry": True
            },
            "routing_logic": {
                "strategy": "greedy_nn_with_capacity",
                "tie_breaker": "lowest_id",
                "deterministic": True
            },
            "capacity_handling": {
                "strategy": "fit_as_much_as_possible_per_route",
                "fallback": "start_new_route_when_capacity_exhausted"
            }
        },
        "construction_tearsheet": {
            "snippet_1": {
                "name": "nearest_neighbor_with_capacity",
                "description": "Builds routes by repeatedly selecting the closest feasible node to the current end point without violating capacity.",
                "pseudocode": [
                    "start_at_depot",
                    "while unvisited_nodes remain",
                    "select candidate with min distance to current_node",
                    "if candidate fits in current_route_capacity and respects constraints:",
                    "    append to route",
                    "else:",
                    "    close current_route and start new one"
                ]
            }
        },
        "transfer_and_transfer_friendly": {
            "purpose": "support robustness on TSPLIB-like instances and synthetic transfers",
            "policy": [
                "avoid overfitting to a single instance",
                "prefer simple, transparent heuristics",
                "ensure deterministic outcomes for fixed input"
            ]
        },
        "reproducibility": {
            "random_seed": 42,
            "deterministic": True
        },
        "outputs": {
            "routes": [
                # Example structure of a route (to be filled by the implementation)
                # {"route_id": 1, "nodes": [depot_id, n1, n2, ..., depot_id], "load": total_demand}
            ],
            "objective": "minimize_total_distance_with_capacity_and_constraints",
            "stats": {
                "routes_used": "int",
                "total_distance": "float",
                "total_nodes_visited": "int",
                "feasibility": "bool"
            }
        }
    }
